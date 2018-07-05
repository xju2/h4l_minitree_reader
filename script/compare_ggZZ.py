#!/usr/bin/env python
import os
import sys

import ROOT
ROOT.gROOT.SetBatch()

sys.path.insert(0, '/afs/cern.ch/user/x/xju/work/h4l/h4lcode/root_plot_utils')
from root_plot_utils import AtlasStyle

from root_plot_utils.ploter import Ploter
ps = Ploter("Internal", 36.1)

base_dir = '/eos/atlas/atlascerngroupdisk/phys-higgs/HSG2/H4l/2018/MiniTrees/Prod_v18/mc16a/Nominal'

powheg_files = [
    "mc16_13TeV.343212.Powheggg2vvPythia8EvtGen_gg_ZZ_bkg_2e2mu_13TeV.root",
    "mc16_13TeV.343213.Powheggg2vvPythia8EvtGen_gg_ZZ_bkg_4l_noTau_13TeV.root"
]
sherpa_files = [
    'mc16_13TeV.345709.Sherpa_222_NNPDF30NNLO_ggllllNoHiggs_130M4l_AFii_.root'
]
sherpa2_files = [
    '/afs/cern.ch/atlas/groups/HSG2/H4l/run2/2016/MiniTrees/Prod_v12/mc/Nominal/mc15_13TeV.361075.Sherpa_CT10_ggllllNoHiggs.root'
]

tree_name = 'tree_incl_all'

ch_powheg =  ROOT.TChain(tree_name, tree_name)
map(lambda x: ch_powheg.Add(os.path.join(base_dir, x)), powheg_files)

ch_sherpa =  ROOT.TChain(tree_name, tree_name)
map(lambda x: ch_sherpa.Add(os.path.join(base_dir, x)), sherpa_files)

ch_sherpa2 =  ROOT.TChain(tree_name, tree_name)
map(lambda x: ch_sherpa2.Add(x), sherpa2_files)


h_incl_powheg = ROOT.TH1F("powheg", "powheg", 100, 130, 1500)
h_incl_sherpa = ROOT.TH1F("sherpa", "sherpa;m_{4l} [GeV];Events/12 GeV", 100, 130, 1500)
h_incl_sherpa2 = ROOT.TH1F("sherpa2", "sherpa2;m_{4l} [GeV];Events/12 GeV", 100, 130, 1500)

cuts = 'weight*36.1/w_lumi*(pass_vtx4lCut==1 && m4l_constrained_HM > 130 && m4l_constrained_HM < 1500)'
ch_powheg.Draw("m4l_constrained_HM>>powheg", cuts)
ch_sherpa.Draw("m4l_constrained_HM>>sherpa", cuts)
ch_sherpa2.Draw("m4l_constrained_HM>>sherpa2", cuts)

ps.compare_hists([h_incl_sherpa, h_incl_powheg], ['Sherpa', 'PowHeg'],
                 **{"add_yields":True,
                    "add_ratio": True,
                    'no_fill': True,
                    'out_name': 'ggZZ_cmp',
                    'ratio_range': (0.5, 3),
                    'ratio_title': 'PowHeg/Sherpa'
                   })

ps.compare_hists([h_incl_sherpa2, h_incl_sherpa, h_incl_powheg], ['MC15 Sherpa', 'MC16a Sherpa', 'MC16a PowHeg'],
                 **{"add_yields":True,
                    "add_ratio": True,
                    'no_fill': True,
                    'out_name': 'ggZZ_cmp_mc15_mc16',
                    'ratio_range': (0.4, 1.5),
                    'ratio_title': 'others/MC15-Sherpa'
                   })

def norm(x):
    x.Scale(1./x.Integral())

norm(h_incl_sherpa)
norm(h_incl_powheg)
norm(h_incl_sherpa2)

ps.compare_hists([h_incl_sherpa, h_incl_powheg], ['Sherpa', 'PowHeg'],
                 **{"add_yields":True,
                    "add_ratio": True,
                    'no_fill': True,
                    'out_name': 'ggZZ_cmp_shape',
                    'ratio_range': (0.5, 1.5),
                    'ratio_title': 'PowHeg/Sherpa'
                   })

ps.compare_hists([h_incl_sherpa2, h_incl_sherpa, h_incl_powheg], ['MC15 Sherpa', 'MC16a Sherpa', 'MC16a PowHeg'],
                 **{"add_yields":False,
                    "add_ratio": True,
                    'no_fill': True,
                    'out_name': 'ggZZ_cmp_mc15_mc16_shape',
                    'ratio_range': (0.4, 1.5),
                    'ratio_title': 'others/MC15-Sherpa'
                   })
