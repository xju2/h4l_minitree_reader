#!/bin/bash

#setup gcc
PATH="/afs/cern.ch/sw/lcg/contrib/gcc/4.9.3/x86_64-slc6/bin:$PATH"
LD_LIBRARY_PATH="/afs/cern.ch/sw/lcg/contrib/gcc/4.9.3/x86_64-slc6/lib64:$LD_LIBRARY_PATH"

# setup python
source /afs/cern.ch/work/x/xju/public/miniconda3/bin/activate py2.7

# setup ROOT
RootDir=/afs/cern.ch/atlas/project/HSG7/root/root_v6-04-02/x86_64-slc6-gcc49/
cd $RootDir
source bin/thisroot.sh
cd -
