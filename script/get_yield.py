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


import json


class MinitreeReader(object):
    def __init__(self, options_):
        self.TREE_NAME = "tree_incl_all"
        self.options = options_
        self.weight_name = options_.wName

        # setup range of POI, usually it's the mass.
        self.mass_low, self.mass_hi = options_.poi_range.split(':')
        self.split_2mu2e = False
        self.DIR_BASE = options_.base
        print "Mass window", self.mass_low, self.mass_hi

        self.category_list = []

    def readInputJson(self, json_file):
        data = json.load(open(json_file))

        self.read_categories(data['categories'])
        self.get_samples(data['samples' ])

    def read_categories(self, json_file):
        data = json.load(open(json_file))

        m4l_ = self.options.poi
        mass_cut = "pass_vtx4lCut==1 &&"+self.mass_low+"<"+m4l_+"&&"+m4l_+"<"+self.mass_hi+"&&"
        for name,cut in data.iteritems():
            cut = mass_cut+cut 
            self.category_list.append(Category(name=name, cut=cut))


    def read_reducible(self):
        data = json.load(open(self.reducible_bkg_input))
        def_lumi =  data['lumi']

        if len(data['yields'].keys()) != len(self.category_list):
            raise Exception("categories in reducible background do not match!")

        if self.options.lumi > 0:
            weight = self.options.lumi/def_lumi
        else:
            weight = 1.

        scaled_res = {}
        for key, value in data['yields'].iteritems():
            scaled_res[key] = [x*weight for x in value]

        return scaled_res

    def get_mc_dir(self):
        return os.path.join(self.DIR_BASE, self.options.mcDir) if self.DIR_BASE is not None else self.options.mcDir

    def get_data_dir(self):
        return os.path.join(self.DIR_BASE, self.options.dataDir) if self.DIR_BASE is not None else self.options.dataDir

    def get_samples(self, json_file):
        input_ =  json.load(open(json_file), object_pairs_hook=OrderedDict)
        mc_dir = self.get_mc_dir()
        print "MC dir",mc_dir
        self.sample_list = []
        data = None
        for name, value in input_.iteritems():
            print "#####",name
            if "data" in name:
                # data
                data = Sample('data')
                data.file_list.append(os.path.join(self.get_data_dir(), value))
                data.is_data = True
            else:
                sample =  Sample(name)
                if "reducible" == name:
                    self.reducible_bkg_input = value
                    self.sample_list.append(sample)
                    continue
                sample.file_list = [os.path.join(self.get_mc_dir(), x) for x in value["files"]]
                sample.sys_dic = helper.get_sys(os.path.join(self.options.sysDir, value['sys']))
                self.sample_list.append(sample)

        self.sample_list.append(data)

    @staticmethod
    def combined_sys(list_sys):
        # construct a new dictionary to save sys info
        # x is expected, y is stats_error, z is the list for sys
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
        all_samples = self.sample_list

        # get yields for each sample for each category
        # save the information in a 2-D list:
        # all_res[channel][sample] = (exp, stats, sys_dic)
        if len(self.category_list) > 0 and len(all_samples) > 0:
            for category in self.category_list:
                for sample in all_samples:
                    if "reducible" not in sample.name:
                        sample.get_yield(category, options)
                    else:
                        sample.yields = self.read_reducible()

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
    usage = "%prog [options] minitree.json"
    version="%prog 1.1"
    parser = OptionParser(usage=usage, description="get yields for WS", version=version)

    parser.add_option("--base", default=None, help="base dir for inputs")
    parser.add_option("--mcDir", default='mc/Nominal',
                      help="directory for MC")
    parser.add_option("--dataDir", default='data/Nominal',
                      help="directory for data")
    parser.add_option("--sysDir", dest='sysDir', help="directory for data",
                      default="./")

    parser.add_option("--poi", dest='poi', default='m4l_constrained_HM',
                      help='which variable used for counting')
    parser.add_option("--poiRange", dest='poi_range', default='130:1500',
                      help='range of POI')
    parser.add_option("-w", '--weightName', dest='wName', default='weight', help="Name of weights")
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

    # no VBF-like category in HighMass
    parser.add_option("--noVBF", dest='no_VBF', default=False, action='store_true', help="no VBF-like category")
    # no VBS samples in HighMass
    parser.add_option("--noVBS", dest='noVBS', default=False, action='store_true', help="no VBS events")
    # separate VBS samples in yields
    parser.add_option("--spVBS", default=False, action='store_true', help="separate VBS events")

    parser.add_option("-v","--verbose", dest='debug', default=False, help="in a debug mode", action='store_true')
    parser.add_option("--paper", dest='paper', default=False, help="paper style", action='store_true')

    parser.add_option("--histOut", default="hist_yields.root", help="root file for histograms")
    parser.add_option("--new", default=False, help="not use root file as input", action='store_true')

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        exit(1)

    reader = MinitreeReader(options)
    reader.readInputJson(args[0])
    reader.process()
