import re
import os
import sys
import os.path
import datetime

def makeBackDir():
    if not os.path.exists("./backTcl"):
        os.makedirs("backTcl")

def backUpFile():
    filePath['backUp'] = "./backTcl/" + sys.argv[1][:-4] \
        + datetime.datetime.now().isoformat() + sys.argv[1][-4:]
    if os.path.isfile(filePath['backUp']):
        os.remove(filePath['backUp'])
    os.rename(filePath['original'], filePath['backUp'])

def updateBlock(line):
    if '# Pass/Fail Criteria:' in line:
        lineState['currentBlock'] = '# Pass/Fail Criteria:'
    elif '# Test Steps:' in line:
        lineState['currentBlock'] = '# Test Steps:'
    elif '# Common Setup' in line:
        lineState['currentBlock'] = '# Common Setup'
    elif re.search(r'# Subtest [0-9]+:', line):
        lineState['currentBlock'] = '# Subtest'
    elif re.search(r'# Test Case Start', line):
        lineState['currentBlock'] = '# Test Case Start'
    elif re.search(r'# Description:', line):
        lineState['currentBlock'] = '# Description:'
    elif re.search(r'# Topology:', line):
        lineState['currentBlock'] = '# Topology:'

def computeCommonStep():
    with open(filePath['backUp']) as f:

        global lines
        lines = f.readlines()

        inPassCommonBlock = False
        inTestCommonBlock = False

        for line in lines:
            updateBlock(line)
            if '# Pass/Fail Criteria:' in line:
                inPassCommonBlock = True

            if '# Pass/Fail Criteria:' == lineState['currentBlock'] \
                and re.search(r'# +Variation [0-9]+:', line):
                inPassCommonBlock = False

            if '# Test Steps:' in line:
                inTestCommonBlock = True

            if '# Test Steps:' == lineState['currentBlock'] \
                and re.search(r'# +Variation [0-9]+:', line):
                inTestCommonBlock = False

            if inPassCommonBlock and re.search(r'# +[0-9]+.', line):
                stepNum['passStepCommon'] += 1
            elif inTestCommonBlock and re.search(r'# +[0-9]+.', line):
                stepNum['testStepCommon'] += 1
            elif '# Common Setup' == lineState['currentBlock'] \
                and re.search(r'# Step [0-9]+', line):
                stepNum['testCaseStepCommon'] += 1

def indentLine(line, prevIsNotEnd):

    # Replace Tab with space
    line = (tabLen * ' ').join(line.split('\t'))

    # Remove the white space both side of line
    line = line.strip()

    if line:
        if prevIsNotEnd:
            if re.search(r'[list [0-9]+ "TYPE_LINE"]', line) \
                and '-' not in line:
                line = (tabLen * (lineState['lineLayer'] + 1) \
                    + len('-layout [list ')) * ' ' + line
            else:
                line = tabLen * (lineState['lineLayer'] + 1) * ' ' + line
        else:
            if line.count('}') > line.count('{'):
                line = tabLen * (lineState['lineLayer'] - 1) * ' ' + line
            else:
                line = tabLen * lineState['lineLayer'] * ' ' + line

    return line + '\n'

def formatDescription(line):
    if re.search(r'^# +.*\..*[0-9]+', line):
        re.sub(r'\.tcl', '', line)
        words = line.split()
        line = words[0] + '     ' + words[1] + '\t' + ' '.join(words[2:-1]) \
            + '\t' + words[-1] + '\n'

    return line

def correctCriteriaLine(line):
    if re.search(r'[0-9]+:', line):
        stepNum['passStep'] = stepNum['passStepCommon']
    if re.search(r'# +[0-9]+.', line):
        stepNum['passStep'] += 1

    return re.sub(r' [0-9]+\.', ' ' + str(stepNum['passStep']) + '.', line)

def correctTestStep(line):
    if re.search(r'[0-9]+:', line):
        stepNum['testStep'] = stepNum['testStepCommon']
    if re.search(r'# +[0-9]+.', line):
        stepNum['testStep'] += 1

    return re.sub(r' [0-9]+\.', ' ' + str(stepNum['testStep']) + '.', line)

def correctStepInSwitchBlock(line):

    # Set common step in SWITCH lineState['currentBlock']
    if re.search(r'switch .+{', line):
        lineState['switchLayer'] += 1
        lineState['isInSwitchBlock'] = True
        lineState['switchStepCommon'] = lineState['testCaseStep']

    elif '{' in line \
        and lineState['isInSwitchBlock'] and lineState['switchLayer'] > 0:
        lineState['switchLayer'] += 1
        lineState['testCaseStep'] = lineState['switchStepCommon']

    elif '}' in line \
        and lineState['isInSwitchBlock'] and lineState['switchLayer'] > 0:
        lineState['switchLayer'] -= 1
        if lineState['testCaseStep'] > lineState['maxStepInBlock']:
            lineState['maxStepInBlock'] = lineState['testCaseStep']
        if 0 == lineState['switchLayer']:
            lineState['isInSwitchBlock'] = False
            lineState['testCaseStep'] = lineState['maxStepInBlock']

def correctTestCaseStep(line):

    # Correct num for "# Step 1", "logStep 1 XXX" and "logStep 1 XXX"
    if re.search(r'tep [0-9]+', line):
        if re.search(r'# Step [0-9]+', line):
            lineState['testCaseStep'] += 1

        if re.search(r'# Step [0-9]', line):
            line = re.sub(r'# Step [0-9]+', '# Step ' \
                + str(lineState['testCaseStep']), line)
        elif re.search(r'logStep [0-9]', line):
            line = re.sub(r'logStep [0-9]+', 'logStep ' \
                + str(lineState['testCaseStep']), line)

    return line

def setLineLayer(line):
    if '{' in line:
        lineState['lineLayer'] += line.count('{')

    if '}' in line:
        lineState['lineLayer'] -= line.count('}')

def creatNewFile():
    with open(sys.argv[1], "w+") as tf:

        needInsertWhiteLine = False
        prevIsNotEnd = False
        prevLineHasContent = False

        global lines
        for line in lines:

            # Indent line
            line = indentLine(line, prevIsNotEnd)

            updateBlock(line)

            if '# Pass/Fail Criteria:' == lineState['currentBlock']:
                line = correctCriteriaLine(line)
            elif '# Test Steps:' == lineState['currentBlock']:
                line = correctTestStep(line)
            else:
                correctStepInSwitchBlock(line)

                # Start step num in '#Common Steup'
                if '# Common Setup' in line:
                    lineState['testCaseStep'] = 0

                # Common Steup num proceed to Subtest num
                if '# Subtest' in line or '# Test Case Start' in line:
                    lineState['testCaseStep'] = stepNum['testCaseStepCommon']

            line = correctTestCaseStep(line)

            if re.search(r'  +#', line) \
                and needInsertWhiteLine and lineState['lineLayer']:
                tf.write('\n')

            if '# Description:' ==  lineState['currentBlock'] \
                and '# Description:' not in line:
                line = formatDescription(line)

            # Write content
            if '\n' != line or prevLineHasContent:
                tf.write(line)

            # Save last line info
            setLineLayer(line)

            # White line is '\n'
            if '\n' == line:
                prevLineHasContent = False
            else:
                prevLineHasContent = True

            needInsertWhiteLine = False

            # White line's length is 1
            if len(line) > 1:
                if not re.search(r'  +#', line):
                    needInsertWhiteLine = True

                # If line is end with 'XX \' and not begin with '#'
                if re.search(r'^(?!#)', line) and ' \\' in line \
                    and ' \\' == line[-3:-1]:
                    prevIsNotEnd = True
                else:
                    prevIsNotEnd = False

            # Remove the last white line
            if "# ;;; End: ***" in line:
                break

tabLen = 4
lines = ''

lineState = {}
lineState['lineLayer'] = 0
lineState['switchLayer'] = 0
lineState['testCaseStep'] = 0
lineState['currentBlock'] = ''
lineState['maxStepInBlock'] = 0
lineState['switchStepCommon'] = 0
lineState['isInSwitchBlock'] = False

filePath = {}
filePath['original'] = sys.argv[1]
filePath['backUp'] = ''

stepNum = {}
stepNum['passStep'] = 0
stepNum['passStepCommon'] = 0
stepNum['testStep'] = 0
stepNum['testStepCommon'] = 0
stepNum['testCaseStepCommon'] = 0

if 2 <= len(sys.argv):
    makeBackDir()

    if os.path.isfile(sys.argv[1]):
        backUpFile()
        computeCommonStep()
        creatNewFile()
        if 3 == len(sys.argv) and 'd' == sys.argv[2]:
            os.system('git diff ' + filePath['backUp'] + ' ' \
                + filePath['original'])
    else:
        print sys.argv[1] + " does not exist."
        sys.exit(0)