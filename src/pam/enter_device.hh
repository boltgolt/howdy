#ifndef __ENTER_DEVICE_H_
#define __ENTER_DEVICE_H_

#include <libevdev/libevdev-uinput.h>
#include <libevdev/libevdev.h>
#include <memory>

class EnterDevice {
  std::unique_ptr<struct libevdev, decltype(&libevdev_free)> raw_device;
  std::unique_ptr<struct libevdev_uinput, decltype(&libevdev_uinput_destroy)>
      raw_uinput_device;

public:
  EnterDevice();
  void send_enter_press() const;
  ~EnterDevice() = default;
};

#endif // __ENTER_DEVICE_H
