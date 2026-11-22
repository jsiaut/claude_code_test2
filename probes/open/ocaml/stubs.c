#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <caml/mlvalues.h>
value probe_gettid(value u) { (void)u; return Val_long(syscall(SYS_gettid)); }
value probe_getcpu(value u) { (void)u; return Val_long(sched_getcpu()); }
