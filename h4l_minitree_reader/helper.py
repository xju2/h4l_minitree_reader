# -*- coding: utf-8 -*-
import ROOT
import sys
from root_pandas import read_root
import pandas as pd

def get_sys(file_name):
    """
    This will read text file for systematics,
    but up/down systematics are merged to 1.
    and returen a dictionary
    """
    sys_map = {}
    curr_section = ''
    with open(file_name) as f:
        for line in f:
            line = line.strip()
            if len(line) <= 0:
                continue

            if line.startswith('#'):
                continue

            # update the current section and add a section to the map
            if '[' in line:
                curr_section = line[1:-1].strip()
                if curr_section not in sys_map:
                    sys_map[curr_section] = {}
                continue

            sys_name = line.split('=')[0].strip()
            low, high = line.split('=')[1].split()
            mean = (abs(float(low)-1) + abs(float(high)-1))/2.

            sys_map[curr_section][sys_name] = mean
    return sys_map


def apply_cut(file_name, new_file_name, tree_name, cuts):
    f1 = ROOT.TFile.Open(file_name)
    tree1 = f1.Get(tree_name)
    outfile = ROOT.TFile.Open(new_file_name, 'recreate')
    new_tree = tree1.CopyTree(cuts)
    new_tree.Write()
    outfile.Close()
    f1.Close()


def overlap_study(f1, f1_suffix, f2, f2_suffix, var_name, low, hi, tree_name="tree_incl_all"):
    variables = ['event', 'run', 'event_type', 'prod_type', 'prod_type_HM', 'm4l_constrained_HM', 'm4l_constrained']
    df1 = read_root(f1, tree_name, columns=variables)
    df2 = read_root(f2, tree_name, columns=variables)

    df_union = pd.merge(df1, df2, how='outer', on=['event', 'run'], indicator=True, suffixes=(f1_suffix, f2_suffix))
    only_f1 = df_union[df_union._merge == 'left_only']
    only_f2 = df_union[df_union._merge == 'right_only']
    common = df_union[df_union._merge == 'both']

    # apply mass cut
    df1_in_mass_range = df1[ (df1[var_name] > low) & (df1[var_name] < hi) ]
    df2_in_mass_range = df2[ (df2[var_name] > low) & (df2[var_name] < hi) ]

    # find union of the two df
    outer_set = pd.merge(df1_in_mass_range, df2_in_mass_range,\
                         how='outer', on=['event', 'run'], indicator=True)
    only_f1_ = outer_set[outer_set._merge == 'left_only']
    only_f2_ = outer_set[outer_set._merge == 'right_only']
    common_ = outer_set[outer_set._merge == 'both']

    summary_list = [common_.shape[0], only_f1_.shape[0], only_f2_.shape[0]]
    print("In the mass range [{}, {}] GeV:".format(low, hi))
    print("{} events in common, {} events only found in {}, {} events only found in {}".format(
        summary_list[0], summary_list[1], f1_suffix, summary_list[2], f2_suffix)
    )

    summary = pd.Series(summary_list, index=['both', f1_suffix, f2_suffix], name='In Fraction')
    summary.plot.pie(autopct='%.2f', fontsize=20, figsize=(6, 6))

    print("there are {} events in total in *{}*".format(df1_in_mass_range.shape[0], f1_suffix))
    print("After moving to {}...".format(f2_suffix))
    # how many events in this range only in df1, but can be found elsewhere in df2.
    inner_f1_moved = pd.merge(only_f1_, df2, how='inner', on=['event', 'run'])
    print("{} events were lost in {} due to calibration".format(inner_f1_moved.shape[0], f2_suffix))
    if inner_f1_moved.shape[0] > 0:
        print(inner_f1_moved[['event', 'run']])

    # how many are in df1 but not in df2?
    inner_f1 = pd.merge(only_f1_, only_f1, how='inner', on=['event', 'run'])
    print("{} events were completely lost in {}".format(inner_f1.shape[0], f2_suffix))
    if inner_f1.shape[0] > 0:
        print(inner_f1[['event', 'run']])

    # how many events in this range only in f2, but can be found elsewhere in f1.
    inner_f2_moved_in = pd.merge(only_f2_, df1, how='inner', on=['event', 'run'])
    print("{} events were added in {} due to calibration".format(inner_f2_moved_in.shape[0], f2_suffix))
    if inner_f2_moved_in.shape[0] > 0:
        print(inner_f2_moved_in[['event', 'run']])

    # how many are only in df2?
    inner_f2 = pd.merge(only_f2_, only_f2, how='inner', on=['event', 'run'])
    print("{} events were added as new candidates in {}".format(inner_f2.shape[0], f2_suffix))
    if inner_f2.shape[0] > 0:
        print(inner_f2[['event', 'run']])
