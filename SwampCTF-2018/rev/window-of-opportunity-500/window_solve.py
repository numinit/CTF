#!/usr/bin/env python2

import z3
import time

smt = z3.Optimize()
timestamp = z3.BitVec('timestamp', 32)
token = z3.BitVec('token', 32)
smt.add(token == (((timestamp & 0xFFC) << 16) - 0x14C437BE) ^ ((timestamp & 0xF0) << 8) | ((timestamp & 0xFFC) << 8) | ((timestamp >> 8) << 24) | timestamp & 0xFC)
smt.add(timestamp > int(time.time()))

timestamps = set()
while True:
    if smt.check() != z3.unsat:
        model = smt.model()
        ts = model[timestamp].as_long()
        tk = model[token].as_long()
        smt.add(token != tk)
        timestamps.add((ts, tk))
    else:
        break

for (ts, tk) in sorted(timestamps):
    print('%d,0x%08x' % (ts, tk))
