#!/usr/bin/env python
import subprocess
import time
import shlex

INTERVAL = 2

while True:
    if '2560' in subprocess.check_output(shlex.split('dconf read
/com/ubuntu/user-interface/scale-factor')):
        subprocess.check_output(shlex.split(('dconf write
/com/ubuntu/user-interface/scale-factor "{\'VGA-1\': 12}"')))
    else:
        subprocess.check_output(shlex.split(('dconf write
/com/ubuntu/user-interface/scale-factor "{\'VGA-1\': 8}"')))
    time.sleep(INTERVAL)

-------------------------------------------------------------------------------
import subprocess
 
cmd = ['xrandr']
cmd2 = ['grep', '*']
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=subprocess.PIPE)
p.stdout.close()
 
resolution_string, junk = p2.communicate()
resolution = resolution_string.split()[0]
width, height = resolution.split('x')


-------------------------------------------------------------------------------
xdpyinfo  | grep -oP 'dimensions:\s+\K\S+'