#!/usr/bin/env python 

import os
import sys
from optparse import OptionParser as opt
from subprocess import call
import numpy as np
import figMethods
import scanomatic.dataProcessing.norm as som_norm
import textwrap

"""
The program takes a list of dates, dates that the scan were preformed. Cycle 1 -> n. It gives all normalized phenotypes into 
temp files. The npy objects need to be called normalized_phenotypes.npy
"""


#Set the options that need to be set
prsr = opt()

prsr.add_option("-l", "--list", dest="list", metavar="FILE", help="List of dates to be analyzed. Format: DDMMYY")
prsr.add_option("-i", "--input-path", dest="path", metavar="PATH", help="Path to projects")
prsr.add_option("-r", "--correction-R-Script", dest="script", metavar="FILE", help="R script containing skipped lines that you want to include in the plotting")
prsr.add_option("-s", "--skip-list", dest="skip", metavar="FILE", help="list of dates to skip in plotting")

# Get options
(options, args) = prsr.parse_args()

def checkValidArgs(options):
	if options.list == None:
		quit("ERROR: No list submitted")
	if options.path == None:
		quit("ERROR: No PATH submitted")

def extractExp(options, scan_date, scan_no):
	scan = "_scanner" + str(scan_no)
	project = os.path.join(options.path,(scan_date + scan), (scan_date + scan), "analysis", "normalized_phenotypes.npy")
	tmpdir = os.path.dirname(project)
	tmpdir = os.path.join(tmpdir, "temp") 
	if not os.path.exists(tmpdir):
    		os.makedirs(tmpdir)
	DN = np.load(project)
	EP = [som_norm.DEFAULT_CONTROL_POSITION_KERNEL == False] * 4
	pn1,pn2,pn3,pn4 = som_norm.getControlPositionsArray(DN,EP)
	pn2=np.ma.masked_invalid(pn2[:, :, 0])
	pn1=np.ma.masked_invalid(pn1[:, :, 0])
	pn3=np.ma.masked_invalid(pn3[:, :, 0])
	pn4=np.ma.masked_invalid(pn4[:, :, 0])	
	np.savetxt((os.path.join(tmpdir,"plate4_exp_gt.txt")), pn4[pn4.mask == False], fmt='%.8f')
	np.savetxt((os.path.join(tmpdir,"plate1_exp_gt.txt")), pn1[pn1.mask == False], fmt='%.8f')
	np.savetxt((os.path.join(tmpdir,"plate2_exp_gt.txt")), pn2[pn2.mask == False], fmt='%.8f')
	np.savetxt((os.path.join(tmpdir,"plate3_exp_gt.txt")), pn3[pn3.mask == False], fmt='%.8f')
	D_CONTROL = som_norm.getControlPositionsArray(DN)
	D_CONTROL_1 = D_CONTROL[0]
	D_CONTROL_2 = D_CONTROL[1]
	D_CONTROL_3 = D_CONTROL[2]
	D_CONTROL_4 = D_CONTROL[3]
	p1=np.ma.masked_invalid(D_CONTROL_1[:, :, 0])
	p2=np.ma.masked_invalid(D_CONTROL_2[:, :, 0])
	p3=np.ma.masked_invalid(D_CONTROL_3[:, :, 0])
	p4=np.ma.masked_invalid(D_CONTROL_4[:, :, 0])
	np.savetxt((os.path.join(tmpdir, "plate1_ctrl_gt.txt")), p1[p1.mask == False], fmt='%.8f')
	np.savetxt((os.path.join(tmpdir, "plate2_ctrl_gt.txt")), p2[p2.mask == False], fmt='%.8f')
	np.savetxt((os.path.join(tmpdir, "plate3_ctrl_gt.txt")), p3[p3.mask == False], fmt='%.8f')
	np.savetxt((os.path.join(tmpdir, "plate4_ctrl_gt.txt")), p4[p4.mask == False], fmt='%.8f')
	FILES_FOR_PLOTTING = []
	FILES_FOR_PLOTTING.append(os.path.join(tmpdir, "plate1_exp_gt.txt"))
	FILES_FOR_PLOTTING.append(os.path.join(tmpdir, "plate2_exp_gt.txt"))
	FILES_FOR_PLOTTING.append(os.path.join(tmpdir, "plate3_exp_gt.txt"))
	FILES_FOR_PLOTTING.append(os.path.join(tmpdir, "plate4_exp_gt.txt"))
	FILES_FOR_PLOTTING.append(os.path.join(tmpdir, "plate1_ctrl_gt.txt"))
	FILES_FOR_PLOTTING.append(os.path.join(tmpdir, "plate2_ctrl_gt.txt"))
	FILES_FOR_PLOTTING.append(os.path.join(tmpdir, "plate3_ctrl_gt.txt"))
	FILES_FOR_PLOTTING.append(os.path.join(tmpdir, "plate4_ctrl_gt.txt"))
	return FILES_FOR_PLOTTING

def startRscript():
	folder=os.path.dirname(options.path)
	out = os.path.join(folder, "run_plot.r")
	out_file = open(out, "w")
	print >> out_file, textwrap.dedent("""\
					#!/usr/bin/env Rscript
					library(ggplot2)
					library(reshape2)""")
def writeRscript(PLATE):
	no_files = len(PLATE)
	folder=os.path.dirname(options.path)
        out = os.path.join(folder, "run_plot.r")
        out_file = open(out, "w")
        print >> out_file, textwrap.dedent("""\
#!/usr/bin/env Rscript
library(ggplot2)
library(reshape2)
options(warn=-1)
args <-commandArgs(trailingOnly = TRUE)		
suppressMessages(library(\"ggplot2\"))
suppressMessages(library(\"plyr\"))""")		
	print >> out_file, "sink(file = \"" + folder + "/temp.out\", type = c(\"output\", \"message\"))"
	print >> out_file, "filename<-paste(args[1], \'.pdf\', sep=\"\")"
	print >> out_file, "pdf(filename)"
	p = 1
	for line in PLATE:
		line = line.rstrip()
		pindex = "p" + str(p)
		print >> out_file, pindex + " <- read.table(\"" + line + "\")"
		p = p + 1
	p = 1
	for line in PLATE:
		pindex = "p" + str(p)
		print >> out_file, pindex + " <- melt(" + pindex + ")"
		p = p + 1
	print >> out_file, "exp <- data.frame(p1$value)"
	p = 2
	i = no_files
	while i > (no_files - 1):
		pindex = "p" + str(p)
                print >> out_file, "exp$V" + str(p) + " <- p" + str(p) + "$value"
		p = p + 1
		i = i - 1
		
	print >> out_file, "exp$type <- \"Experiment\""
	n = 1
	print >> out_file, ("names(exp) <- c("),
	while p > 1:
		if p == 1:
			print >> out_file, "\"Cycle" + str(n) + "\",",
		
		else:
			print >> out_file, ",\"Cycle" + str(n) + "\"",
		
		n = n + 1
		p = p - 1 
	print >> out_file, ")" 
	print >> out_file, "exp.molten <- melt(exp, id=\"type\")"
	print >> out_file, "p <- ggplot(exp.molten, aes(y=value, x=variable, fill=type))"
	print >> out_file, "p <- p + geom_boxplot() + labs(x=\"\", y=\"Generation time\") + scale_fill_manual(name=\"\", values=c(\"#00AA93\",\"#FF6A00\"))"
	

""" START  """	
PLATE1, PLATE2, PLATE3, PLATE4, PLATE5, PLATE6, PLATE7, PLATE8, PLATE9 = [],[],[],[],[],[],[],[],[]

with open (options.list, "r") as file:
	for date in file:
		date = date.rstrip()
		SCANNER1 = extractExp(options,date,1)
		PLATE1.append(SCANNER1[0])
		PLATE2.append(SCANNER1[1])
		PLATE3.append(SCANNER1[2])
		PLATE4.append(SCANNER1[3])
"""		SCANNER2 = extractExp(options,date,2)
		PLATE5.append(SCANNER2[0])
                PLATE6.append(SCANNER2[1])
                PLATE7.append(SCANNER2[2])
                PLATE8.append(SCANNER2[3])
		try:
			SCANNER3 = extractExp(options,date,3)
			PLATE9.append(SCANNER3[0])
		except:
			pass
"""

checkValidArgs(options)
#startRscript()
writeRscript(PLATE1)

