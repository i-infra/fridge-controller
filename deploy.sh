#! /bin/bash
set -exu
sudo chown $USER /dev/ttyUSB0
for source in $(ls *.py libs/*.py)
do pipenv run ampy -p /dev/ttyUSB0 put $source
done
