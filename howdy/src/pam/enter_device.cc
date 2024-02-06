#include "enter_device.hh"

#include <cstring>
#include <memory>
#include <stdexcept>

EnterDevice::EnterDevice()
    : raw_device(libevdev_new(), &libevdev_free),
      raw_uinput_device(nullptr, &libevdev_uinput_destroy) {
  auto *dev_ptr = raw_device.get();

  libevdev_set_name(dev_ptr, "enter device");
  libevdev_enable_event_type(dev_ptr, EV_KEY);
  libevdev_enable_event_code(dev_ptr, EV_KEY, KEY_SPACE, nullptr);
  libevdev_enable_event_code(dev_ptr, EV_KEY, KEY_ENTER, nullptr);

  int err;
  struct libevdev_uinput *uinput_dev_ptr;
  if ((err = libevdev_uinput_create_from_device(
           dev_ptr, LIBEVDEV_UINPUT_OPEN_MANAGED, &uinput_dev_ptr)) != 0) {
    throw std::runtime_error(std::string("Failed to create device: ") +
                             strerror(-err));
  }

  raw_uinput_device.reset(uinput_dev_ptr);
};

void EnterDevice::send_space_press() const {
  auto *uinput_dev_ptr = raw_uinput_device.get();

  int err;
  if ((err = libevdev_uinput_write_event(uinput_dev_ptr, EV_KEY, KEY_SPACE,
                                         1)) != 0) {
    throw std::runtime_error(std::string("Failed to write event: ") +
                             strerror(-err));
  }

  if ((err = libevdev_uinput_write_event(uinput_dev_ptr, EV_KEY, KEY_SPACE,
                                         0)) != 0) {
    throw std::runtime_error(std::string("Failed to write event: ") +
                             strerror(-err));
  }

  if ((err = libevdev_uinput_write_event(uinput_dev_ptr, EV_SYN, SYN_REPORT,
                                         0)) != 0)
  {
    throw std::runtime_error(std::string("Failed to write event: ") +
                             strerror(-err));
  };
}

void EnterDevice::send_enter_press() const {
  auto *uinput_dev_ptr = raw_uinput_device.get();

  int err;
  if ((err = libevdev_uinput_write_event(uinput_dev_ptr, EV_KEY, KEY_ENTER,
                                         1)) != 0) {
    throw std::runtime_error(std::string("Failed to write event: ") +
                             strerror(-err));
  }

  if ((err = libevdev_uinput_write_event(uinput_dev_ptr, EV_KEY, KEY_ENTER,
                                         0)) != 0) {
    throw std::runtime_error(std::string("Failed to write event: ") +
                             strerror(-err));
  }

  if ((err = libevdev_uinput_write_event(uinput_dev_ptr, EV_SYN, SYN_REPORT,
                                         0)) != 0) {
    throw std::runtime_error(std::string("Failed to write event: ") +
                             strerror(-err));
  };
}
