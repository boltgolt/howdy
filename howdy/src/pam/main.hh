#ifndef MAIN_H_
#define MAIN_H_

#include <cstring>
#include <string>
#include <unistd.h>
#include <cstdint>

enum class ConfirmationType : std::uint8_t { Unset, Howdy, Pam };
enum class Workaround : std::uint8_t { Off, Input, Native };

// Exit status codes returned by the compare process
enum CompareError : std::uint8_t {
  NO_FACE_MODEL = 10,
  TIMEOUT_REACHED = 11,
  ABORT = 12,
  TOO_DARK = 13,
  INVALID_DEVICE = 14,
  RUBBERSTAMP = 15
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

/**
 * Check if an environment variable exists either in the environ array or using
 * getenv.
 * @param name The name of the environment variable.
 * @return The value of the environment variable or nullptr if it doesn't exist
 * or environ is nullptr.
 * @note This function was created because `getenv` wasn't working properly in
 * some contexts (like sudo).
 */
auto checkenv(const char *name) -> bool {
  if (std::getenv(name) != nullptr) {
    return true;
  }

  auto len = strlen(name);

  for (char **env = environ; *env != nullptr; env++) {
    if (strncmp(*env, name, len) == 0) {
      return true;
    }
  }

  return false;
}

/**
 * Get the value of an environment variable either using getenv or from the
 * environ array.
 * @param name The name of the environment variable.
 * @return The value of the environment variable or nullptr if it doesn't exist.
 * @note The environ array is searched for the same reason as in checkenv.
 */
auto getenv_value(const char *name) -> const char * {
  const char *value = std::getenv(name);
  if (value != nullptr) {
    return value;
  }

  auto len = strlen(name);

  for (char **env = environ; *env != nullptr; env++) {
    // Only match the full name, directly followed by the equals sign
    if (strncmp(*env, name, len) == 0 && (*env)[len] == '=') {
      return *env + len + 1;
    }
  }

  return nullptr;
}

/**
 * Check if a locale environment variable is safe to pass to the root python
 * subprocess.
 * @param value The value of the environment variable.
 * @return True if the value only looks like locale names.
 */
auto is_safe_locale(const char *value) -> bool {
  if (*value == '\0' || strstr(value, "..") != nullptr) {
    return false;
  }

  for (const char *chr = value; *chr != '\0'; chr++) {
    bool allowed = (*chr >= 'a' && *chr <= 'z') ||
                   (*chr >= 'A' && *chr <= 'Z') ||
                   (*chr >= '0' && *chr <= '9') || *chr == '_' ||
                   *chr == '.' || *chr == '@' || *chr == ':' || *chr == '-';
    if (!allowed) {
      return false;
    }
  }

  return true;
}

#endif // MAIN_H_
