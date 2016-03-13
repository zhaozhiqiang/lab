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
    passStep = 0
    passStepCommon = 0
    commonBlock = False
    testStep = 0
    testStepCommon = 0
    testCaseStep = 0
    testCaseStepCommon = 0
    block = ''
    lines = ''

    # Set common step num
    with open(backPath) as f:
        lines = f.readlines()
        for line in lines:
            if '# Pass/Fail Criteria:' in line:
                commonBlock = True
                block = '# Pass/Fail Criteria:'
            elif '# Test Steps:' in line:
                commonBlock = True
                block = '# Test Steps:'
            elif '# Common Setup' in line:
                block = '# Common Setup'
            elif re.search(r'# +Variation [0-9]+:', line):
                block = ''

            if re.search(r'[0-9]+:', line):
                commonBlock = False

            if '# Pass/Fail Criteria:' == block and re.search(r'# +[0-9]+.', line) and True == commonBlock:
                passStepCommon += 1
                print 'passStepCommon'
            elif '# Test Steps:' == block and re.search(r'# +[0-9]+.', line) and True == commonBlock:
                testStepCommon += 1
                print 'testStepCommon'
            elif '# Common Setup' == block and re.search(r'# Step [0-9]+', line):
                testCaseStepCommon += 1

    # Set correct step num
    with open(sys.argv[1], "w+") as tf:
        for line in lines:
            if '# Common Setup' in line:
                testCaseStep = 0

            # Remove the white space at the end of line
            line = line.rstrip() + '\n'

            if '# Pass/Fail Criteria:' in line:
                block = '# Pass/Fail Criteria:'
            elif '# Test Steps:' in line:
                block = '# Test Steps:'
            elif '# Common Setup' in line:
                block = '# Common Setup'
            elif re.search(r'# Subtest [0-9]+:', line):
                block = '# Subtest'
                testCaseStep = testCaseStepCommon

            if '# Pass/Fail Criteria:' == block:
                if re.search(r'[0-9]+:', line):
                    passStep = passStepCommon
                if re.search(r'# +[0-9]+.', line):
                    passStep += 1
                tf.write(re.sub(r' [0-9]+\.', ' ' + str(passStep) + '.', line))

            elif '# Test Steps:' == block:
                if re.search(r'[0-9]+:', line):
                    testStep = testStepCommon
                if re.search(r'# +[0-9]+.', line):
                    testStep += 1
                tf.write(re.sub(r' [0-9]+\.', ' ' + str(testStep) + '.', line))


            # Select num from "# Step 1" or "logStep 1 XXX" or "logStep 1 XXX"
            elif re.search(r'tep [0-9]+', line):
                if re.search(r'# Step [0-9]+', line):
                    testCaseStep += 1

                if re.search(r'# Step [0-9]', line):
                    tf.write(re.sub(r'# Step [0-9]+', '# Step ' + str(testCaseStep), line))
                elif re.search(r'logStep [0-9]', line):
                    tf.write(re.sub(r'logStep [0-9]+', 'logStep ' + str(testCaseStep), line))
                else:
                    tf.write(line)
            else:
                tf.write(line)

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