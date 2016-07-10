#!/bin/bash -
#

if test -n "$TRAVIS"
then
	echo "Skip in travis"
fi

export PYTHONPATH=$PWD:$PYTHONPATH
python tests/test_client.py
