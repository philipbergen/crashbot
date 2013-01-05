#!/bin/bash
cd `dirname $0`
here=`pwd`

##
# Calls build.sh then runs a set of bot programs against each other.
# Usage: ./run.sh <robot 1 program> [<robot 2 program> ...]
# @author Philip Bergen

if [ -z "$*" ]; then
    echo "Please specify robot programs on the command line."
    exit 1
fi

./build.sh

echo "Running Crashbots"
python crashbots.py
