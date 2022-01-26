#ifndef MAIN_H_
#define MAIN_H_

#include <string>

enum class ConfirmationType { Unset, Howdy, Pam };

enum class Workaround { Off, Input, Native };

// Exit status codes returned by the compare process
enum CompareError : int {
  NO_FACE_MODEL = 10,
  TIMEOUT_REACHED = 11,
  ABORT = 12,
  TOO_DARK = 13
};

inline auto get_workaround(const std::string &workaround) -> Workaround {
  if (workaround == "input") {
    return Workaround::Input;
  }

  if (workaround == "native") {
    return Workaround::Native;
  }

  return Workaround::Off;
}

#endif // MAIN_H_
