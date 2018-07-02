#!/usr/bin/env python

import ROOT
import os
ROOT.SetBatch(True)

mini_dir = "/eos/atlas/atlascerngroupdisk/phys-higgs/HSG2/H4l/2018/MiniTrees/Prod_v18/mc16a/Nominal"
file_list = [
    "mc16_13TeV.364250.Sherpa_222_NNPDF30NNLO_llll.root",
    "mc16_13TeV.364251.Sherpa_222_NNPDF30NNLO_llll_m4l100_300_filt100_150.root",
    "mc16_13TeV.364252.Sherpa_222_NNPDF30NNLO_llll_m4l300.root"
]

tree_name = "tree_incl_all"
chain = ROOT.TChain(tree_name, tree_name)
map(lambda x: chain.Add(os.path.join(mini_dir, x)), file_list)

h_4e = ROOT.TH1F("m4l_ggF_4e_13TeV", "m4l_ggF_4e_13TeV", 600, 130, 1500)
chain.Draw("m4l_constrained_HM>>m4l_ggF_4e_13TeV", "weight*(event_type == 1)")

out = ROOT.TFile.Open("nominal_qqZZ.root", 'recreate')
h_4e.Write()
out.Close()

