import re
import os
import sys

if 2 == len(sys.argv):
    # Walking every path
    for dirname, dirnames, filenames in os.walk(sys.argv[1]):
        captions = [""]
        videos = []

        for filename in filenames:
            if re.search(r'.ass', filename) or re.search(r'.srt', filename):
                captions.append(filename)
            elif re.search(r'.mkv', filename):
                videos.append(filename)

        # Rename captions
        for caption in captions:
            se = "".join(re.findall(r'S[0-9][0-9]E[0-9][0-9]', caption))
            for video in videos:
                if "" != se and re.search(str(se), video):
                    os.rename(os.path.join(dirname, caption), dirname + "\\" + video[:-4] + caption[-4:])