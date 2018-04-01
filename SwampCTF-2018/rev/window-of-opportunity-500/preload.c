/* gcc -shared -fPIC -Os -opreload.so preload.c */

#include <stdlib.h>
#include <sys/time.h>
#include <unistd.h>
#include <signal.h>

int gettimeofday(struct timeval *tv, struct timezone *tz) {
    const char *timestamp_str = getenv("TS");
    unsigned long int timestamp = timestamp_str ? strtoul(timestamp_str, NULL, 10) : 0;
    tv->tv_sec = timestamp;
    tv->tv_usec = 0;
}

unsigned int sleep(unsigned int seconds) {
    // Just pretend we slept for that many seconds to move things along.
    return seconds;
}

