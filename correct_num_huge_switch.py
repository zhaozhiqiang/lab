import re
import os
import sys
import os.path
import datetime

def makeBackDir():
    if not os.path.exists("./backTcl"):
        os.makedirs("backTcl")

def backUpFile():
    filePath['backUp'] = "./backTcl/" + sys.argv[1][:-4] + datetime.datetime.now().isoformat() + sys.argv[1][-4:]
    if os.path.isfile(filePath['backUp']):
        os.remove(filePath['backUp'])
    os.rename(filePath['original'], filePath['backUp'])

def compute():
    with open(filePath['backUp']) as f:

        block = ''
        commonBlock = False
        global lines
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
                stepNum['passStepCommon'] += 1
            elif '# Test Steps:' == block and re.search(r'# +[0-9]+.', line) and True == commonBlock:
                stepNum['testStepCommon'] += 1
            elif '# Common Setup' == block and re.search(r'# Step [0-9]+', line):
                stepNum['testCaseStepCommon'] += 1

def creatNewFile():
    with open(sys.argv[1], "w+") as tf:

        block = ''
        layer = 0
        passStep = 0
        testStep = 0
        testCaseStep = 0
        isSwitchBlock = False
        switchStepCommon = 0
        maxStepInBlock = 0

        global lines
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
                testCaseStep = stepNum['testCaseStepCommon']

            if '# Pass/Fail Criteria:' == block:
                if re.search(r'[0-9]+:', line):
                    passStep = stepNum['passStepCommon']
                if re.search(r'# +[0-9]+.', line):
                    passStep += 1
                tf.write(re.sub(r' [0-9]+\.', ' ' + str(passStep) + '.', line))

            elif '# Test Steps:' == block:
                if re.search(r'[0-9]+:', line):
                    testStep = stepNum['testStepCommon']
                if re.search(r'# +[0-9]+.', line):
                    testStep += 1
                tf.write(re.sub(r' [0-9]+\.', ' ' + str(testStep) + '.', line))

            else:
                # Set common step in SWITCH block
                if re.search(r'switch .+{', line):
                    layer += 1
                    isSwitchBlock = True
                    switchStepCommon = testCaseStep

                elif isSwitchBlock and layer > 0 and '{' in line:
                    layer += 1
                    testCaseStep = switchStepCommon

                elif isSwitchBlock and layer > 0 and '}' in line:
                    layer -= 1
                    if testCaseStep > maxStepInBlock:
                        maxStepInBlock = testCaseStep
                    if 0 == layer:
                        isSwitchBlock = False
                        testCaseStep = maxStepInBlock

                # Select num from "# Step 1" or "logStep 1 XXX" or "logStep 1 XXX"
                if re.search(r'tep [0-9]+', line):
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

            # Remove the last white line
            if "# ;;; End: ***" in line:
                break

lines = ''

filePath = {}
filePath['original'] = sys.argv[1]
filePath['backUp'] = ''

stepNum = {}
stepNum['passStepCommon'] = 0
stepNum['testStepCommon'] = 0
stepNum['testCaseStepCommon'] = 0

if 2 <= len(sys.argv):
    makeBackDir()

    if os.path.isfile(sys.argv[1]):
        backUpFile()
        compute()
        creatNewFile()
        if 3 == len(sys.argv) and 'd' == sys.argv[2]:
                os.system('git diff ' + filePath['backUp'] + ' ' + filePath['original'])
    else:
        print sys.argv[1] + "does not exist."
        sys.exit(0)
