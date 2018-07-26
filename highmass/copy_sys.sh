#!/bin/bash

base_dir=/afs/cern.ch/work/s/svonbudd/public/HZZ/June2019Unblinding/Systematics
mc_tag=mc16d

if [ ! -d $mc_tag ]; then
    mkdir ${mc_tag}
fi

cp ${base_dir}/$mc_tag/norm_qqZZ.txt ${mc_tag}/
cp ${base_dir}/$mc_tag/norm_qqZZjj.txt ${mc_tag}/norm_qqZZEW.txt
cp ${base_dir}/$mc_tag/norm_ggZZ.txt ${mc_tag}/norm_ggllll.txt
