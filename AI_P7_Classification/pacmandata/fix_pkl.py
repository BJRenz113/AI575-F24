#!/usr/bin/env python
"""
convert dos linefeeds (crlf) to unix (lf)
usage: dos2unix.py
"""

import os



for file in os.listdir("."):
    if ".pkl" in file:
        print("file:", file)
        original = file
        destination =  file[:-4]+"_old.pkl"

        content = ''
        outsize = 0
        with open(original, 'rb') as infile:
            content = infile.read()

        with open(destination, 'wb') as outfile:
            outfile.write(content)

        with open(original, 'wb') as output:
            for line in content.splitlines():
                outsize += len(line) + 1
                output.write(line + str.encode('\n'))

        print(f"Done {file}. Saved {len(content)-outsize} bytes.")
