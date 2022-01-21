#ifndef OPTIONAL_TASK_H_
#define OPTIONAL_TASK_H_

#include <cassert>
#include <chrono>
#include <future>
#include <thread>

template <typename T> class optional_task {
  std::thread _thread;
  std::packaged_task<T()> _task;
  std::future<T> _future;
  std::atomic<bool> _spawned;
  std::atomic<bool> _is_active;

public:
  explicit optional_task(std::packaged_task<T()> task);
  void activate();
  template <typename Dur, typename Rat>
  auto wait(std::chrono::duration<Dur, Rat> dur) -> std::future_status;
  auto get() -> T;
  auto is_active() -> bool;
  void stop(bool force);
  ~optional_task();
};

template <typename T>
optional_task<T>::optional_task(std::packaged_task<T()> t)
    : _task(std::move(t)), _future(_task.get_future()) {}

template <typename T> void optional_task<T>::activate() {
  _thread = std::thread(std::move(_task));
  _spawned = true;
  _is_active = true;
}

template <typename T>
template <typename Dur, typename Rat>
auto optional_task<T>::wait(std::chrono::duration<Dur, Rat> dur)
    -> std::future_status {
  return _future.wait_for(dur);
}

template <typename T> auto optional_task<T>::get() -> T {
  assert(!_is_active && _spawned);
  return _future.get();
}

template <typename T> auto optional_task<T>::is_active() -> bool {
  return _is_active;
}

template <typename T> void optional_task<T>::stop(bool force) {
  if (!(_is_active && _thread.joinable()) && _spawned) {
    _is_active = false;
    return;
  }

  // We use pthread to cancel the thread
  if (force) {
    auto native_hd = _thread.native_handle();
    pthread_cancel(native_hd);
  }
  _thread.join();
  _is_active = false;
}

template <typename T> optional_task<T>::~optional_task<T>() {
  if (_is_active && _spawned) {
    stop(false);
  }
}

#endif // OPTIONAL_TASK_H_
