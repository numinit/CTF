# Window of Opportunity (rev500)

$ nc chal1.swampctf.com 1313

No user input. After some reverse engineering, it turns out that it mmaps a region of memory +rwx and generates an access token.
The token is generated based on the current time and used to decrypt a bunch of x86 instructions, which it then jumps to.
If you generate the right token, you get the flag.

An equation for the token is:

    (((tv.tv_sec & 0xFFC) << 16) - 0x14C437BE) ^ ((tv.tv_sec & 0xF0) << 8) | ((tv.tv_sec & 0xFFC) << 8) | ((tv.tv_sec >> 8) << 24) | tv.tv_sec & 0xFC;

There is an upper bound of 2^16 potential tokens. The search space is way smaller considering the crazy equation to make the token.

Considering that, it's sat solver time. Let's explore the space of tokens with z3: [source here](window_solve.py). Run it with `python window_solve.py | tee timestamps`.

Now that we have all the possible timestamps after the current one, we need to test them.
Let's write a [LD_PRELOAD](http://www.goldsborough.me/c/low-level/kernel/2016/08/29/16-48-53-the_-ld_preload-_trick/) shared library
that can mock `gettimeofday()`.

```c
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
```

So, we can rename the provided `OS.BIN` to `window` and run it like `TS=1522400279 LD_PRELOAD="$(realpath preload.so)" ./window` to mock the timestamp.

With a bunch of timestamps in hand, I wrote a bash script to run the binary a bunch of times to look for any output other than `NOT AUTHORIZED`.

```sh
(
    cat timestamps |
        sort -n |
        while read line; do
            ts="$(echo "$line" | cut -d, -f1)"
            tk="$(echo "$line" | cut -d, -f2)"
            echo -n "$ts,$tk,"
            TS="$ts" LD_PRELOAD="$(realpath preload.so)" timeout 5 ./window 2>&1 | grep 'NOT AUTHORIZED'
        done
) | tee results
```

It found a few. Manually reviewed them, and the one with key `0xff4fdc56` said "ACCESS GRANTED." Nice!

```
> RUN "V:\OS\GETFLG.BIN" WITH KEY "0xff4fdc56"
ACCESS GRANTED
RUNNING ...
```

Now we have the correct key, which makes coming up with z3 constraints way easier.
We just have to minimize `timestamp` with the constraints `timestamp > time.time()` (i.e. it's in the future) and `token == 0xff4fdc56`.
We also need to account for server/client clock difference and repeatedly run netcat when the "window of opportunity" presents itself. [Source here](window-connect.py).

Wait a while, and then...

```
> RUN "V:\OS\GETFLG.BIN" WITH KEY "0xff4fdc56"
ACCESS GRANTED
RUNNING ...
PERFORMING CHECKSUM ..... PASSED
LOADING DATA SECTION ..... LOADED

V:\OS\GETFLG.BIN > HELP
LIST
GET [ID]
SET [ID] [CONTENT]
CREATE [CONTENT]
EXIT


V:\OS\GETFLG.BIN > LIST
FLAG # |         DATE CREATED      |      LAST MODIFIED        |
-------+---------------------------+---------------------------+
1      | 2018-03-19T18:32:02+00:00 | 2018-03-29T04:56:40+00:00 |


V:\OS\GETFLG.BIN > GET 1
FLAG 1: flag{y0ur_t1m3_t0_sh1ne_is_N0W}
```

