#!/usr/bin/env python
import yaafelib as yaafe
import sys
import os
import pb_functions

def afeImport( musiclist, featureplan):
	fin = open(musiclist,'r')
	audiofiles = []
	newfiles = set()
	for line in fin:
		audiofiles.append(line.strip())
	fin.close()
	features = pb_functions.getFeatures(featureplan)
	for audiofile in audiofiles:
		for feat in features:
			try:
				fin = open(os.path.dirname(os.path.realpath(__file__)) + audiofile + "." + str(feat) + ".csv")
			except IOError:
				newfiles.add(audiofile)
	if len(newfiles) == 0:
		print "No extraction necessary. Database is up to date."
	else:
		afe( newfiles, featureplan )
			

def afe( audiofiles , featureplan):
	if yaafe.loadComponentLibrary('yaafe-io')!=0:
			print 'WARNING: cannot load yaafe-io component library !'
	globalrate = 44100
	fp = yaafe.FeaturePlan(sample_rate=globalrate)
	# read featureplan list
	fp.loadFeaturePlan(featureplan)
	# read audio file list
	if audiofiles:
			# initialize engine
			engine = yaafe.Engine()
			if not engine.load(fp.getDataFlow()):
				return
			# initialize file processor
			afp = yaafe.AudioFileProcessor()
			oparams = dict()
			for pstr in {'Metadata=false'}:
				pstrdata = pstr.split('=')
				if len(pstrdata)!=2:
					print 'ERROR: invalid parameter syntax in "%s" (should be "key=value")'%pstr
					return
				oparams[pstrdata[0]] = pstrdata[1]
			afp.setOutputFormat('csv',os.path.dirname(os.path.realpath(__file__)),oparams)
			# process audio files
			for audiofile in audiofiles:
				afp.processFile(engine,audiofile)



    

if __name__ == '__main__':
    afe(sys.argv[1],sys.argv[2])
