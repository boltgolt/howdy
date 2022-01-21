#ifndef MAIN_H_
#define MAIN_H_

#include <cstdint>
#include <string>

enum class Type { Unset, Howdy, Pam };

enum class Workaround { Off, Input, Native };

inline Workaround get_workaround(std::string workaround) {
  if (workaround == "input")
    return Workaround::Input;

  if (workaround == "native")
    return Workaround::Native;

  return Workaround::Off;
}

#endif // MAIN_H_
