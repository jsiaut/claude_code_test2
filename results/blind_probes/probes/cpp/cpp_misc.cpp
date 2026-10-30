#include <new>
#include <atomic>
#include <thread>
#include <numeric>
#include <execution>
#include <vector>
#include <set>
#include <mutex>
#include <cstdio>
int f(int x){ if (x > 0) [[likely]] return 1; else [[unlikely]] return 2; }
int main(){
  std::printf("destructive=%zu constructive=%zu\n", std::hardware_destructive_interference_size, std::hardware_constructive_interference_size);
  std::atomic<int> a{0}; a.store(1, std::memory_order_release); std::atomic_thread_fence(std::memory_order_seq_cst);
  std::vector<int> v(1<<20); std::iota(v.begin(), v.end(), 0);
  std::set<std::thread::id> ids; std::mutex m;
  std::for_each(std::execution::par, v.begin(), v.end(), [&](int){ std::lock_guard g(m); ids.insert(std::this_thread::get_id()); });
  std::printf("par for_each distinct threads=%zu likely=%d\n", ids.size(), f(3));
}
