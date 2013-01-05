#!/bin/bash
cd `dirname $0`
here=`pwd`

##
# You can run this file directly. It is meant to be run from build.sh though.
# @author Philip Bergen

for file in *.py; do
    echo "TEST "$file
    python -m doctest $file
done

ls *.md >/dev/null 2>&1 && for file in *.md; do
    python <<EOF
import doctest
print "TEST $file"
doctest.testfile('$file')
EOF
done
