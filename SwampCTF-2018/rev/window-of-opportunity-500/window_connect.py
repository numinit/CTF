#!/usr/bin/env python2

import z3
import time
import datetime
import os

def start_processes(redundancy):
    for i in range(redundancy):
        pid = os.fork()
        if pid == 0:
            # Child
            os.execlp('nc', 'nc', 'chal1.swampctf.com', '1313')
            sys.exit(1)

smt = z3.Optimize()
timestamp = z3.BitVec('timestamp', 32)
token = z3.BitVec('token', 32)

# This token gets us the flag
smt.add(token == 0xff4fdc56)
smt.add(token == (((timestamp & 0xFFC) << 16) - 0x14C437BE) ^ ((timestamp & 0xF0) << 8) | ((timestamp & 0xFFC) << 8) | ((timestamp >> 8) << 24) | timestamp & 0xFC)

# Find the closest timestamp to now
smt.add(timestamp > int(time.time()))
smt.minimize(timestamp)

if smt.check() != z3.unsat:
    model = smt.model()
    ts = model[timestamp].as_long()
    #ts = int(time.time())
    dt = datetime.datetime.fromtimestamp(ts)

    # The server is 2 minutes behind us
    server_delta = -120 - 13

    # The server takes 5 seconds to start up
    startup_delay = 5

    # We will try every second in this range
    time_range = 2

    # Start this many connections
    redundancy = 3

    target = ts - server_delta - startup_delay
    target_dt = datetime.datetime.fromtimestamp(target)

    range_low = target - time_range
    range_hi = target + time_range

    print('Trying %d (%s)' % (ts, dt.strftime('%Y-%m-%dT%H:%M:%S')))
    print('Target is %d (%s)' % (target, target_dt.strftime('%Y-%m-%dT%H:%M:%S')))
    while True:
        now = int(time.time())
        now_dt = datetime.datetime.fromtimestamp(now)
        if now >= range_low and now <= range_hi:
            print("WE'RE GOING @ %s (%d)" % (now_dt.strftime('%Y-%m-%dT%H:%M:%S'), now))
            start_processes(redundancy)
        else:
            print('It is now %s (%d); shooting for %s (%d) to hit %d' % 
                    (now_dt.strftime('%Y-%m-%dT%H:%M:%S'), now,
                        target_dt.strftime('%Y-%m-%dT%H:%M:%S'), target, ts))
        
        time.sleep(1)
