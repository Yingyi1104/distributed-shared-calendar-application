#!/usr/bin/env bash


# uncomment the next line if you want to remove the existing bin directory before building
rm -rf bin
mkdir bin



# copy python files from src to bin
cp -R src/  bin/


cp run.sh bin/

echo Done!

exit 0