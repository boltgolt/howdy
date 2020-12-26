#include <cerrno>
#include <csignal>
#include <cstdlib>
#include <glob.h>
#include <poll.h>
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

int on_howdy_auth(int code, function<int(int, const char *)> conv_function) {

  switch (code) {
  case 10:
    conv_function(PAM_ERROR_MSG, "There is no face model known");
    syslog(LOG_NOTICE, "Failure, no face model known");
    break;
  case 11:
    syslog(LOG_INFO, "Failure, timeout reached");
    break;
  case 12:
    syslog(LOG_INFO, "Failure, general abort");
    break;
  case 13:
    syslog(LOG_INFO, "Failure, image too dark");
    break;
  default:
    conv_function(PAM_ERROR_MSG,
                  string("Unknown error:" + to_string(code)).c_str());
    syslog(LOG_INFO, "Failure, unknown error %d", code);
  }

  return PAM_AUTH_ERR;
}

int send_message(function<int(int, const struct pam_message **,
                              struct pam_response **, void *)>
                     conv,
                 int type, const char *message) {
  // No need to free this, it's allocated on the stack
  const struct pam_message msg = {.msg_style = type, .msg = message};
  const struct pam_message *msgp = &msg;

  struct pam_response res_ = {};
  struct pam_response *resp_ = &res_;

  return conv(1, &msgp, &resp_, nullptr);
}

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc,
                                   const char **argv) {
  INIReader reader("/lib/security/howdy/config.ini");
  openlog("[PAM_HOWDY]", 0, LOG_AUTHPRIV);

  struct pam_conv *conv = nullptr;
  int pam_res = PAM_IGNORE;

  if ((pam_res = pam_get_item(pamh, PAM_CONV, (const void **)&conv)) !=
      PAM_SUCCESS) {
    syslog(LOG_ERR, "Failed to acquire conversation");
    return pam_res;
  }

  auto conv_function =
      bind(send_message, (*conv->conv), placeholders::_1, placeholders::_2);

  if (reader.ParseError() < 0) {
    syslog(LOG_ERR, "Failed to parse the configuration");
    return PAM_SYSTEM_ERR;
  }

  if (reader.GetBoolean("core", "disabled", false)) {
    return PAM_AUTHINFO_UNAVAIL;
  }

  if (reader.GetBoolean("core", "ignore_ssh", true)) {
    if (getenv("SSH_CONNECTION") != nullptr ||
        getenv("SSH_CLIENT") != nullptr || getenv("SSHD_OPTS") != nullptr) {
      return PAM_AUTHINFO_UNAVAIL;
    }
  }

  if (reader.GetBoolean("core", "detection_notice", false)) {
    if ((pam_res = conv_function(PAM_TEXT_INFO,
                                 "Attempting facial authentication")) !=
        PAM_SUCCESS) {
      syslog(LOG_ERR, "Failed to send detection notice");
      return pam_res;
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
  string user(user_ptr);

  posix_spawn_file_actions_t file_actions;
  posix_spawn_file_actions_init(&file_actions);
  posix_spawn_file_actions_addclose(&file_actions, STDOUT_FILENO);
  posix_spawn_file_actions_addclose(&file_actions, STDERR_FILENO);
  vector<const char *> args{"python", "/lib/security/howdy/compare.py",
                            user.c_str(), nullptr};
  pid_t child_pid;
  if (posix_spawnp(&child_pid, "python", &file_actions, nullptr,
                   (char *const *)args.data(), nullptr) < 0) {
    syslog(LOG_ERR, "Can't spawn the howdy process: %s", strerror(errno));
    return PAM_SYSTEM_ERR;
  }

  packaged_task<int()> child_task([&] {
    int status;
    wait(&status);
    return status;
  });
  auto child_future = child_task.get_future();
  thread child_thread(move(child_task));

  auto pass_future = async(launch::async, [&] {
    char *auth_tok_ptr = nullptr;
    int pam_res = pam_get_authtok(pamh, PAM_AUTHTOK,
                                  (const char **)&auth_tok_ptr, nullptr);
    return make_pair(auth_tok_ptr, pam_res);
  });

  auto pass = pass_future.get();

  if (child_future.wait_for(1.5s) == future_status::timeout) {
    kill(child_pid, SIGTERM);
  }
  child_thread.join();
  int howdy_status = child_future.get();

  if (howdy_status == 0) {
    if (!reader.GetBoolean("section", "no_confirmation", true)) {
      string identify_msg("Identified face as " + user);
      conv_function(PAM_TEXT_INFO, identify_msg.c_str());
    }

    syslog(LOG_INFO, "Login approved");
    return PAM_SUCCESS;
  } else if ((get<int>(pass) == PAM_SUCCESS && get<char *>(pass) != nullptr &&
              !string(get<char *>(pass)).empty()) ||
             WIFSIGNALED(howdy_status)) {
    return PAM_IGNORE;
  } else {
    return on_howdy_auth(howdy_status, conv_function);
  }
}
