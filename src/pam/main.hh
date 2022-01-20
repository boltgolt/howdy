#ifndef MAIN_H_
#define MAIN_H_

#include <cstdint>
#include <string>

enum class Type { Unset, Howdy, Pam };

enum class Workaround { Off, Input, Native };

inline bool operator==(const std::string &l, const Workaround &r) {
  switch (r) {
  case Workaround::Off:
    return (l == "off");
  case Workaround::Input:
    return (l == "input");
  case Workaround::Native:
    return (l == "native");
  default:
    return false;
  }
}

inline bool operator==(const Workaround &l, const std::string &r) {
  return operator==(r, l);
}

inline bool operator!=(const std::string &l, const Workaround &r) {
  return !operator==(l, r);
}

inline bool operator!=(const Workaround &l, const std::string &r) {
  return operator!=(r, l);
}

#endif // MAIN_H_
