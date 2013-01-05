#!/bin/bash
cd `dirname $0`
here=`pwd`

##
# Builds and tests the source, getting ready to run.
# @author Philip Bergen

for file in *.py; do
    grep -q '	' $file && if [ true ]; then
	echo "Converting tabs in $file"
        cp $file{,.bak}
        cat $file.bak | ../tools/detab.py > $file
        rm $file.bak
    fi
done

./test.sh
