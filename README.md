# WidebandSDINT
Joint Reconstruction of Wideband Single Dish and Interferometer data for Radio Astronomy

Publication : A Joint Deconvolution Algorithm to Combine Single-dish and Interferometer Data for Wideband Multiterm and Mosaic Imaging , Rau, U. ; Naik, N. ; Braun, T. Astronomical Journal, Volume 158, Number 1, June 2019 

This repository contains python scripts that work with CASA, a pointer to two simulated datasets, and a series of output PNG figures to compare and evaluate the results of different algorithmic options. 


To run the examples,

(1) Download data from ftp://ftp.aoc.nrao.edu/pub/staff/rurvashi/Data_For_WidebandSDINT_UR_github.tgz  and untar inside the Data directory.

(2) Run scripts from the Runs directory, within CASA.  

execfile('../Scripts/runsdint.py');runtest(1);runtest(2);runtest(3); etc.... 

Generated outputs are CASA log files, output CASA image files, and PNG figure files that summarize the imaging results for each example. Scripts/runsdint.py contains documentation on each of the tests triggered by runtest(num). 

