#!/bin/bash -
#

if test -n "$TRAVIS"
then
	echo "Skip in travis"
fi

python tests/test_client.py
