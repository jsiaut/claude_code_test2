#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>
long probe_gettid(void) { return (long)syscall(SYS_gettid); }
