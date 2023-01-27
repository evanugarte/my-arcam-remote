#!/bin/bash
if [ ! -d "./arcam_fmj" ] 
then
  git clone --single-branch --branch non-rc5-source-optional-state https://github.com/evanugarte/arcam_fmj.git
fi

# TODO change dependency install steps for arcam_fmj
cd arcam_fmj
python3 setup.py install
cd ..
