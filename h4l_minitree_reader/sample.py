# -*- coding: utf-8 -*-

import os
from collections import namedtuple

Category = namedtuple("Category", 'name cut')

import ROOT
import math
class Sample(object):
    def __init__(self, name):
        self.name = name
        self.file_list = []
        self.sys_dic = {}
        self.scale = 1.0
        self.yields = {}
        self.is_data = False
        self.TREE_NAME = "tree_incl_all"

    def get_hist_name(self, category):
        return "{}_{}".format(self.name, category.name)

    def get_yield(self, category, options):
        """get yields in each category
        : type category : namedtuple("Category", 'name cut')
        : rtype : TH1F
        """

        if not self.is_data:
            try:
                sys_ = self.sys_dic[category.name]
            except KeyError:
                print self.name,"no systematics?"
                sys_ = 0
            except TypeError:
                print self.name,"no systematic dictionary"
                sys_ = 0
        else:
            sys_ = 0

        hist = None
        if os.path.exists(options.histOut) and not options.new:
            fout = ROOT.TFile.Open(options.histOut)
            hist = fout.Get(self.get_hist_name(category))

        if not hist:
            hist = self.create_hist(category, options)
            if options.new:
                fout = ROOT.TFile.Open(options.histOut, 'recreate')
            else:
                fout = ROOT.TFile.Open(options.histOut, 'UPDATE')
            hist.Write()
            fout.Close()

        exp_ = hist.Integral() * self.scale
        try:
            stats_error = exp_/math.sqrt(hist.GetEntries())
        except ZeroDivisionError:
            stats_error = 0

        self.yields[category.name] = (exp_, stats_error, sys_)
        del hist

    def create_hist(self, category, options):
        tree = ROOT.TChain(self.TREE_NAME, self.TREE_NAME)
        w_name = options.wName

        for file_ in self.file_list:
            tree.Add(file_)

        cut = category.cut
        if self.is_data:
            # add weight in data,
            # because sometimes event can pass selections via new pairing, which only used in coupling
            cut_t = ROOT.TCut(w_name+"*("+cut+")")
        else:
            if options.lumi > 0:
                lumi = options.lumi
            else:
                tree.GetEntry(0)
                lumi = tree.w_lumi

            cut_t = ROOT.TCut(w_name+"/w_lumi*"+str(lumi)+"*("+cut+")")

        hist_name = self.get_hist_name(category)
        tree.Draw(options.poi+">>"+hist_name, cut_t)
        hist = ROOT.gDirectory.Get(hist_name)
        hist.SetDirectory(0)
        return hist
