#!/bin/bash
cd `dirname $0`
here=`pwd`

##
# You can run this file directly. It is meant to be run from build.sh though.
# @author Philip Bergen

set -e

for file in *.py *.md; do
    echo "TEST "$file
    case $file in
        *.py)
            python -m doctest $file &
            ;;
        *.md)
            (python <<EOF
import doctest
doctest.testfile('$file')
EOF
) &
            ;;
        *)
            echo "Unsupported file format: $file"
            exit 1
            ;;
    esac
done
wait
