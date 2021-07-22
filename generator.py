#!/usr/bin/env python3
from time import sleep
#file to read from
filename = 'filename'
#seconds to wait between each tweet
seconds = 86400

for line in open(filename):
    sleep(seconds)
    print(line.rstrip())
