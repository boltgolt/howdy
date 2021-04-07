#include <cerrno>
#include <csignal>
#include <cstdlib>
#include <glob.h>
#include <poll.h>
#include <pthread.h>
#include <spawn.h>
#include <sys/poll.h>
#include <sys/signalfd.h>
#include <sys/syslog.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <syslog.h>
#include <unistd.h>

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

using namespace std;

enum class Type { Howdy, Pam };

/**
 * Inspect the status code returned by the compare process
 * @param  code          The status code
 * @param  conv_function The PAM conversation function
 * @return               A PAM return code
 */
int on_howdy_auth(int code, function<int(int, const char *)> conv_function) {
  // If the process has exited
  if (!WIFEXITED(code)) {
    // Get the status code returned
    code = WEXITSTATUS(code);

    switch (code) {
    // Status 10 means we couldn't find any face models
    case 10:
      conv_function(PAM_ERROR_MSG, "There is no face model known");
      syslog(LOG_NOTICE, "Failure, no face model known");
      break;
    // Status 11 means we exceded the maximum retry count
    case 11:
      syslog(LOG_INFO, "Failure, timeout reached");
      break;
    // Status 12 means we aborted
    case 12:
      syslog(LOG_INFO, "Failure, general abort");
      break;
    // Status 13 means the image was too dark
    case 13:
      conv_function(PAM_ERROR_MSG, "Face detection image too dark");
      syslog(LOG_INFO, "Failure, image too dark");
      break;
    // Otherwise, we can't discribe what happend but it wasn't successful
    default:
      conv_function(PAM_ERROR_MSG,
                    string("Unknown error:" + to_string(code)).c_str());
      syslog(LOG_INFO, "Failure, unknown error %d", code);
    }
  }

  // As this function is only called for error status codes, signal an error to
  // PAM
  return PAM_AUTH_ERR;
}

/**
 * Format and send a message to PAM
 * @param  conv    PAM conversation function
 * @param  type    Type of PAM message
 * @param  message String to show the user
 * @return         Returns the conversation function return code
 */
int send_message(function<int(int, const struct pam_message **,
                              struct pam_response **, void *)>
                     conv,
                 int type, const char *message) {
  // Formet the message as PAM expects it
  // No need to free this, it's allocated on the stack
  const struct pam_message msg = {.msg_style = type, .msg = message};
  const struct pam_message *msgp = &msg;

  // Create a variable for the response to be stored in
  struct pam_response res_ = {};
  struct pam_response *resp_ = &res_;

  // Call the conversation function with the constructed arguments
  return conv(1, &msgp, &resp_, nullptr);
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
int identify(pam_handle_t *pamh, int flags, int argc, const char **argv,
             bool auth_tok) {
  // Open and read the config file
  INIReader reader("/lib/security/howdy/config.ini");
  // Open the system log so we can write to it
  openlog("pam_howdy", 0, LOG_AUTHPRIV);

  // Will contain PAM conversation function
  struct pam_conv *conv = nullptr;
  // Will contain the responses from PAM functions
  int pam_res = PAM_IGNORE;

  // Try to get the conversation function and error out if we can't
  if ((pam_res = pam_get_item(pamh, PAM_CONV, (const void **)&conv)) !=
      PAM_SUCCESS) {
    syslog(LOG_ERR, "Failed to acquire conversation");
    return pam_res;
  }

  // Wrap the PAM conversation function in our own, easier function
  auto conv_function =
      bind(send_message, conv->conv, placeholders::_1, placeholders::_2);

  // Error out if we could not ready the config file
  if (reader.ParseError() < 0) {
    syslog(LOG_ERR, "Failed to parse the configuration");
    return PAM_SYSTEM_ERR;
  }

  // Stop executing if Howdy has been disabled in the config
  if (reader.GetBoolean("core", "disabled", false)) {
    return PAM_AUTHINFO_UNAVAIL;
  }

  // Stop if we're in a remote shell and configured to exit
  if (reader.GetBoolean("core", "ignore_ssh", true)) {
    if (getenv("SSH_CONNECTION") != nullptr ||
        getenv("SSH_CLIENT") != nullptr || getenv("SSHD_OPTS") != nullptr) {
      return PAM_AUTHINFO_UNAVAIL;
    }
  }

  // If enabled, send a notice to the user that facial login is being attempted
  if (reader.GetBoolean("core", "detection_notice", false)) {
    if ((pam_res = conv_function(PAM_TEXT_INFO,
                                 "Attempting facial authentication")) !=
        PAM_SUCCESS) {
      syslog(LOG_ERR, "Failed to send detection notice");
    }
  }

  if (reader.GetBoolean("core", "ignore_closed_lid", true)) {
    glob_t glob_result{};

    int return_value =
        glob("/proc/acpi/button/lid/*/state", 0, nullptr, &glob_result);

    // TODO: We ignore the result
    if (return_value != 0) {
      globfree(&glob_result);
    }

    for (size_t i = 0; i < glob_result.gl_pathc; ++i) {
      ifstream file(string(glob_result.gl_pathv[i]));
      string lid_state;
      getline(file, lid_state, (char)file.eof());
      if (lid_state.find("closed") != std::string::npos) {
        globfree(&glob_result);
        return PAM_AUTHINFO_UNAVAIL;
      }
    }

    globfree(&glob_result);
  }

  char *user_ptr = nullptr;
  if ((pam_res = pam_get_user(pamh, (const char **)&user_ptr, nullptr)) !=
      PAM_SUCCESS) {
    syslog(LOG_ERR, "Failed to get username");
    return pam_res;
  }
  posix_spawn_file_actions_t file_actions;
  posix_spawn_file_actions_init(&file_actions);
  // We close stdout and stderr for the child
  posix_spawn_file_actions_addclose(&file_actions, STDOUT_FILENO);
  posix_spawn_file_actions_addclose(&file_actions, STDERR_FILENO);
  const char *const args[] = {"/usr/bin/python3", "/lib/security/howdy/compare.py",
                              user_ptr, nullptr};
  pid_t child_pid;

  if (posix_spawnp(&child_pid, "/usr/bin/python3", &file_actions, nullptr,
                   (char *const *)args, nullptr) < 0) {
    syslog(LOG_ERR, "Can't spawn the howdy process: %s", strerror(errno));
    return PAM_SYSTEM_ERR;
  }

  std::mutex m;
  std::condition_variable cv;
  Type t;
  packaged_task<int()> child_task([&] {
    int status;
    wait(&status);
    {
      unique_lock<mutex> lk(m);
      t = Type::Howdy;
    }
    cv.notify_all();
    return status;
  });
  auto child_future = child_task.get_future();
  thread child_thread(move(child_task));

  packaged_task<int()> pass_task([&] {
    char *auth_tok_ptr = nullptr;
    int pam_res = pam_get_authtok(pamh, PAM_AUTHTOK,
                                  (const char **)&auth_tok_ptr, nullptr);
    {
      unique_lock<mutex> lk(m);
      t = Type::Pam;
    }
    cv.notify_all();
    return pam_res;
  });
  auto pass_future = pass_task.get_future();
  thread pass_thread;
  if (auth_tok) {
    pass_thread = thread(move(pass_task));
  }

  {
    unique_lock<mutex> lk(m);
    cv.wait(lk);
  }

  if (t == Type::Howdy) {
    if (auth_tok) {
      // We cancel the thread using pthread, pam_get_authtok seems to be a
      // cancellation point
      auto native_hd = pass_thread.native_handle();
      pthread_cancel(native_hd);
      pass_thread.join();
    }
    child_thread.join();
    int howdy_status = child_future.get();

    if (howdy_status == 0) {
      if (!reader.GetBoolean("core", "no_confirmation", true)) {
        string identify_msg("Identified face as " + string(user_ptr));
        conv_function(PAM_TEXT_INFO, identify_msg.c_str());
      }
      syslog(LOG_INFO, "Login approved");
      return PAM_SUCCESS;
    } else {
      return on_howdy_auth(howdy_status, conv_function);
    }
  } else {
    kill(child_pid, SIGTERM);
    python_thread.join();
    pass_thread.join();
    auto pam_res = pass_future.get();

    if (pam_res != PAM_SUCCESS)
      return pam_res;

    return PAM_IGNORE;
  }
}

// Called by PAM when a user needs to be authenticated, for example by running
// the sudo command
PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc,
                                   const char **argv) {
  return identify(pamh, flags, argc, argv, true);
}

// Called by PAM when a session is started, such as by the su command
PAM_EXTERN int pam_sm_open_session(pam_handle_t *pamh, int flags, int argc,
                                   const char **argv) {
  return identify(pamh, flags, argc, argv, false);
}

// The functions below are required by PAM, but not needed in this module
PAM_EXTERN int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc,
                                const char **argv) {
  return PAM_IGNORE;
}
PAM_EXTERN int pam_sm_close_session(pam_handle_t *pamh, int flags, int argc,
                                    const char **argv) {
  return PAM_IGNORE;
}
PAM_EXTERN int pam_sm_chauthtok(pam_handle_t *pamh, int flags, int argc,
                                const char **argv) {
  return PAM_IGNORE;
}
PAM_EXTERN int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc,
                              const char **argv) {
  return PAM_IGNORE;
}
