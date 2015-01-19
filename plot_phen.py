#!/usr/bin/env python 

import os
import sys
from optparse import OptionParser as opt
from subprocess import call
import numpy as np
import figMethods
import scanomatic.dataProcessing.norm as som_norm
import textwrap

DEVNULL = open(os.devnull, 'wb')

"""
The program takes a list of dates, dates that the scan were preformed. Cycle 1 -> n. It gives all normalized phenotypes into 
temp files. The npy objects need to be called normalized_phenotypes.npy
"""


#Set the options that need to be set
prsr = opt()

prsr.add_option("-l", "--list", dest="list", metavar="FILE", help="List of dates to be analyzed. Format: DDMMYY")
prsr.add_option("-i", "--input-path", dest="path", metavar="PATH", help="Path to projects")
prsr.add_option( "-n", "--name-list", dest="name", metavar="FILE", help="list of environments plate1 -> plate8")

# Get options
(options, args) = prsr.parse_args()

def checkFile(file):
        if not os.path.isfile(file):
                quit("Could not find the file:" + file)

def checkValidArgs(options):
	if options.list == None:
		quit("ERROR: No list submitted")
	if options.path == None:
		quit("ERROR: No PATH submitted")
	if options.name == None:
		quit("ERROR: No name file submitted")
	listfile = options.list
	name = options.name
	checkFile(name)
	checkFile(listfile)

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

def writeRscript(PLATE):
	no_files = len(PLATE)
	folder=os.path.dirname(options.path)
        out = os.path.join(folder, "run_plot.r")
        out_file = open(out, "w")
	print >> out_file, "#!/usr/bin/env Rscript"
	print >> out_file, "library(ggplot2)"
	print >> out_file, "library(reshape2)"
	print >> out_file, "args <-commandArgs(trailingOnly = TRUE)"		
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
		print >> out_file, pindex + "$variable <- \"Cycle" + str(p) + "\"" 
		p = p + 1
	print >> out_file, "exp.molten <- rbind(", 
	p = 1
	while p <= no_files:
		if p == 1:
			print >> out_file, "p" + str(p),
		
		else:
			print >> out_file, ",p" + str(p),
		p = p + 1 
	print >> out_file, ")" 
	print >> out_file, "p <- ggplot(exp.molten, aes(y=value, x=variable, fill=\"#00AA93\"))"
	print >> out_file, "p <- p + geom_boxplot() + labs(x=\"\", y=\"Generation time\") + scale_fill_manual(name=\"\", values=c(\"#00AA93\",\"#FF6A00\"))"
	print >> out_file, "p <- p + theme(legend.position=\"none\")"
	print >> out_file, "print(p)"
	print >> out_file, "dev.off()"

def runPlot (options, name):
	name = os.path.join(os.path.dirname(options.path), name)
	name = name.rstrip()
	rscript=os.path.join(os.path.dirname(options.path), "run_plot.r")
	call(["Rscript", rscript, name], stdout=DEVNULL, stderr=DEVNULL)
	call(["rm", rscript])	

def fixParaquat(PLATE4, PLATE9):
	PLATE4[1] = PLATE9[1]
	PLATE4[2] = PLATE9[2]
	return PLATE4

def fixMissingCycles(PLATE1, PLATE3):
	del PLATE1[4:6]
	del PLATE3[5]	
	return PLATE1, PLATE3


""" START  """	

checkValidArgs(options)

PLATE1, PLATE2, PLATE3, PLATE4, PLATE5, PLATE6, PLATE7, PLATE8, PLATE9 = [],[],[],[],[],[],[],[],[]

with open (options.list, "r") as file:
	for date in file:
		date = date.rstrip()
		try:
			SCANNER1 = extractExp(options,date,1)
			PLATE1.append(SCANNER1[0])
			PLATE2.append(SCANNER1[1])
			PLATE3.append(SCANNER1[2])
			PLATE4.append(SCANNER1[3])
		except:
			pass
		try:
			SCANNER2 = extractExp(options,date,2)
			PLATE5.append(SCANNER2[0])
                	PLATE6.append(SCANNER2[1])
                	PLATE7.append(SCANNER2[2])
               		PLATE8.append(SCANNER2[3])
		except:
			pass
		try:
			SCANNER3 = extractExp(options,date,3)
			PLATE9.append(SCANNER3[0])
		except:
			pass


namefile = open(options.name, "r")

#PLATE4 = fixParaquat(PLATE4, PLATE9)
#PLATE1, PLATE3 = fixMissingCycles(PLATE1, PLATE3)


writeRscript(PLATE1)
name = namefile.readline()
runPlot(options, name)
writeRscript(PLATE2)
name = namefile.readline()
runPlot(options, name)
writeRscript(PLATE3)
name = namefile.readline()
runPlot(options, name)
writeRscript(PLATE4)
name = namefile.readline()
runPlot(options, name)
writeRscript(PLATE5)
name = namefile.readline()
runPlot(options, name)
writeRscript(PLATE6)
name = namefile.readline()
runPlot(options, name)
writeRscript(PLATE7)
name = namefile.readline()
runPlot(options, name)
writeRscript(PLATE8)
name = namefile.readline()
runPlot(options, name)













