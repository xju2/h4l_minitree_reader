#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), '..')))

from h4l_minitree_reader.sample import Sample
from h4l_minitree_reader.sample import Category

from h4l_minitree_reader import helper

from collections import namedtuple
Option = namedtuple("Option", 'wName lumi poi')

import ROOT

gg_zz = Sample('ggZZ')

mc_dir = "/afs/cern.ch/atlas/groups/HSG2/H4l/run2/2016/MiniTrees/Prod_v12/mc/Nominal/"
gg_zz.file_list.append(mc_dir + 'mc15_13TeV.361073.Sherpa_CT10_ggllll.root')

gg_zz.sys_dic = helper.get_sys('.', 'norm_ggllll.txt')

options = Option(wName="weight", lumi=36.1, poi="m4l_constrained_HM")

mass_cut = "pass_vtx4lCut==1 && 200 < "+options.poi+"&&"+options.poi+"< 1500 && "
category = Category(name="2mu2e", cut=mass_cut+"event_type==2")

gg_zz.get_yield(category, options)
print gg_zz.yields[category.name]
