from lxml import etree as et
from sys import platform
import uuid

DEFAULT_ANALYSIS_LENGTH = 1000
DEFAULT_LEN = 4000
TO_FRAMES = 44.1/512
FROM_FRAMES = 512/44.1

def fileHandler(filen):
                
        if platform.startswith("win32"):
                if filen == '':
                        return '\\'
                elif filen[0] == '\\':
                        return filen
                elif filen[2] == '\\':
                        return filen[2:]
                else:
                        return '\\' + filen
        else:
                if filen == '':
                        return '/'
                elif filen[0] == '/':
                        return filen
                else:
                        return '/' + filen

# units are given in mseconds
class Section(object):
    

    def __init__(self, start, length, label):
        self.start = start
        if length >= 0.0:
            self.length = length
            self.end = start + length
        else:
            self.length = DEFAULT_LEN
            self.end = start + DEFAULT_LEN
        self.label = label
        
    def toFrames(self):
            st = int(self.start * TO_FRAMES)
            le = int(self.length * TO_FRAMES)
            if le <=0:
                    le = DEFAULT_ANALYSIS_LENGTH
            return st , le  

    def fromFrames(self):
        self.start *= FROM_FRAMES
        self.length *= FROM_FRAMES
        #return self

        
class Song(object):

    def __init__(self, artist, title, bpm, key, location, sections, playtime):
        self.bpm = bpm
        self.artist = artist
        self.title = title
        self.location = location
        self.key = key
        self.startsections = []
        self.endsections =[]
        if playtime != 0.0:
                self.playtime = playtime
                middle = 0.5*playtime
                # convert to ms
                middle *= 1000.0
                for sec in sections:
                        if sec.start < middle:
                                self.startsections.append(sec)
                        else:
                                self.endsections.append(sec)
        else:
                for sec in sections:
                        self.sections.append(sec)
                        
    def setRecommendedSection(self,recstart,recend):
            self.recStart = recstart
            self.recEnd = recend
        


class Playlist(object):
        
    def __init__(self, songs, order):
        self.songs = []
        self.order = []
        for s in songs:
            self.songs.append(s)
        for o in order:
            self.order.append(o)
    
    def add(self, songs, order):
        for s in songs:
            self.songs.append(s)
        for o in order:
            self.order.append(o)
    
    def updateOrder(self, neworder):
        self.order = []
        for o in  neworder:
            self.order.append(o)

    def sendTable(self):
        tab = []
        for o in self.order:
            tab.append([self.songs[o].location,self.songs[o].bpm,self.songs[o].key])
        return tab

    
    def sendArtistTitleTable(self):
        tab = []
        for o in self.order:
            tab.append([self.songs[o].location,self.songs[o].artist,self.songs[o].title])
        return tab
    
    def sendLocationTable(self):
        tab = []
        for o in self.order:
            tab.append(self.songs[o].location)
        return tab
        

class NMLHandler(object):

    def loadFile(self, file):
        songs = []
        order = []
        nml = open(file, 'r')
        tree = et.parse(nml)
        root = et.fromstring(et.tostring(tree))
        for i in root:
            if i.tag=='COLLECTION':
                collection = i
                for entry in collection:
                    location = entry[0].get("VOLUME")+self.fixNMLlocation(entry[0].get("DIR")+entry[0].get("FILE"))
                    bpm,key,artist,title, playtime = 0,0,entry.get("ARTIST"), entry.get("TITLE"), 0.0
                    sections = []
                    for child in entry:
                        if child.tag=='TEMPO':
                            bpm = float(child.get("BPM"))
                        if child.tag=='MUSICAL_KEY':
                            key = int(child.get("VALUE"))
                        if child.tag=='INFO':
                                playtime = float(child.get("PLAYTIME"))
                        if child.tag=='CUE_V2':
                            if int(child.get("TYPE"))!=4:
                                sections.append(Section(float(child.get("START")),float(child.get("LEN")), "None"))
                    songs.append(Song(artist,title,bpm, key, location, sections,playtime))
            if i.tag =='PLAYLISTS':
                if i[0][0].tag=='SUBNODES':
                    for j in range(int(i[0][0].get("COUNT"))):
                        if i[0][0][j].get("TYPE")=="PLAYLIST":
                            currlist = i[0][0][j][0]
                            for entry in currlist:
                                for i, s in enumerate(songs):
                                    if str(s.location.split(fileHandler(''))[-1]) ==str(entry[0].get("KEY").split(':')[-1]):
                                        order.append(i)
                                
        nml.close
        print order
        return songs, order

    def saveFile(self, plist, oldfile, newfile):
        songs = []
        order = []
        defaultCueDict = {'NAME':'n.n.','DISPL_ORDER':'0','START':'0','LEN':'0','TYPE':'0','REPEATS':'-1','HOTCUE':'0'}
        defaultPlaylistDict = {'ENTRIES':'0','TYPE':'LIST','UUID':'0'}
        defaultPlaylistSongDict = {'TYPE':'TRACK','KEY':''}
        nml = open(oldfile, 'r')
        tree = et.parse(nml)
        root = et.fromstring(et.tostring(tree))
        for i in root:
            if i.tag=='COLLECTION':
                collection = i
                for j,entry in enumerate(collection):
                    #for child in entry:
                    #    if child.tag=='CUE_V2':
                    #        if child.get("TYPE")!=5:
                    #            entry.remove(child)
                    startnode = et.Element('CUE_V2',defaultCueDict)
                    startnode.set("HOTCUE","3")
                    startnode.set("NAME","Start")
                    startnode.set("START",str(plist.songs[j].startsections[plist.songs[j].recStart].start))
                    entry.append(startnode)
                    endnode = et.Element('CUE_V2',defaultCueDict)
                    endnode.set("HOTCUE","4")
                    endnode.set("NAME","End")
                    endnode.set("START",str(plist.songs[j].endsections[plist.songs[j].recEnd].start))
                    entry.append(endnode)
            if i.tag =='PLAYLISTS':
                if i[0][0].tag=='SUBNODES':
                    for j in range(int(i[0][0].get("COUNT"))):
                        i[0][0].remove(i[0][0][j])    
                    #    if i[0][0][j].get("TYPE")=="PLAYLIST":
                    numOfPlaylists = int(i[0][0].get("COUNT"))
                    #numOfPlaylists += 1
                    #i[0][0].set("COUNT", str(numOfPlaylists))
                    newplist = et.Element('PLAYLIST',defaultPlaylistDict)
                    newplist.set('ENTRIES',str(len(plist.songs)))
                    newplist.set('UUID',uuid.uuid4().hex)
                    newlist = et.Element('NODE',{'TYPE':'PLAYLIST','NAME':'Smoosic list'})
                    newlist.append(newplist)
                    i[0][0].append(newlist)
                    for o in plist.order:
                            key = ""
                            for sub in plist.songs[o].location.split("\\"):
                                    key += sub + "/:"
                            key = key[:-2]
                            entry = et.Element('ENTRY')
                            song = et.Element('PRIMARYKEY',defaultPlaylistSongDict)
                            song.set('KEY',str(key))
                            entry.append(song)
                            i[0][0][0][numOfPlaylists-1].append(entry)
                                
        nml.close
        try:
                et.ElementTree(root).write(str(newfile))
        except IOError:
                print "Error: cannot save current XML document!"
                return 0
        return 1

    def fixNMLlocation(self, wrongstring):
        newstring = ''
        for s in wrongstring.split('/'):
            if len(s)>1:
                newstring+=fileHandler(s[1:])
        return newstring

if __name__ == '__main__':
    nmlhandler = NMLHandler()
    one,  two = nmlhandler.loadFile('/home/hugo/EcpliseWorkspaceC++/PlaylistBuilder/test.nml')
    pl = Playlist(one,  two)
    for s in pl.songs:
        print s.track,  s.artist
