#!/usr/bin/env python
import sys
import os
from pb_functions import DEFAULT_DATABASE,fileHandler, getFeatures
from ctypes import cdll

try:
    import yaafelib as yaafe
except ImportError, e:
    print 'ERROR: cannot load yaafe packages: ', e
    sys.exit()

print yaafe.__file__

def afeImport( songs , featureplan):
	newfiles = set()
	features = getFeatures(featureplan)
	for song in songs:
		for feat in features:
			if not os.path.isfile(DEFAULT_DATABASE + fileHandler(song.location) + "." + str(feat) + ".csv"):
                                newfiles.add(song.location)
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
                        afp.setOutputFormat('csv',os.path.dirname(os.path.realpath(__file__))+"/database",oparams)
                        #afp.setOutputFormat('csv',DEFAULT_DATABASE,oparams)

                        # process audio files
			for audiofile in audiofiles:
                                print "Processing: ", audiofile
				afp.processFile(engine,audiofile)



    

if __name__ == '__main__':
    fin = open(sys.argv[1],'r')
    songs = []
    for line in fin:
        songs.append(line.strip('\n'))
    fin.close
    afe(songs,sys.argv[2])
