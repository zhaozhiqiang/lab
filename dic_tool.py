import re
import os
import sys
import os.path

with open(sys.argv[1]) as old:
    oLines = old.readlines()
with open(sys.argv[2]) as new:
    newLines = new.readlines()
with open('target', 'w+') as target:
    nu = 1
    for line in newLines:
        if r'<CustomizeListItem word=' in line:
            for oLine in oLines:
                if re.search(r'<CustomizeListItem word="[A-z]+"', line):
                    word = re.search(r'<CustomizeListItem word="[A-z]+"', line).group(0)
                    if word in oLine:
                        line = oLine
                        line = re.sub(r' localTimestamp="[0-9]+T[0-9]+" ', ' localTimestamp="20160407T230218" ', line)
                        line = re.sub(r' serverTimestamp="[0-9]+T[0-9]+" ', ' serverTimestamp="20160407T230218" ', line)
                        break
        target.write(line)
        print nu
        nu += 1