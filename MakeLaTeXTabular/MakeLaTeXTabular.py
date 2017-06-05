import sys
import pandas as pd
import numpy as np
import csv
from scipy import stats
#import matplotlib.pyplot as plt
from pathlib import Path
import os

def makeStrategies():
	stratlist = ['Dy-CSRPO-','Dy-ABlkDFSCSRPO-','Dy-ABlkBFSCSRPO-','Dy-ABlkCSRPO-']

	return stratlist

def makeEncodingsFC():
	elist = ['ABEl','ABEl-FC','ABEl-FCm','lf','lf-FC','lf-FCm','PredAbs-ABEl','PredAbs-ABElf']

	return elist

def makeMetrics():
	mlist = ['-cputime (s)','.csv-NoR','.csv-RLen','.csv-RLeninBlkAvg','.csv-AFC','.csv-SFC','.csv-ComS','.csv-TfR','.csv-TTfCPA','.csv-TfFC','.csv-TfTran','.csv-TfSMTwoitp','.csv-NoAbs']

	return mlist

def getFieldName(travstrat,encodingsfc,metrics):
	fieldnames = []
	fieldnames.append('Filename')
	for i in range(len(encodingsfc)):
		for j in range(len(travstrat)):
			field = travstrat[j]+encodingsfc[i]+metrics[0]
			fieldnames.append(field)
	return fieldnames

def MakeLaTexTabular(fname):

	LaTeXTabfile = 'LaTeXTabular'

	travstrat = makeStrategies()
	encodingsfc = makeEncodingsFC()
	metrics = makeMetrics()

	fieldnames = getFieldName(travstrat,encodingsfc,metrics)

	targetfile = open(fname,'r')
	reader = csv.DictReader(targetfile,delimiter=',')

	for dictline in reader:
		aline = ''
		for i in range(len(fieldnames)):
			aline = aline + dictline[fieldnames[i]] + '&'
		aline = aline[0:len(aline)-1]
		aline = aline + '\\\\[1ex]\n'
		wrfile = open(LaTeXTabfile,'a')
		wrfile.write(aline)

if __name__ == '__main__':
	MakeLaTexTabular(sys.argv[1])
