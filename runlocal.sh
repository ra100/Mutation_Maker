#!/bin/bash

set -Eeuo pipefail

trap "exit" INT TERM ERR
trap "kill -9 0" EXIT

pids=""
make run-worker & pids="$pids $!"
make run-monitor & pids="$pids $!"
make run-frontend & pids="$pids $!"
make run-api & pids="$pids $!"
#make run-lambda & pids="$pids $!"

while [[ ! -z "$pids" ]]; do \
        for pid in $pids; do \
                kill -0 "$pid" 2>/dev/null || exit 1
        done
        sleep 1
done
