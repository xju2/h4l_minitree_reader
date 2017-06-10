#!/usr/bin/env python
"""
get the yields for H4l analysis,
The samples, input minitress are encoded!
Change the function if it does fit you.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), '..')))

from h4l_minitree_reader.sample import Sample
from h4l_minitree_reader.sample import Category
from h4l_minitree_reader import helper

import ROOT
ROOT.gROOT.SetBatch()

from optparse import OptionParser
from collections import OrderedDict
from functools import reduce
import math
import re


class MinitreeReader(object):
    def __init__(self, options_):
        self.TREE_NAME = "tree_incl_all"
        self.options = options_
        self.weight_name = options_.wName

        # setup range of POI, usually it's the mass.
        self.mass_low, self.mass_hi = options_.poi_range.split(':')
        self.split_2mu2e = False
        self.DIR_BASE = "/afs/cern.ch/atlas/groups/HSG2/H4l/run2/2016/MiniTrees/"
        print "Mass window", self.mass_low, self.mass_hi

        self.category_list = []

    def get_cuts(self):
        current_ana = self.options.analysis
        m4l_ = self.options.poi

        mass_cut = "pass_vtx4lCut==1 &&"+self.mass_low+"<"+m4l_+"&&"+m4l_+"<"+self.mass_hi+"&&"
        if current_ana == "HighMass":

            if self.options.no_VBF:
                if self.options.noCombLep:
                    self.category_list.append(Category(name="2mu2e", cut=mass_cut+"event_type==2"))
                    self.category_list.append(Category(name="2e2mu", cut=mass_cut+"event_type==3"))
                else:
                    self.category_list.append(Category(name="2mu2e", cut=mass_cut+"(event_type==3 || event_type==2)"))

                self.category_list.append(Category(name="4e", cut=mass_cut+"event_type==1"))
                self.category_list.append(Category(name="4mu", cut=mass_cut+"event_type==0"))
            else:
                self.category_list.append(Category(name="4mu", cut=mass_cut+"event_type==0 && prod_type_HM==0"))
                self.category_list.append(Category(name="2mu2e", cut=mass_cut+"(event_type==3 || event_type==2) && prod_type_HM==0"))
                self.category_list.append(Category(name="4e", cut=mass_cut+"event_type==1 && prod_type_HM==0"))
                self.category_list.append(Category(name="VBF", cut=mass_cut+"prod_type_HM==1"))
        else:
            print "analysis not defined"

    def get_reducible(self):
        """return a dictionary for pre-defined background, the keys should match ones in get_cuts"""
        current_ana = self.options.analysis
        dic = OrderedDict()
        if current_ana == "HighMass":
            if self.options.no_VBF:
                dic["2mu2e"] = (7.95706, 0.2926057, 1.1205216)
                dic["4e"] = (4.48462, 0.241686, 0.789469)
                dic["4mu"] = (3.78732, 0.159662, 0.884825)
            else:
                dic["2mu2e"] = (7.77571, 0, 1.05572)
                dic["4e"] = (4.37282, 0, 0.759606)
                dic["4mu"] = (3.71372, 0, 0.808304)
                dic["VBF"] = (0.3724366, 0, 0.049943)
        else:
            print "I don't know"

        return dic

    def get_mc_dir(self):
        return self.options.mcDir if self.options.prod is None else self.DIR_BASE + self.options.prod + "/mc/Nominal/"

    def get_data_dir(self):
        return self.options.dataDir if self.options.prod is None else self.DIR_BASE + self.options.prod + \
                                                                      "/data/Nominal/"

    def get_samples(self):
        analysis = self.options.analysis
        mc_dir = self.get_mc_dir()
        print "MC dir",mc_dir
        sample_list = []
        if analysis == "HighMass":

            # qqZZ
            qq_zz = Sample("qqZZ")
            if self.options.powheg:
                # Powheg
                print "use PowHeg for qqZZ"
                qq_zz.file_list.append(mc_dir+'mc15_13TeV.361603.PowhegPy8EG_CT10nloME_AZNLOCTEQ6L1_ZZllll_mll4.root')
                qq_zz.file_list.append(mc_dir+'mc15_13TeV.342556.PowhegPy8EG_CT10nloME_AZNLOCTEQ6L1_ZZllll_mll4_m4l_100_150.root')
                qq_zz.file_list.append(mc_dir+'mc15_13TeV.343232.PowhegPy8EG_CT10nloME_AZNLOCTEQ6L1_ZZllll_mll4_m4l_500_13000.root')

            elif self.options.sherpa == 2.1:
                print "use Sherpa 2.1 for qqZZ"
                # qqZZ, Sherpa, 2.1
                qq_zz.file_list.append(mc_dir + 'mc15_13TeV.361090.Sherpa_CT10_llll_M4l100.root')
            elif self.options.sherpa == 2.2:
                print "use Sherpa 2.2 for qqZZ"
                # qqZZ, Sherpa, 2.2.2,
                qq_zz.file_list.append(mc_dir+'mc15_13TeV.363490.Sherpa_221_NNPDF30NNLO_llll.root')
                qq_zz.file_list.append(mc_dir+'mc15_13TeV.345107.Sherpa_221_NNPDF30NNLO_llll_m4l100_300_filt100_150.root')
                qq_zz.file_list.append(mc_dir+'mc15_13TeV.345108.Sherpa_221_NNPDF30NNLO_llll_m4l300.root')
                #qq_zz.scale = 1.0411

            qq_zz.sys_dic = helper.get_sys(self.options.sysDir, 'norm_qqZZ.txt')
            sample_list.append(qq_zz)

            # ggZZ
            gg_zz = Sample('ggZZ')
            gg_zz.file_list.append(mc_dir + 'mc15_13TeV.361073.Sherpa_CT10_ggllll.root')
            gg_zz.sys_dic = helper.get_sys(self.options.sysDir, 'norm_ggllll.txt')
            sample_list.append(gg_zz)

            # qqZZjj
            qq_zz_input = mc_dir + 'mc15_13TeV.361072.Sherpa_CT10_lllljj_EW6.root'
            qqZZjj = Sample('qqZZjj')
            qqZZjj.file_list.append(qq_zz_input)
            qqZZjj.sys_dic = helper.get_sys(self.options.sysDir, 'norm_qqZZEW.txt')
            if self.options.noVBS:
                print "VBS samples ignored"
            else:
                sample_list.append(qqZZjj)


            # reducible
            reducible = Sample('reducible')
            sample_list.append(reducible)

            # ttV
            ttv = Sample('ttV')
            ttv.file_list.append(mc_dir + 'mc15_13TeV.361621.Sherpa_CT10_WWZ_4l2v.root')
            ttv.file_list.append(mc_dir + 'mc15_13TeV.361623.Sherpa_CT10_WZZ_5l1v.root')
            ttv.file_list.append(mc_dir + 'mc15_13TeV.361625.Sherpa_CT10_ZZZ_6l0v.root')
            ttv.file_list.append(mc_dir + 'mc15_13TeV.361626.Sherpa_CT10_ZZZ_4l2v.root')
            ttv.file_list.append(mc_dir + 'mc15_13TeV.410144.Sherpa_NNPDF30NNLO_ttW.root')
            ttv.file_list.append(mc_dir + 'mc15_13TeV.410142.Sherpa_NNPDF30NNLO_ttll_mll5.root')
            ttv.sys_dic = helper.get_sys(self.options.sysDir, 'norm_qqZZ.txt')
            sample_list.append(ttv)

            # data
            data = Sample('data')
            data.file_list.append(self.get_data_dir()+ 'data_13TeV.root')
            data.is_data = True
            sample_list.append(data)
        else:
            print "I don't know"

        return sample_list



    @staticmethod
    def combined_sys(list_sys):
        # construct a new dictionary to save sys info
        total_exp = sum([x for x,y,z in list_sys])

        new_dic = {}
        all_sys_names = [z.keys() for x, y, z in list_sys if type(z) is dict]

        # common systematics are correlated, added linearly
        if len(all_sys_names) > 0:
            union_sys_name = reduce((lambda x, y: set(x).union(set(y))), all_sys_names)
            for sys_name in union_sys_name:
                sys_val = sum([x*z[sys_name] for x, y, z in list_sys if type(z) is dict and sys_name in z])
                new_dic[sys_name] = sys_val/total_exp

            #new_dic["ADDSYS"] = math.sqrt(sum([(z/x)**2 for x,y,z in list_sys if type(z) is not dict]))
        else:
            #new_dic["ADDSYS"] = math.sqrt(sum([(z/x)**2 for x,y,z in list_sys if type(z) is not dict]))
            #new_dic["ADDSYS"] = sum([z/x for x,y,z in list_sys if type(z) is not dict])
            new_dic =  sum([z*1.02 for x,y,z in list_sys if type(z) is not dict])

        total_stat = math.sqrt(sum([y**2 for x,y,z in list_sys]))

        return (total_exp, total_stat, new_dic)

    def get_sys_val(self, exp, sys_dic):
        if type(sys_dic) is dict:
            # print exp, sys_dic, # only for debug
            return math.sqrt(sum([(exp*y)**2 for y in sys_dic.values()]))
        else:
            return sys_dic

    def get_str(self, nominal, stats, sys):
        """
        return a str: "10 $\pm$ 10 $\pm$ 10"
        """
        split_sys = self.options.split
        dd = self.options.digits
        if split_sys:
            res = str(round(nominal, dd))+' $\pm$ '+str(round(stats, dd))+' $\pm$ '+str(round(sys,dd))
        else:
            total_ = math.sqrt(stats**2 + sys**2)
            res = str(round(nominal, dd))+' $\pm$ '+str(round(total_, dd))

        return res

    def combine_samples(self, samples, name):
        combined = Sample(name)
        for category in self.category_list:
            combined.yields[category.name] = self.combined_sys(map(lambda x: x.yields[category.name], samples))

        return combined

    def print_list(self, samples):
        out_text = ""
        ic = 0
        for sample in samples:
            if ic == 0:
                out_text += sample.name
            else:
                out_text += " & " + sample.name
            ic += 1

        out_text += " \\\\ \\hline \n"

        for category in self.category_list:
            ch_name = category.name
            out_text += ch_name

            for sample in samples:
                if self.options.debug:
                    print "IN sample: ", sample.name, ch_name

                exp_, stat_, sys_dic_ = sample.yields[ch_name]

                if 'data' in sample.name:
                    out_text += ' & ' + str(exp_)
                else:
                    sys_ = self.get_sys_val(exp_, sys_dic_)
                    out_text += ' & ' + self.get_str(exp_, stat_, sys_)

            out_text += " \\\\ \n"


        out_text += "Total"
        for sample in samples:
            list_sys = []
            for category in self.category_list:
                list_sys.append(sample.yields[category.name])

            total_exp, total_stat, total_sys_dic = self.combined_sys(list_sys)
            total_sys = self.get_sys_val(total_exp, total_sys_dic)

            if "data" in sample.name:
                out_text += ' & '+ str(total_exp)
            else:
                out_text += ' & '+self.get_str(total_exp, total_stat, total_sys)

        out_text += " \\\\ \\hline \n"
        print out_text

    def print_list_paper(self, samples):
        out_text = ""
        ic = 0
        for category in self.category_list:
            if ic == 0:
                out_text += category.name
            else:
                out_text += " & " + category.name
            ic += 1

        out_text += " \\\\ \\hline \n"

        for sample in samples:
            out_text += sample.name

            for category in self.category_list:
                ch_name = category.name

                exp_, stat_, sys_dic_ = sample.yields[ch_name]

                if 'data' in sample.name:
                    out_text += ' & ' + str(exp_)
                else:
                    sys_ = self.get_sys_val(exp_, sys_dic_)
                    out_text += ' & ' + self.get_str(exp_, stat_, sys_)

            out_text += " \\\\ \n"
        print out_text

    def process(self):
        self.get_cuts()
        all_samples = self.get_samples()

        # get yields for each sample for each category
        # save the information in a 2-D list:
        # all_res[channel][sample] = (exp, stats, sys_dic)
        if len(self.category_list) > 0 and len(all_samples) > 0:
            for category in self.category_list:
                for sample in all_samples:
                    if "reducible" not in sample.name:
                        sample.get_yield(category, options)
                    else:
                        sample.yields = self.get_reducible()

        new_samples = []
        if self.options.comb_zz:
            index = 2 if (self.options.noVBS or self.options.spVBS) else 3
            combined = self.combine_samples(all_samples[0:index], "combinedZZ")
            new_samples.append(combined)
            new_samples += all_samples[index:-1]
        else:
            new_samples += all_samples[:-1]

        new_samples.append(self.combine_samples(all_samples[0:-1], "expected"))
        new_samples.append(all_samples[-1])

        if self.options.paper:
            self.print_list_paper(new_samples)
        else:
            self.print_list(new_samples)


if __name__ == "__main__":
    usage = "%prog [options]"
    version="%prog 1.1"
    parser = OptionParser(usage=usage, description="get yields for WS", version=version)
    parser.add_option("--analysis", dest='analysis', default='HighMass',
                      help='which analysis, affecting the built-in cuts')

    parser.add_option("--poi", dest='poi', default='m4l_constrained_HM',
                      help='which variable used for counting')
    parser.add_option("--poiRange", dest='poi_range', default='130:1500',
                      help='range of POI')
    parser.add_option("-w", '--weightName', dest='wName', default='weight_jet', help="Name of weights")

    parser.add_option("--mcDir", dest='mcDir',
                      default='/afs/cern.ch/atlas/groups/HSG2/H4l/run2/2016/MiniTrees/Prod_v10/mc/Nominal/',
                      help="directory for MC")
    parser.add_option("--dataDir", dest='dataDir',
                      default='/afs/cern.ch/atlas/groups/HSG2/H4l/run2/2016/MiniTrees/Prod_v10/data/Nominal/',
                      help="directory for data")
    parser.add_option("--sysDir", dest='sysDir', help="directory for data",
                      default="/Users/xju/Documents/Higgs/H4l/highmass/yields/")
    parser.add_option("--prod", dest='prod', default=None, help="Use production")

    parser.add_option("--lumi", dest='lumi', default=-1, type='float',
                      help='final luminosity')
    parser.add_option("--digits", dest='digits', default=2, type='int',
                      help="digits in final numbers")
    parser.add_option("--split", dest='split', default=False, action='store_true',
                      help="split stats and sys")
    parser.add_option("--noCombLep", dest='noCombLep', default=False,
                      help="not combine 2mu2e with 2e2mu", action='store_true')
    parser.add_option("--combZZ", dest='comb_zz', default=False,
                      help="combine qq/gg/qqjj", action='store_true')

    parser.add_option("--test", dest='test', default=False, action='store_true', help="no VBF in highmass")

    # change qqZZ samples
    parser.add_option("--powheg", dest='powheg', default=False, action='store_true', help="use PowHeg for qqZZ")
    parser.add_option("--sherpa", dest='sherpa', default=2.2, type='float', help="Sherpa version")

    # no VBF-like category in HighMass
    parser.add_option("--noVBF", dest='no_VBF', default=False, action='store_true', help="no VBF-like category")
    # no VBS samples in HighMass
    parser.add_option("--noVBS", dest='noVBS', default=False, action='store_true', help="no VBS events")
    # separate VBS samples in yields
    parser.add_option("--spVBS", default=False, action='store_true', help="separate VBS events")

    parser.add_option("-v","--verbose", dest='debug', default=False, help="in a debug mode", action='store_true')
    parser.add_option("--paper", dest='paper', default=False, help="paper style", action='store_true')

    parser.add_option("--histOut", default="hist_yields.root", help="root file for histograms")

    (options, args) = parser.parse_args()

    reader = MinitreeReader(options)
    reader.process()
