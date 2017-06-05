import sys
import csv
from pathlib import Path

def getFieldnames_table(afile):
	dicfieldnames = []
	csvfile = afile.open('r')
	csvlines = csv.reader(csvfile,delimiter='\t')
	csvlines.__next__()
	dicfieldnames1 = csvlines.__next__()
	dicfieldnames2 = csvlines.__next__()
	for i in range(1,len(dicfieldnames1)):
		dicfieldnames.append(dicfieldnames1[i] + '-' + dicfieldnames2[i])
	csvfile.close()
	return dicfieldnames

def getFieldnames_table_read(afile):
	dicfieldnames = []
	dicfieldnames.append('Filename')
	csvfile = afile.open('r')
	csvlines = csv.reader(csvfile,delimiter='\t')
	csvlines.__next__()
	dicfieldnames1 = csvlines.__next__()
	dicfieldnames2 = csvlines.__next__()
	for i in range(1,len(dicfieldnames1)):
		dicfieldnames.append(dicfieldnames1[i] + '-' + dicfieldnames2[i])
	csvfile.close()
	return dicfieldnames

def getFieldnames(afile,filename):
	dicfieldnames = []
	csvfile = afile.open('r')
	csvlines = csv.reader(csvfile,delimiter=',')
	dicfieldnames1 = csvlines.__next__()
	for i in range(1,len(dicfieldnames1)):
		dicfieldnames.append(filename + '-' + dicfieldnames1[i])
	csvfile.close()
	return dicfieldnames

def getFieldnames_read(afile,filename):
	dicfieldnames = []
	dicfieldnames.append('Filename')
	csvfile = afile.open('r')
	csvlines = csv.reader(csvfile,delimiter=',')
	dicfieldnames1 = csvlines.__next__()
	for i in range(1,len(dicfieldnames1)):
		dicfieldnames.append(filename + '-' + dicfieldnames1[i])
	csvfile.close()
	return dicfieldnames

def makeSummaryFile(csvline,fieldnames):
	tmpname = csvline['Filename']
	tokens = tmpname.split('/')
	targetname = tokens[len(tokens)-1]
	filename = 'git/pacc_cpachecker/DyResults/Summary/' + targetname + '.csv'
	targetfile = open(filename,'w')
	writer = csv.DictWriter(targetfile,fieldnames)
	writer.writeheader()
	targetfile.close()
	
	return filename

def getSummaryFile(csvline):
	tmpname = csvline['Filename']
	tokens = tmpname.split('/')
	targetname = tokens[len(tokens)-1]
	filename = 'git/pacc_cpachecker/DyResults/Summary/' + targetname + '.csv'

	return filename

def loadFieldName(dirname,filelist):
	dicfieldnames = []
	pfieldname = Path('git/pacc_cpachecker/DyResults/fieldnames')
	removingset = set()

	if pfieldname.exists(): # fieldname file is existed
		line = pfieldname.open('r').readline()
		tokens = line.split(',')
		tokens.pop()
		dicfieldnames = tokens
		for afile in filelist:
			afileparts = afile.parts
			filename = afileparts[len(afileparts)-1]
			if 'diff' in filename:
				removingset.add(afile)
	else:
		for afile in filelist:
			afileparts = afile.parts
			filename = afileparts[len(afileparts)-1]
			if 'diff' in filename:
				removingset.add(afile)
			elif 'table' in filename:
				tmp = getFieldnames_table(afile)
				dicfieldnames = dicfieldnames + tmp
			else:
				tmp = getFieldnames(afile,filename)
				dicfieldnames = dicfieldnames + tmp
		strfields = ''
		for i in range(len(dicfieldnames)):
			strfields += dicfieldnames[i]
			strfields += ','
		f = open('git/pacc_cpachecker/DyResults/fieldnames','w')
		f.write(strfields)
		f.close()

	return dicfieldnames, removingset

def addDummyRow(targetfile,fieldnames):
	dummyrow = {}
	for field in fieldnames:
		dummyrow[field] = 'NA'
	tf = open(targetfile,'a')
	writer = csv.DictWriter(tf, fieldnames=fieldnames)
	writer.writerow(dummyrow)
	tf.close()

def getStatusFromLine(csvline, ctkey):
	ret = 3
	algo = ctkey.split('-cputime')
	runset = algo[0]
	runkey = runset + '-status'
	if ('true' in csvline[runkey]) or ('false' in csvline[runkey]):
		ret = 0
	elif 'OUT OF NATIVE MEMORY' in csvline[runkey]:
		ret = 1
	elif 'TIMEOUT' in csvline[runkey]:
		ret = 2
	else:
		pass
	return ret

def writeRealRow(targetfile,fieldnames,csvline):
	f = open(targetfile,'r')
	reader = csv.DictReader(f,delimiter=',')
	targetlines = []
	for line in reader:
		targetlines.append(line)
	f.close()
	lastline = targetlines[len(targetlines)-1]
	for key in csvline:
		if lastline[key] == 'NA':
			if '-cputime (s)' in key:
				astatus = getStatusFromLine(csvline, key)
				if astatus == 0: # success! true or false
					lastline[key] = csvline[key]
				elif astatus == 1: # memory-out!
					lastline[key] = 1400
				elif astatus == 2: # time-out!
					lastline[key] = 1200
				else: # just error...
					lastline[key] = 1600
			else:
				lastline[key] = csvline[key]
	f = open(targetfile,'w')
	writer = csv.DictWriter(f,fieldnames=fieldnames)
	writer.writeheader()
	for line in targetlines:
		writer.writerow(line)
	f.close()

def ResultHandler(dirname,isexist):

	dicfieldnames = None
	isSummarycsvexist = isexist
	isDummyneed = True

	p = Path(dirname)
	filelist = set(p.glob('*.csv'))

	dicfieldnames, removingset = loadFieldName(dirname,filelist)

	filelist.difference_update(removingset)

	for afile in filelist:
		afileparts = afile.parts
		filename = afileparts[len(afileparts)-1]
		tmpfieldnames = []
		if 'table' in filename:
			tmpfieldnames = getFieldnames_table_read(afile)
			csvfile = afile.open('r')
			csvlines = csv.DictReader(csvfile,fieldnames=tmpfieldnames,delimiter='\t')
			csvlines.__next__()
			csvlines.__next__()
			csvlines.__next__()
			for csvline in csvlines:
				targetfile = ''
				if not isSummarycsvexist:
					targetfile = makeSummaryFile(csvline,dicfieldnames)
				else:
					targetfile = getSummaryFile(csvline)
				csvline.pop('Filename')
				if isDummyneed:
					addDummyRow(targetfile,dicfieldnames)
				writeRealRow(targetfile,dicfieldnames,csvline)
			csvfile.close()
		else:
			tmpfieldnames = getFieldnames_read(afile,filename)
			csvfile = afile.open('r')
			csvlines = csv.DictReader(csvfile,fieldnames=tmpfieldnames,delimiter=',')
			csvlines.__next__()
			for csvline in csvlines:
				targetfile = ''
				if not isSummarycsvexist:
					targetfile = makeSummaryFile(csvline,dicfieldnames)
				else:
					targetfile = getSummaryFile(csvline)
				csvline.pop('Filename')
				if isDummyneed:
					addDummyRow(targetfile,dicfieldnames)
				writeRealRow(targetfile,dicfieldnames,csvline)
			csvfile.close()
		isSummarycsvexist = True #only first afile have it as False
		isDummyneed = False

if __name__ == '__main__':
	ret = 0;	
	if len(sys.argv) == 2:
		ret = ResultHandler(sys.argv[1],False)
	elif len(sys.argv) > 2:
		ret = ResultHandler(sys.argv[1],True)
