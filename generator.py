#!/usr/bin/env python3
from time import sleep
from sys import stdout
#file to read from
filename = 'filename'
#seconds to wait between each tweet
seconds = 86400

for line in open(filename):
    print(line.rstrip()+'\f')
    stdout.flush()
    sleep(seconds)
