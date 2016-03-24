#!/bin/bash
if [[ $ == 0 ]]; then
for d in */; do
    echo $d
    cd $d
    git fetch
    git pull
    cd ..
done
else
    for d in "$@"; do
      echo $d
      cd $d
      git fetch
      git pull
      cd ..
    done
fi
