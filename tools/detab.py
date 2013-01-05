#!/usr/bin/env python
import sys
for line in sys.stdin.read():
    sys.stdout.write(line.replace('\t', '    '))
