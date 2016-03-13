import re
import os
import sys
import os.path
import datetime

def makeBackDir():
    if not os.path.exists("./backTcl"):
        os.makedirs("backTcl")

def backUpFile():
    backPath = "./backTcl/" + sys.argv[1][:-4] + datetime.datetime.now().isoformat() + sys.argv[1][-4:]
    if os.path.isfile(backPath):
        os.remove(backPath)
    os.rename(sys.argv[1], backPath)
    return backPath

def correctNum(backPath):
    step = 0

    f = open(backPath, "r")
    tf = open(sys.argv[1], "w")

    for line in f.readlines():
        # Remove the white space at the end of line
        line = line.rstrip() + '\n'

        # Reset step num is 0 when enter into a new block
        if re.search(r'# Pass/Fail Criteria:|# Test Steps:|# Common Setup|#     After step ', line):
            step = 0

        # Select num from "#     1. XXX"
        if re.search(r'#     [0-9]*\.', line):
            step += 1
            tf.write(re.sub(r' [0-9]*\.', ' ' + str(step) + '.', line))

            # Skip next tf.write, or this line will been written twice
            continue

        # Select num from "# Step 1" or "logStep 1 XXX" or "logStep 1 XXX"
        if re.search(r'tep [0-9]*', line):
            if re.search(r'# Step [0-9]*', line):
                step += 1

            if re.search(r'# Step [0-9]', line):
                tf.write(re.sub(r'# Step [0-9]*', '# Step ' + str(step), line))
                continue

            if re.search(r'logStep [0-9]', line):
                tf.write(re.sub(r'logStep [0-9]*', 'logStep ' + str(step), line))
                continue

        tf.write(line)

        # Remove the last white line
        if "# ;;; End: ***" in line:
            break

    f.close()
    tf.close()

if 2 <= len(sys.argv):
    makeBackDir()

    if os.path.isfile(sys.argv[1]):
        backPath = backUpFile()
        correctNum(backPath)
        if 3 == len(sys.argv) and 'd' == sys.argv[2]:
                os.system('git diff ' + backPath + ' ' + sys.argv[1])
    else:
        print sys.argv[1] + "does not exist."
        sys.exit(0)