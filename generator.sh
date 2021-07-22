#!/bin/bash
#file to read from
file="filename"
#seconds to wait between each tweet
seconds=86400
while IFS= read -r line; do
	sleep $seconds
	echo $line | sed -e 's/[[:space:]]*$//'
done < $file
