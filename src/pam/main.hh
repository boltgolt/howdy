#ifndef MAIN_H_
#define MAIN_H_

#include <cstdint>
#include <string>

enum class ConfirmationType { Unset, Howdy, Pam };

enum class Workaround { Off, Input, Native };

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
