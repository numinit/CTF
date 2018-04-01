#!/bin/sh 

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
