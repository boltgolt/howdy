#include <cerrno>
#include <csignal>
#include <cstdlib>
#include <ostream>

#include <glob.h>
#include <libintl.h>
#include <pthread.h>
#include <spawn.h>
#include <stdexcept>
#include <sys/signalfd.h>
#include <sys/syslog.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <syslog.h>
#include <unistd.h>

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstring>
#include <fstream>
#include <functional>
#include <future>
#include <iostream>
#include <iterator>
#include <memory>
#include <mutex>
#include <string>
#include <system_error>
#include <thread>
#include <tuple>
#include <vector>

#include <INIReader.h>

#include <security/pam_appl.h>
#include <security/pam_ext.h>
#include <security/pam_modules.h>

#include "enter_device.hh"
#include "main.hh"
#include "optional_task.hh"

const auto DEFAULT_TIMEOUT =
    std::chrono::duration<int, std::chrono::milliseconds::period>(100);
const auto MAX_RETRIES = 5;
const auto PYTHON_EXECUTABLE = "python3";
const auto COMPARE_PROCESS_PATH = "/lib/security/howdy/compare.py";

#define S(msg) gettext(msg)

/**
 * Inspect the status code returned by the compare process
 * @param  status        The status code
 * @param  conv_function The PAM conversation function
 * @return               A PAM return code
 */
auto howdy_error(int status,
                 const std::function<int(int, const char *)> &conv_function)
    -> int {
  // If the process has exited
  if (WIFEXITED(status)) {
    // Get the status code returned
    status = WEXITSTATUS(status);

    switch (status) {
    case CompareError::NO_FACE_MODEL:
      syslog(LOG_NOTICE, "Failure, no face model known");
      break;
    case CompareError::TIMEOUT_REACHED:
      conv_function(PAM_ERROR_MSG, S("Failure, timeout reached"));
      syslog(LOG_ERR, "Failure, timeout reached");
      break;
    case CompareError::ABORT:
      syslog(LOG_ERR, "Failure, general abort");
      break;
    case CompareError::TOO_DARK:
      conv_function(PAM_ERROR_MSG, S("Face detection image too dark"));
      syslog(LOG_ERR, "Failure, image too dark");
      break;
    case CompareError::INVALID_DEVICE:
      syslog(LOG_ERR, "Failure, not possible to open camera at configured path");
      break;
    default:
      conv_function(PAM_ERROR_MSG,
                    std::string(S("Unknown error: ") + status).c_str());
      syslog(LOG_ERR, "Failure, unknown error %d", status);
    }
  } else if (WIFSIGNALED(status)) {
    // We get the signal
    status = WTERMSIG(status);

    syslog(LOG_ERR, "Child killed by signal %s (%d)", strsignal(status),
           status);
  }

  // As this function is only called for error status codes, signal an error to
  // PAM
  return PAM_AUTH_ERR;
}

/**
 * Format the success message if the status is successful or log the error in
 * the other case
 * @param  username      Username
 * @param  status        Status code
 * @param  config        INI  configuration
 * @param  conv_function PAM conversation function
 * @return          Returns the conversation function return code
 */
auto howdy_status(char *username, int status, const INIReader &config,
                  const std::function<int(int, const char *)> &conv_function)
    -> int {
  if (status != EXIT_SUCCESS) {
    return howdy_error(status, conv_function);
  }

  if (!config.GetBoolean("core", "no_confirmation", true)) {
    // Construct confirmation text from i18n string
    std::string confirm_text(S("Identified face as {}"));
    std::string identify_msg =
        confirm_text.replace(confirm_text.find("{}"), 2, std::string(username));
    conv_function(PAM_TEXT_INFO, identify_msg.c_str());
  }

  syslog(LOG_INFO, "Login approved");

  return PAM_SUCCESS;
}

/**
 * Check if Howdy should be enabled according to the configuration and the
 * environment.
 * @param  config INI configuration
 * @return        Returns PAM_AUTHINFO_UNAVAIL if it shouldn't be enabled,
 * PAM_SUCCESS otherwise
 */
auto check_enabled(const INIReader &config) -> int {
  // Stop executing if Howdy has been disabled in the config
  if (config.GetBoolean("core", "disabled", false)) {
    syslog(LOG_INFO, "Skipped authentication, Howdy is disabled");
    return PAM_AUTHINFO_UNAVAIL;
  }

  // Stop if we're in a remote shell and configured to exit
  if (config.GetBoolean("core", "abort_if_ssh", true)) {
    if (getenv("SSH_CONNECTION") != nullptr ||
        getenv("SSH_CLIENT") != nullptr || getenv("SSHD_OPTS") != nullptr) {
      syslog(LOG_INFO, "Skipped authentication, SSH session detected");
      return PAM_AUTHINFO_UNAVAIL;
    }
  }

  // Try to detect the laptop lid state and stop if it's closed
  if (config.GetBoolean("core", "abort_if_lid_closed", true)) {
    glob_t glob_result;

    // Get any files containing lid state
    int return_value =
        glob("/proc/acpi/button/lid/*/state", 0, nullptr, &glob_result);

    if (return_value != 0) {
      syslog(LOG_ERR, "Failed to read files from glob: %d", return_value);
      if (errno != 0) {
        syslog(LOG_ERR, "Underlying error: %s (%d)", strerror(errno), errno);
      }
    } else {
      for (size_t i = 0; i < glob_result.gl_pathc; i++) {
        std::ifstream file(std::string(glob_result.gl_pathv[i]));
        std::string lid_state;
        std::getline(file, lid_state, static_cast<char>(file.eof()));

        if (lid_state.find("closed") != std::string::npos) {
          globfree(&glob_result);

          syslog(LOG_INFO, "Skipped authentication, closed lid detected");
          return PAM_AUTHINFO_UNAVAIL;
        }
      }
    }
    globfree(&glob_result);
  }

  return PAM_SUCCESS;
}

/**
 * The main function, runs the identification and authentication
 * @param  pamh     The handle to interface directly with PAM
 * @param  flags    Flags passed on to us by PAM, XORed
 * @param  argc     Amount of rules in the PAM config (disregared)
 * @param  argv     Options defined in the PAM config
 * @param  auth_tok True if we should ask for a password too
 * @return          Returns a PAM return code
 */
auto identify(pam_handle_t *pamh, int flags, int argc, const char **argv,
              bool auth_tok) -> int {
  INIReader config("/etc/howdy/config.ini");
  openlog("pam_howdy", 0, LOG_AUTHPRIV);

  // Error out if we could not read the config file
  if (config.ParseError() != 0) {
    syslog(LOG_ERR, "Failed to parse the configuration file: %d",
           config.ParseError());
    return PAM_SYSTEM_ERR;
  }

  // Will contain the responses from PAM functions
  int pam_res = PAM_IGNORE;

  // Check if we should continue
  if ((pam_res = check_enabled(config)) != PAM_SUCCESS) {
    return pam_res;
  }

  Workaround workaround =
      get_workaround(config.GetString("core", "workaround", "input"));

  // Will contain PAM conversation structure
  struct pam_conv *conv = nullptr;
  const void **conv_ptr =
      const_cast<const void **>(reinterpret_cast<void **>(&conv));

  if ((pam_res = pam_get_item(pamh, PAM_CONV, conv_ptr)) != PAM_SUCCESS) {
    syslog(LOG_ERR, "Failed to acquire conversation");
    return pam_res;
  }

  // Wrap the PAM conversation function in our own, easier function
  auto conv_function = [conv](int msg_type, const char *msg_str) {
    const struct pam_message msg = {.msg_style = msg_type, .msg = msg_str};
    const struct pam_message *msgp = &msg;

    struct pam_response res = {};
    struct pam_response *resp = &res;

    return conv->conv(1, &msgp, &resp, conv->appdata_ptr);
  };

  // Initialize gettext
  setlocale(LC_ALL, "");
  bindtextdomain(GETTEXT_PACKAGE, LOCALEDIR);
  textdomain(GETTEXT_PACKAGE);

  // If enabled, send a notice to the user that facial login is being attempted
  bool detection_notice = config.GetBoolean("core", "detection_notice", true);

  // Get the username from PAM, needed to match correct face model
  char *username = nullptr;
  if ((pam_res = pam_get_user(pamh, const_cast<const char **>(&username),
                              nullptr)) != PAM_SUCCESS) {
    syslog(LOG_ERR, "Failed to get username");
    return pam_res;
  }

  int conv_pipe[2];

  if (pipe (conv_pipe)) {
    syslog(LOG_ERR, "Pipe failed.");
    return PAM_SYSTEM_ERR;
  }

  posix_spawn_file_actions_t action;
  posix_spawn_file_actions_init(&action);
  posix_spawn_file_actions_addclose(&action, conv_pipe[0]);
  posix_spawn_file_actions_adddup2(&action, conv_pipe[1], 1);
  posix_spawn_file_actions_addclose(&action, conv_pipe[1]);

  const char *const args[] = {PYTHON_EXECUTABLE, // NOLINT
                              COMPARE_PROCESS_PATH, username, nullptr};
  pid_t child_pid;

  // Start the python subprocess
  if (posix_spawnp(&child_pid, PYTHON_EXECUTABLE, &action, nullptr,
                   const_cast<char *const *>(args), nullptr) != 0) {
    syslog(LOG_ERR, "Can't spawn the howdy process: %s (%d)", strerror(errno),
           errno);
    return PAM_SYSTEM_ERR;
  }

  // show the PAM message from the compare script
  optional_task<void> child_conv([&] {
    char buffer[100];
    while(read(conv_pipe[0], buffer, 100)) {
      if (!strncmp(buffer, "HAS_MODEL", 9) && detection_notice) {
        if ((conv_function(PAM_TEXT_INFO,
                           S("Attempting facial authentication"))) !=
            PAM_SUCCESS) {
          syslog(LOG_ERR, "Failed to send detection notice");
        }
      }
    }
  });
  child_conv.activate();

  // NOTE: We should replace mutex and condition_variable by atomic wait, but
  // it's too recent (C++20)
  std::mutex mutx;
  std::condition_variable convar;
  ConfirmationType confirmation_type(ConfirmationType::Unset);

  // This task wait for the status of the python subprocess (we don't want a
  // zombie process)
  optional_task<int> child_task([&] {
    int status;
    wait(&status);
    {
      std::unique_lock<std::mutex> lock(mutx);
      if (confirmation_type == ConfirmationType::Unset) {
        confirmation_type = ConfirmationType::Howdy;
      }
    }
    convar.notify_one();

    return status;
  });
  child_task.activate();

  // This task waits for the password input (if the workaround wants it)
  optional_task<std::tuple<int, char *>> pass_task([&] {
    char *auth_tok_ptr = nullptr;
    int pam_res = pam_get_authtok(
        pamh, PAM_AUTHTOK, const_cast<const char **>(&auth_tok_ptr), nullptr);
    {
      std::unique_lock<std::mutex> lock(mutx);
      if (confirmation_type == ConfirmationType::Unset) {
        confirmation_type = ConfirmationType::Pam;
      }
    }
    convar.notify_one();

    return std::tuple<int, char *>(pam_res, auth_tok_ptr);
  });

  auto ask_pass = auth_tok && workaround != Workaround::Off;

  // We ask for the password if the function requires it and if a workaround is
  // set
  if (ask_pass) {
    pass_task.activate();
  }

  // Wait for the end either of the child or the password input
  {
    std::unique_lock<std::mutex> lock(mutx);
    convar.wait(lock, [&] { return confirmation_type != ConfirmationType::Unset; });
  }

  // The password has been entered or an error has occurred
  if (confirmation_type == ConfirmationType::Pam) {
    // We kill the child because we don't need its result
    kill(child_pid, SIGTERM);
    child_task.stop(false);

    // We just wait for the thread to stop since it's this one which sent us the
    // confirmation type
    pass_task.stop(false);

    char *password = nullptr;
    std::tie(pam_res, password) = pass_task.get();

    if (pam_res != PAM_SUCCESS) {
      return pam_res;
    }

    // The password has been entered, we are passing it to PAM stack
    return PAM_IGNORE;
  }

  // The compare process has finished its execution
  child_task.stop(false);
  child_conv.stop(true);

  // Get python process status code
  int status = child_task.get();

  // If python process ran into a timeout
  // Do not send enter presses or terminate the PAM function, as the user might
  // still be typing their password
  if (WIFEXITED(status) && WEXITSTATUS(status) != EXIT_SUCCESS && ask_pass) {
    // Wait for the password to be typed
    pass_task.stop(false);

    char *password = nullptr;
    std::tie(pam_res, password) = pass_task.get();

    if (pam_res != PAM_SUCCESS) {
      return howdy_status(username, status, config, conv_function);
    }

    // The password has been entered, we are passing it to PAM stack
    return PAM_IGNORE;
  }

  // We want to stop the password prompt, either by canceling the thread when
  // workaround is set to "native", or by emulating "Enter" input with
  // "input"

  // UNSAFE: We cancel the thread using pthread, pam_get_authtok seems to be
  // a cancellation point
  if (workaround == Workaround::Native) {
    pass_task.stop(true);
  } else if (workaround == Workaround::Input) {
    // We check if we have the right permissions on /dev/uinput
    if (euidaccess("/dev/uinput", W_OK | R_OK) != 0) {
      syslog(LOG_WARNING, "Insufficient permissions to create the fake device");
      conv_function(PAM_ERROR_MSG,
                    S("Insufficient permissions to send Enter "
                      "press, waiting for user to press it instead"));
    } else {
      try {
        EnterDevice enter_device;
        int retries;

        // We try to send it
        enter_device.send_enter_press();

        for (retries = 0;
             retries < MAX_RETRIES &&
             pass_task.wait(DEFAULT_TIMEOUT) == std::future_status::timeout;
             retries++) {
          enter_device.send_enter_press();
        }

        if (retries == MAX_RETRIES) {
          syslog(LOG_WARNING,
                 "Failed to send enter input before the retries limit");
          conv_function(PAM_ERROR_MSG, S("Failed to send Enter press, waiting "
                                         "for user to press it instead"));
        }
      } catch (std::runtime_error &err) {
        syslog(LOG_WARNING, "Failed to send enter input: %s", err.what());
        conv_function(PAM_ERROR_MSG, S("Failed to send Enter press, waiting "
                                       "for user to press it instead"));
      }
    }

    // We stop the thread (will block until the enter key is pressed if the
    // input wasn't focused or if the uinput device failed to send keypress)
    pass_task.stop(false);
  }

  return howdy_status(username, status, config, conv_function);
}

// Called by PAM when a user needs to be authenticated, for example by running
// the sudo command
PAM_EXTERN auto pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc,
                                    const char **argv) -> int {
  return identify(pamh, flags, argc, argv, true);
}

// Called by PAM when a session is started, such as by the su command
PAM_EXTERN auto pam_sm_open_session(pam_handle_t *pamh, int flags, int argc,
                                    const char **argv) -> int {
  return identify(pamh, flags, argc, argv, false);
}

// The functions below are required by PAM, but not needed in this module
PAM_EXTERN auto pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc,
                                 const char **argv) -> int {
  return PAM_IGNORE;
}
PAM_EXTERN auto pam_sm_close_session(pam_handle_t *pamh, int flags, int argc,
                                     const char **argv) -> int {
  return PAM_IGNORE;
}
PAM_EXTERN auto pam_sm_chauthtok(pam_handle_t *pamh, int flags, int argc,
                                 const char **argv) -> int {
  return PAM_IGNORE;
}
PAM_EXTERN auto pam_sm_setcred(pam_handle_t *pamh, int flags, int argc,
                               const char **argv) -> int {
  return PAM_IGNORE;
}
