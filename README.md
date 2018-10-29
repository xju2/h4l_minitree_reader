# h4l_minitree_reader

Dependence:
*  python 2.7
*  ROOT
*  pandas
*  root-pandas


Example command:

* Yield from mc15a
```bash
cd highmass
python ../script/get_yield.py minitree.json --base="/eos/atlas/atlascerngroupdisk/phys-higgs/HSG2/H4l/2018/MiniTrees/Prod_v18" --mcDir="mc16a/Nominal" --lumi=36.1 --digits=3 --histOut=hist_mc16a_new_sys.root --sysDir=mc16a
```
* Yield from mc16d
```bash
cd highmass
python ../script/get_yield.py minitree.json --base=/eos/atlas/atlascerngroupdisk/phys-higgs/HSG2/H4l/2018/MiniTrees/Prod_v18 --mcDir=mc16d/Nominal --lumi=43.7 --digits=3 --histOut=hist_mc16d_new_sys_2017.root --sysDir=mc16d
```
