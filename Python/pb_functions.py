import sys
import os
from numpy import zeros, log10, array, mean ,var, linalg, ones, cov, argmax, argmin
import linecache as lc
from pb_nml import Song, fileHandler

#import matplotlib.pyplot as plt
#import scipy as sp

DEFAULT_ANALYSIS_LENGTH = 1000
#DEFAULT_DATABASE = os.path.dirname(os.path.realpath(sys.argv[0]))+"/database"
if sys.platform.startswith("win32"):
        DEFAULT_DATABASE = os.path.dirname(os.path.realpath(sys.argv[0]))+fileHandler("\\database")
else:
        DEFAULT_DATABASE = os.path.dirname(os.path.realpath(sys.argv[0]))+fileHandler("/database")
                

def getFeatures( featureplan ):
	fp = open(featureplan, 'r')
	features = []
	for line in fp:
		features.append(line.split(":")[0])
	fp.close
	return features

def fillFVsBySeg( audiofile , features , segst , seglen ):
	fv =[]
	nof = 0
	for feat in features:
                afefile = DEFAULT_DATABSE + fileHandler(audiofile) + "." + str(feat) + ".csv"
		try:
			fin = open(afefile)
			if not str(feat)=="mfcc":
				for i,line in enumerate(fin):
					if i > segst and i <= seglen+segst:
						line.strip("\n")
						num = line.split(",")
						fv.append(float(num[0]))
				nof = nof + 1
			else:
				for j in range(3):
					fin.seek(0)
					for i,line in enumerate(fin):
						if i > segst and i <= seglen+segst:
							line.strip("\n")
							num = line.split(",")
							fv.append(float(num[j]))
					nof = nof + 1
		except IOError:
			print "Afe file not found: ",afefile
			pass
		fin.close()
	return fv, nof
	
def fillFVs( audiofile , features):
	fv =[]
	nos = 0
	nof = 0
	for feat in features:
                afefile = DEFAULT_DATABASE + fileHandler(audiofile) + "." + str(feat) + ".csv"
		try:
			fin = open(afefile)
                        if not str(feat)=="mfcc":
				for line in fin:
					line.strip("\n")
					num = line.split(",")
					fv.append(float(num[0]))
				nof = nof + 1
			else:
				for j in range(3):
					fin.seek(0)
					for line in fin:
						line.strip("\n")
						num = line.split(",")
						fv.append(float(num[j]))
					nof = nof + 1
			fin.close()
		except IOError:
			print "Afe file not found", afefile
			pass
		if nos==0:
			nos = len(fv)
	return fv, nos, nof

def timbFV( audiofile, features , segst, seglen ):
	fv, nof = fillFVsBySeg( audiofile, features , segst, seglen )
	mat = array(fv)
	mat = mat.reshape((nof,seglen))
	tfv = []
	for j in range(nof):
		tfv.append(mean(mat[j,:]))
		tfv.append(var(mat[j,:]))
	# compute low energy feature:
	lef = 0
	for j in range(seglen):
		if mat[0,j]<tfv[0]:
			lef = lef+1
	# norm timbFV:
	tfv[0]=float(lef)/seglen
	tfv[2]=1+log10(tfv[2])/log10(16000)
	tfv[3]=1+log10(tfv[3])/log10(16000)
	tfv[4]=log10(tfv[4])/log10(16000)
	tfv[5]=log10(tfv[5])/log10(16000)
	tfv[6]=tfv[6]/seglen
	#print tfv
	return tfv
	
def comp2FV( fv1, fv2 ):
	if not len(fv1)==len(fv2):
		print "ERROR: Feature vectores of different sizes entered"
		return
	ffv = []
	length = 0
	for i in range(len(fv1)):
		n = fv1[i]+fv2[i]
		m = abs(fv1[i]-fv2[i])
		if not n==0:
			ffv.append(m/n)
		else:
			ffv.append(0)
	return linalg.norm(array(ffv))

# DEPRECATED!
# testing function
def comp2Songs( song1, song2 , featureplan):
	seglen = 50
	maxi1 = findSeg( song1.location , featureplan )
	maxi2 = findSeg( song2.location , featureplan )
	fvs1 = []
	fvs2 = []
	for i in maxi1:
		fvs1.append(timbFV( song1.location, featureplan , i, seglen ))
	for i in maxi2:
		fvs2.append(timbFV( song2.location, featureplan , i, seglen ))
	mat = ones((len(maxi1),len(maxi2)))
	for i in range(len(maxi1)):
		for j in range(len(maxi2)):
			mat[i,j]=comp2FV(fvs1[i],fvs2[j])
	print mat

# DEPRECATED!	
# old Database implementation
def read1SegFromDbFile( audiofiles ):
	segs = dict.fromkeys(audiofiles)
	fin = open(DEFAULT_DATABASE+fileHandler("sections_db.txt"))
	for line in fin:
		name = line.split(":")
		if name[0] in audiofiles:
			rest = line.strip(name[0] + ":")
			maxi = rest.split(",")
			segs[name[0]] = maxi[0]
	return segs

# DEPRECATED!	
# old Database implementation
def updateSeg( audiofiles , featureplan, num ):
	newfiles = set(audiofiles)
	fin = open(DEFAULT_DATABASE+fileHandler("sections_db.txt"),'r+')
	for line in fin:
		name = line.split(":")
		rest = line.strip(name[0] + ":")
		maxi = rest.split(",")
		if len(maxi) >= num:
			try:
				newfiles.remove(name[0])
			except KeyError:
				pass
	for song in newfiles:
		maxi = findSeg( song.location , featureplan, num )
		s = ''
		s = song + ":"
		for i in maxi:
			s = s + str(i)
			s = s + ","
		s = s[:-1]
		s = s + "\n"
		fin.write(s)

def findSeg( audiofile , featureplan , num):
	features = getFeatures( featureplan )
	fv, nos, nof = fillFVs( audiofile, features )
	mat = array(fv)
	mat = mat.reshape((nof,nos))
	
	# average data over desired windowsize:
	windowsize = 20
	tfv = []
	newlen = nos / windowsize
	print "Number of Samples:", nos,  "Window:", windowsize
	for i in range(nof):
		for j in range(newlen):
			start = j*windowsize
			tfv.append(mean(mat[i,range(start, start+windowsize)]))
			#tfv.append(np.var(mat[i,range(start, start+windowsize)]))
	mat = array(tfv)
	mat = mat.reshape((nof,newlen))
	nof = nof
	NumberOfSamples = nos
	nos=newlen
	
	
	# create covariance matrix
	cm = zeros((nof,nof))
	for i in range(nof):
		a = mat[i,:]
		for j in range(nof):
			if not i==j:
				b = mat[j,:]
				elem = cov(a,b)
				cm[i,i] = elem[0,0]
				cm[j,j] = elem[1,1]
				cm[i,j] = elem[0,1]
				cm[j,i] = elem[1,0]
	# inverted covariance matrix
	icm = linalg.inv(cm)
	# distance vector
	dv = zeros(nos)
	ddv = zeros(nos)
	
		
	for i in range(int(0.05*nos),int(0.95*nos)):
		dif = array(mat.T[i]-mat.T[i+1])
		dv[i] = dif.T.dot(icm).dot(dif)
		ddv[i] = dv[i]-dv[i-1]
	#plt.plot(dv)
	#plt.plot(ddv)
	#plt.axis([0,nos,0,50])
	#plt.show()
	
	# select ROIs by maxima
	maxi = []
	deletedRange = int(nos/(num*2))
	for i in range(num):
		maxi.append(argmax(ddv))
		for j in range(deletedRange):
			try:
				ddv[maxi[i]-j]=0
				ddv[maxi[i]+j]=0
			except:
				pass
	multiplier = windowsize/86.0
	realMaxi =[]
	for i in maxi:
		realMaxi.append(i*windowsize)
		print secondsToMinutes(i*multiplier)
	return realMaxi, NumberOfSamples

def secondsToMinutes(s):
	a = int(s/60)
	b = float(s-a*60)/100
	#print s,a,b
	return a+b

# Distance Matrix implementation
# only calculates distances between first halfs and second halfs
def distanceMatrixMtlSmart(songs, featureplan, bpmVal, keyVal): 
    print "Starting smart distance matrix calculation of ",  songs
    features = getFeatures( featureplan )
    sections = []
    sentrys = []
    eentrys = []
    sfvs = []
    efvs = []
    matlen = 0
    sections.append(0)
    for s in songs:
		fin = open(DEFAULT_DATABASE+fileHandler(s.location)+".timeline.mtl","r")
		nosecs = int(fin.readline())
		ssecs = int(nosecs*0.5)
		sections.append(ssecs+sections[len(sections)-1])
		matlen = matlen +ssecs
		fin.readline()
		nos = int(fin.readline())
		for secs in range(ssecs):
			sta = int(fin.readline())
			fin.readline()
			end = int(fin.readline())
			label = fin.readline()
			sfvs.append(timbFV( s.location, features , sta, end-sta ).append(s.bpm).append(s.key))
			sentrys.append(s+":"+label+":"+str(sta))
		for secs in range(ssecs,nosecs):
			sta = int(fin.readline())
			fin.readline()
			end = int(fin.readline())
			label = fin.readline()
			efvs.append(timbFV( s.location, features , sta, end-sta ).append(s.bpm).append(s.key))
			eentrys.append(s+":"+label+".:"+str(sta))
    mat = zeros((matlen,matlen))
    for i in range(matlen):
		for j in range(matlen):
			mat[i,j]=comp2FV(efvs[i],sfvs[j])
    return mat, sections, sentrys, eentrys

# DEPRECATED!
# Simple distance Matrix Timeline implementation
# Careful: Function does not distinguish between different songs, similarity among parts of the same songs possible!	
def distanceMatrixMtl(songs, featureplan): 
	features = getFeatures( featureplan )
	entrys = []
	fvs = []
	for s in songs:
		fin = open(DEFAULT_DATABASE+fileHandler(s.location)+".timeline.mtl","r")
		nosecs = int(fin.readline())
		fin.readline()
		nos = int(fin.readline())
		for secs in range(nosecs):
			sta = int(fin.readline())
			fin.readline()
			end = int(fin.readline())
			label = fin.readline()
			fvs.append(timbFV( s.location, features , sta, end-sta ))
			entrys.append(s+"."+label+"."+str(secs))
	mat = zeros((len(entrys),len(entrys)))
	for i in range(len(entrys)):
		for j in range(len(entrys)):
			if j>i:
				mat[i,j]=comp2FV(fvs[i],fvs[j])
				mat[j,i]=mat[i,j]
			if j==i:
				mat[i,j]=float("inf")
	return mat,entrys

# Simple single vector distance Matrix
def distanceMatrix( songs , featureplan, bpmVal, keyVal):
	seglen = 50
	features = getFeatures( featureplan )
	segs = read1SegFromDbFile(songs)
	print segs
	fvs = []
	for song in songs:
		sta = int(segs[song])
		fvs.append(timbFV( song.location, features , sta, seglen ))
	mat = zeros((len(fvs),len(fvs)))
	for i in range(len(fvs)):
		for j in range(len(fvs)):
			if j>i:
				mat[i,j]=comp2FV(fvs[i],fvs[j])
				mat[j,i]=mat[i,j]
			if j==i:
				mat[i,j]=float("inf")
	return mat

def orderMatrix( mat, entrys, first ):
	final = [0 for i in range(len(mat[0]))]
	final[0] = first
	mat[:,first]=float("inf")
	for i in range(len(mat[0])-1):
		final[i+1] = argmin(mat[final[i]])
		mat[:,final[i+1]]=float("inf")
	for i in final:
		print i,":",entrys[i]
	print final
	return final

def orderMatrixSmart( songs, mat, sections, sentrys, eentrys, first,  outputfile ):
    final = [0 for i in range(len(songs))]
    final[0] = first
    ssection = [0 for i in range(len(songs))]
    esection = [0 for i in range(len(songs))]
    ssection[0] = 0
    for i in range(sections[first],sections[first+1]):
        mat[i,:] = float("inf")
    for i in range(len(songs)-1):
        testlist = []
        for j in range(sections[final[i]],sections[final[i]+1]):
            testlist.append(mat[:,i])
        argmin = argmin(testlist)
        while argmin > sections[len(sections)-1]:
            argmin = argmin - sections[len(sections)-1]
            esection[i] = esection[i]+1
        for j,sec in enumerate(sections):
            if argmin < sec:
                final[i+1] = j-1
                ssection[i+1] = argmin-sections[j-1]
                break
        for j in range(sections[final[i+1]],sections[final[i+1]+1]):
            mat[j,:] = float("inf")

    if outputfile !='':
        output = open(outputfile, 'w+')
    split = 2
    if sys.platform.startswith("win32"):
            split = 3
    for j,i in enumerate(final):
        sseconds = 0
        if j != 0:
            sseconds = float(sentrys[sections[i]+ssection[i]].split(":")[split])/44100.0
        sseconds = sseconds * 512
        sminutes = int(secondsToMinutes(sseconds))
        sseconds = sseconds - 60*sminutes
        #print eentrys[sections[i]+esection[i]].split(":"), eentrys[sections[i]+esection[i]], eentrys, sections[i], esection[i]
        eseconds = float(eentrys[sections[i]+esection[i]].split(":")[split])/44100.0
        eseconds = eseconds * 512
        eminutes = int(secondsToMinutes(eseconds))
        eseconds = eseconds - 60*eminutes				
        print "Starting at ", sminutes, ":" , int(sseconds),"\n",i,":",songs[i].location,"\nEnding at",eminutes, ":" , int(eseconds)
        if output:
            for stri in ["Starting at ", sminutes, ":" , str(int(sseconds)),"\n",i,":",songs[i].location,"\nEnding at ",str(eminutes), ":" , str(int(eseconds)),"\n"]:
                output.write(str(stri))
    output.close()
    return final

#Timeline Database update
def updateMtlDatabase(songs, featureplan, noMaxi):
        for s in songs:
                if (os.path.isfile(DEFAULT_DATABASE+fileHandler(s.location)+".timeline.mtl")):
                        continue
                else:
                        labels=[]
                        maxi,nos = findSeg(s.location,featureplan,noMaxi)
                        for i in maxi:
                                labels.append("none")
                        createMtlFile(s, maxi, labels, nos, DEFAULT_ANALYSIS_LENGTH)
                

#Timeline file writer
def createMtlFile(song, maxi, labels, NumberOfSamples, sectionlen):
	fout = open(DEFAULT_DATABASE+fileHandler(song.location)+".timeline.mtl",'w+')
	fout.write(str(len(maxi))+"\n")
	fout.write("1"+"\n")
	fout.write(str(NumberOfSamples)+"\n")
	for index, i in enumerate(sorted(maxi)):
		fout.write(str(i)+"\n")
		fout.write(str(index)+"\n")
		fout.write(str(i+sectionlen)+"\n")
		fout.write(str(labels[index])+"\n")
	fout.close()	
	
#UNFINISHED!	
def createMfFile(songs, outputfile):
	fout = open(DEFAULT_DATABASE+fileHandler(outputfile),'w+')
	for s in songs:
		fout.write(s.location+"\t"+DEFAULT_DATABASE+fileHandler(s.location)+".timeline.mtl"+"\n")
	fout.close()

#Testfunktion:
#if __name__ == '__main__':
#	fin = open(sys.argv[1])
#	songs = []
#	for line in fin:
#		songs.append(Song('','',0,0,line.strip(),[])
#		#maxi =[]
#		#labels = []
#		maxi,nos = findSeg(line.strip(),sys.argv[2],8)
#		for i in maxi:
#			#labels.append("none")
#		createMtlFile(line.strip(), maxi, labels, nos, DEFAULT_ANALYSIS_LENGTH)
#	fin.close
#	mat,sections, sentrys, eentrys = distanceMatrixMtlSmart(songs,sys.argv[2])
#	orderMatrixSmart(songs,mat,sections, sentrys, eentrys, 1, '')
#	#createMfFile(songs,"/musiclist.mf")
#	
#	#comp2Songs(songs[0],songs[1], sys.argv[2])
	
	
