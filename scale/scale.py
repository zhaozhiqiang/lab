#!/usr/bin/env python
import subprocess
import time
import shlex
import re
import os

INTERVAL = 2
PATTERN = re.compile(r'dimensions:\s*(?P<res>\d+x\d+)\spixels')
SCALE_FACTOR = '/com/ubuntu/user-interface/scale-factor'
MAP = {'2560x1267': 12,
       '2560x1331': 12,
       '2560x1440': 12,
       '1680x941': 8}


def getCurrentResolution():
    xdpyinfo = subprocess.check_output('xdpyinfo')
    return PATTERN.search(xdpyinfo).group('res')


def setScale(scale):
    if str(scale) not in subprocess.check_output(shlex.split('dconf read '
+ SCALE_FACTOR)):
        subprocess.check_output(shlex.split(('dconf write ' + SCALE_FACTOR
+ ' "{\'VGA-1\': %d}"') % scale))


def main():
    while True:
        setScale(MAP.get(getCurrentResolution(), 8))
        time.sleep(INTERVAL)


try:
    pid = os.fork()
 
    if pid == 0:
        main()
    else:
        print "Started"
 
except OSError, e:
    pass
