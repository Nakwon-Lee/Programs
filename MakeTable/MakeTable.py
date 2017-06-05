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

def getFieldName(travstrat,encodingsfc,metrics,index):
	fieldnames = []
	fieldnames.append('Filename')
	for i in range(len(encodingsfc)):
		for j in range(len(travstrat)):
			field = travstrat[j]+encodingsfc[i]+metrics[index]
			fieldnames.append(field)
	return fieldnames

def MakeTable(dirname):

	travstrat = makeStrategies()
	encodingsfc = makeEncodingsFC()
	metrics = makeMetrics()

	p = Path(dirname)
	filelist = set(p.glob('*.csv'))
	dataframes = []

	index = 11

	fieldnames = getFieldName(travstrat,encodingsfc,metrics,index)
	targetfilename = dirname+'../a'+metrics[index]+'.csv'

	targetfile = open(targetfilename,'w')
	writer = csv.DictWriter(targetfile,fieldnames)
	writer.writeheader()
	targetfile.close()

	for afile in filelist:
		dataframes.append(pd.read_csv(afile,sep = ','))
		print(afile)
		df = dataframes[len(dataframes)-1]
		arow = {}
		arow['Filename'] = afile
		for i in range(len(encodingsfc)):
			for j in range(len(travstrat)):
				trav = travstrat[j]
				vals = df[trav+encodingsfc[i]+metrics[index]]
				for k in range(len(vals)):
					if vals[k] == 'none':
						vals[k] = np.nan
				vals = pd.Series(df[trav+encodingsfc[i]+metrics[index]],dtype=float)
				#print(vals)
				valmean = vals.mean(skipna=True)
				arow[trav+encodingsfc[i]+metrics[index]] = valmean
		targetfile = open(targetfilename,'a')
		writer = csv.DictWriter(targetfile,fieldnames)
		writer.writerow(arow)
		targetfile.close()

if __name__ == '__main__':
	MakeTable(sys.argv[1])
