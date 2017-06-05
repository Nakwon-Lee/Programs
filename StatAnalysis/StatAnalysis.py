import sys
import pandas as pd
import numpy as np
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
	mlist = ['-cputime (s)','-status','.csv-NoR','.csv-RLen','.csv-RLeninBlkAvg','.csv-AFC','.csv-SFC','.csv-ComS','.csv-TfR','.csv-TTfCPA','.csv-TfFC','.csv-TfTran','.csv-TfSMTwoitp','.csv-NoAbs']

	return mlist

def cohen_D(x,y):
	nx = 0
	ny = 0
	for a in x:
		if a != 'none':
			nx = nx + 1
	for b in y:
		if b != 'none':
			ny = ny + 1

	mx = x.mean()
	my = y.mean()

	xsum = 0
	for a in x:
		if a != 'none':
			xsum = xsum + ((a - mx) * (a - mx))

	ysum = 0
	for b in y:
		if a != 'none':
			ysum = ysum + ((b - my) * (b - my))

	sx2 = xsum / (nx - 1)
	sy2 = ysum / (ny - 1)

	s = np.sqrt( (((nx - 1) * sx2) + ((ny - 1) * sy2)) / (nx+ny-2) )

	return (x.mean() - y.mean()) / s if s > 0 else 9999

def checkOtherMetrics(df, travst1, travst2, enfc, metrics):
	for i in range(1,len(metrics)):
		#x = df[df[travst1 + enfc + metrics[i]] != 'none'][travst1 + enfc + metrics[i]]
		#y = df[df[travst2 + enfc + metrics[i]] != 'none'][travst2 + enfc + metrics[i]]
		x = df[travst1 + enfc + metrics[i]]
		y = df[travst2 + enfc + metrics[i]]

		isgood = True
		statistics = None
		pvalue = None
		mx = None
		my = None

		if x.dtype != 'object' and y.dtype != 'object':
			statistics, pvalue = stats.ttest_ind(x,y)
			mx = x.mean()
			my = y.mean()
			cd = cohen_D(x,y)
		else:
			isgood = False

		if isgood and pvalue < 0.05 and (cd >= 0.2 or cd <= -0.2):
			print('\t',metrics[i],' ',mx,' ',my,' ',pvalue,' ',cd)

	print('')

def StatusDiff(stat):
	ret = 1
	key = stat[0]
	for i in range(len(stat)):
		if key == stat[i]:
			ret = 0
	return ret

def StatAnalysis(dirname):

	travstrat = makeStrategies()
	encodingsfc = makeEncodingsFC()
	metrics = makeMetrics()

	p = Path(dirname)
	filelist = set(p.glob('*.csv'))
	dataframes = []

	for afile in filelist:
		dataframes.append(pd.read_csv(afile,sep = ','))
		print(afile)
		df = dataframes[len(dataframes)-1]
		for i in range(len(encodingsfc)):
			xtrav = travstrat[1]
			ytrav = travstrat[3] 
			x = df[xtrav+encodingsfc[i]+metrics[0]]
			y = df[ytrav+encodingsfc[i]+metrics[0]]
			#statx = df[xtrav+encodingsfc[i]+metrics[1]] 
			#staty = df[ytrav+encodingsfc[i]+metrics[1]]
			#print('x=',StatusDiff(statx))
			#print('y=',StatusDiff(staty))
			statistics, pvalue = stats.ttest_ind(x,y)
			mx = x.mean()
			my = y.mean()
			mr = mx / my
			cd = cohen_D(x,y)
			#if pvalue < 0.05:
			#if pvalue < 0.05 and (cd >= 0.2 or cd <= -0.2):
			#print(encodingsfc[i],' ',mx,' ',my)
			if pvalue < 0.05 and (cd >= 0.8 or cd <= -0.8) and (mr > 1.1 or mr < 0.9):
				print(encodingsfc[i],mx,' ',my,' ',mr,' ',pvalue,' ',cd)
				checkOtherMetrics(df,xtrav,ytrav,encodingsfc[i],metrics)
		print('')

if __name__ == '__main__':
	StatAnalysis(sys.argv[1])
