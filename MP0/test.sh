#!/usr/bin/env bash

set -o pipefail
set -o errexit
set -o xtrace

sleep 10 && python3 -u generator.py 1 10 | python3 node.py A 127.0.0.1 8080 &
sleep 10 && python3 -u generator.py 1 10 | python3 node.py B 127.0.0.1 8080 &
sleep 10 && python3 -u generator.py 2 10 | python3 node.py C 127.0.0.1 8080 &

python3 -u logger.py 8080 > history.log
