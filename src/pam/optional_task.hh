#ifndef OPTIONAL_TASK_H_
#define OPTIONAL_TASK_H_

#include <cassert>
#include <chrono>
#include <future>
#include <thread>

// A task executed only if activated.
template <typename T> class optional_task {
  std::thread thread;
  std::packaged_task<T()> task;
  std::future<T> future;
  bool spawned;
  bool is_active;

public:
  explicit optional_task(std::function<T()> fn);
  void activate();
  template <typename R, typename P>
  auto wait(std::chrono::duration<R, P> dur) -> std::future_status;
  auto get() -> T;
  void stop(bool force);
  ~optional_task();
};

template <typename T>
optional_task<T>::optional_task(std::function<T()> fn)
    : task(std::packaged_task<T()>(std::move(fn))), future(task.get_future()),
      spawned(false), is_active(false) {}

// Create a new thread and launch the task on it.
template <typename T> void optional_task<T>::activate() {
  thread = std::thread(std::move(task));
  spawned = true;
  is_active = true;
}

// Wait for `dur` time and return a `future` status.
template <typename T>
template <typename R, typename P>
auto optional_task<T>::wait(std::chrono::duration<R, P> dur)
    -> std::future_status {
  return future.wait_for(dur);
}

// Get the value.
// WARNING: The function hould be run only if the task has successfully been
// stopped.
template <typename T> auto optional_task<T>::get() -> T {
  assert(!is_active && spawned);
  return future.get();
}

// Stop the thread:
// - if `force` is `false`, by joining the thread.
// - if `force` is `true`, by cancelling the thread using `pthread_cancel`.
// WARNING: This function should be used with extreme caution when `force` is
// set to `true`.
template <typename T> void optional_task<T>::stop(bool force) {
  if (!(is_active && thread.joinable()) && spawned) {
    is_active = false;
    return;
  }

  // We use pthread to cancel the thread
  if (force) {
    auto native_hd = thread.native_handle();
    pthread_cancel(native_hd);
  }
  thread.join();
  is_active = false;
}

template <typename T> optional_task<T>::~optional_task<T>() {
  if (is_active && spawned) {
    stop(false);
  }
}

#endif // OPTIONAL_TASK_H_
