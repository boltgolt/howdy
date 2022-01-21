#include <boost/locale/message.hpp>
#include <cerrno>
#include <csignal>
#include <cstdlib>
#include <ostream>

#include <glob.h>
#include <pthread.h>
#include <spawn.h>
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

#include <boost/locale.hpp>

#include <security/pam_appl.h>
#include <security/pam_ext.h>
#include <security/pam_modules.h>

#include "main.hh"
#include "optional_task.hh"

const auto DEFAULT_TIMEOUT =
    std::chrono::duration<int, std::chrono::milliseconds::period>(2500);

#define S(msg) boost::locale::dgettext("pam", msg)

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
    // Status 10 means we couldn't find any face models
    case 10:
      conv_function(PAM_ERROR_MSG, S("There is no face model known").c_str());
      syslog(LOG_NOTICE, "Failure, no face model known");
      break;
    // Status 11 means we exceded the maximum retry count
    case 11:
      syslog(LOG_ERR, "Failure, timeout reached");
      break;
    // Status 12 means we aborted
    case 12:
      syslog(LOG_ERR, "Failure, general abort");
      break;
    // Status 13 means the image was too dark
    case 13:
      conv_function(PAM_ERROR_MSG, S("Face detection image too dark").c_str());
      syslog(LOG_ERR, "Failure, image too dark");
      break;
    // Otherwise, we can't describe what happened but it wasn't successful
    default:
      conv_function(
          PAM_ERROR_MSG,
          S("Unknown error: ").append(std::to_string(status)).c_str());
      syslog(LOG_ERR, "Failure, unknown error %d", status);
    }
  } else {
    // We get the signal
    status = WIFSIGNALED(status);

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
 * @param  reader        INI  configuration
 * @param  conv_function PAM conversation function
 * @return          Returns the conversation function return code
 */
auto howdy_msg(char *username, int status, INIReader &reader,
               const std::function<int(int, const char *)> &conv_function)
    -> int {
  if (status != EXIT_SUCCESS) {
    return howdy_error(status, conv_function);
  }

  if (!reader.GetBoolean("core", "no_confirmation", true)) {
    // Construct confirmation text from i18n string
    std::string confirm_text = S("Identified face as {}");
    std::string identify_msg =
        confirm_text.replace(confirm_text.find("{}"), 2, std::string(username));
    conv_function(PAM_TEXT_INFO, identify_msg.c_str());
  }

  syslog(LOG_INFO, "Login approved");

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
  INIReader reader("/lib/security/howdy/config.ini");
  // Open the system log so we can write to it
  openlog("pam_howdy", 0, LOG_AUTHPRIV);

  Workaround workaround =
      get_workaround(reader.GetString("core", "workaround", "input"));

  // In this case, we are not asking for the password
  if (workaround == Workaround::Off && auth_tok) {
    auth_tok = false;
  }

  // Will contain PAM conversation structure
  struct pam_conv *conv = nullptr;
  const void **conv_ptr =
      const_cast<const void **>(reinterpret_cast<void **>(&conv));
  // Will contain the responses from PAM functions
  int pam_res = PAM_IGNORE;

  // Try to get the conversation function and error out if we can't
  if ((pam_res = pam_get_item(pamh, PAM_CONV, conv_ptr)) != PAM_SUCCESS) {
    syslog(LOG_ERR, "Failed to acquire conversation");
    return pam_res;
  }

  // Wrap the PAM conversation function in our own, easier function
  auto conv_function = [conv](int msg_type, const char *msg_str) {
    // No need to free this, it's allocated on the stack
    const struct pam_message msg = {.msg_style = msg_type, .msg = msg_str};
    const struct pam_message *msgp = &msg;

    struct pam_response res = {};
    struct pam_response *resp = &res;

    // Call the conversation function with the constructed arguments
    return conv->conv(1, &msgp, &resp, conv->appdata_ptr);
  };

  // Error out if we could not ready the config file
  if (reader.ParseError() < 0) {
    syslog(LOG_ERR, "Failed to parse the configuration file");
    return PAM_SYSTEM_ERR;
  }

  // Stop executing if Howdy has been disabled in the config
  if (reader.GetBoolean("core", "disabled", false)) {
    syslog(LOG_INFO, "Skipped authentication, Howdy is disabled");
    return PAM_AUTHINFO_UNAVAIL;
  }

  // Stop if we're in a remote shell and configured to exit
  if (reader.GetBoolean("core", "ignore_ssh", true)) {
    if (getenv("SSH_CONNECTION") != nullptr ||
        getenv("SSH_CLIENT") != nullptr || getenv("SSHD_OPTS") != nullptr) {
      syslog(LOG_INFO, "Skipped authentication, SSH session detected");
      return PAM_AUTHINFO_UNAVAIL;
    }
  }

  // Try to detect the laptop lid state and stop if it's closed
  if (reader.GetBoolean("core", "ignore_closed_lid", true)) {
    glob_t glob_result;

    // Get any files containing lid state
    int return_value =
        glob("/proc/acpi/button/lid/*/state", 0, nullptr, &glob_result);

    if (return_value != 0) {
      syslog(LOG_ERR, "Failed to read files from glob: %d", return_value);
      if (errno != 0) {
        syslog(LOG_ERR, "Underlying error: %s (%d)", strerror(errno), errno);
      }
      globfree(&glob_result);
    }

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

    globfree(&glob_result);
  }

  // If enabled, send a notice to the user that facial login is being attempted
  if (reader.GetBoolean("core", "detection_notice", false)) {
    if ((conv_function(PAM_TEXT_INFO,
                       S("Attempting facial authentication").c_str())) !=
        PAM_SUCCESS) {
      syslog(LOG_ERR, "Failed to send detection notice");
    }
  }

  // Get the username from PAM, needed to match correct face model
  char *username = nullptr;
  if ((pam_res = pam_get_user(pamh, const_cast<const char **>(&username),
                              nullptr)) != PAM_SUCCESS) {
    syslog(LOG_ERR, "Failed to get username");
    return pam_res;
  }

  posix_spawn_file_actions_t file_actions;
  posix_spawn_file_actions_init(&file_actions);

  const char *const args[] = {"/usr/bin/python3", // NOLINT
                              "/lib/security/howdy/compare.py", username,
                              nullptr};
  pid_t child_pid;

  // Start the python subprocess
  if (posix_spawnp(&child_pid, "/usr/bin/python3", &file_actions, nullptr,
                   const_cast<char *const *>(args), nullptr) > 0) {
    syslog(LOG_ERR, "Can't spawn the howdy process: %s (%d)", strerror(errno),
           errno);
    return PAM_SYSTEM_ERR;
  }

  // NOTE: We should replace mutex and condition_variable by atomic wait, but
  // it's too recent (C++20)
  std::mutex m;
  std::condition_variable cv;
  std::atomic<ConfirmationType> confirmation_type(ConfirmationType::Unset);

  // This task wait for the status of the python subprocess (we don't want a
  // zombie process)
  optional_task<int> child_task(std::packaged_task<int()>([&] {
    int status;
    wait(&status);

    {
      std::unique_lock<std::mutex> lk(m);
      ConfirmationType type = confirmation_type.load(std::memory_order_relaxed);
      if (type == ConfirmationType::Unset) {
        confirmation_type.store(ConfirmationType::Howdy,
                                std::memory_order_relaxed);
      }
    }
    cv.notify_one();

    return status;
  }));
  child_task.activate();

  // This task waits for the password input (if the workaround wants it)
  optional_task<std::tuple<int, char *>> pass_task(
      std::packaged_task<std::tuple<int, char *>()>([&] {
        char *auth_tok_ptr = nullptr;
        int pam_res =
            pam_get_authtok(pamh, PAM_AUTHTOK,
                            const_cast<const char **>(&auth_tok_ptr), nullptr);
        {
          std::unique_lock<std::mutex> lk(m);
          ConfirmationType type =
              confirmation_type.load(std::memory_order_relaxed);
          if (type == ConfirmationType::Unset) {
            confirmation_type.store(ConfirmationType::Pam,
                                    std::memory_order_relaxed);
          }
        }
        cv.notify_one();

        return std::tuple<int, char *>(pam_res, auth_tok_ptr);
      }));

  if (auth_tok) {
    pass_task.activate();
  }

  // Wait for the end either of the child or the password input
  {
    std::unique_lock<std::mutex> lk(m);
    cv.wait(lk, [&] { return confirmation_type != ConfirmationType::Unset; });
  }

  if (confirmation_type == ConfirmationType::Howdy) {
    child_task.stop(false);

    // If the workaround is native
    if (auth_tok) {
      // We cancel the thread using pthread, pam_get_authtok seems to be a
      // cancellation point
      if (pass_task.is_active()) {
        pass_task.stop(true);
      }
    }
    int howdy_status = child_task.get();

    return howdy_msg(username, howdy_status, reader, conv_function);
  }

  // The password has been entered

  // We need to be sure that we're not going to block forever if the
  // child has a problem
  if (child_task.wait(DEFAULT_TIMEOUT) == std::future_status::timeout) {
    kill(child_pid, SIGTERM);
  }
  child_task.stop(false);

  // We just wait for the thread to stop since it's this one which sent us the
  // confirmation type
  if (workaround == Workaround::Input && auth_tok) {
    pass_task.stop(false);
  }

  char *password = nullptr;
  std::tie(pam_res, password) = pass_task.get();

  if (pam_res != PAM_SUCCESS) {
    return pam_res;
  }

  int howdy_status = child_task.get();
  // If python process (or user) sent Enter key
  if (strlen(password) == 0) {
    return howdy_msg(username, howdy_status, reader, conv_function);
  }

  // The password has been entered, we are passing it to PAM stack
  return PAM_IGNORE;
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
