from lxml import etree as et
from sys import platform

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
        if length >= 0:
            self.length = length
            self.end = start + length
        else:
            self.length = DEFAULT_LEN
            self.end = start + DEFAULT_LEN
        self.label = label
        
    def toFrames(self):
            return int(self.start * TO_FRAMES), int(self.length * TO_FRAMES)

    def fromFrames(self):
        self.start *= FROM_FRAMES
        self.length *= FROM_FRAMES
        #return self

        
class Song(object):
    #bpm = 0
    #location = ''
    #artist = ''
    #title = ''
    #key = 0
    #sections = []
    #startsections = []
    #endsections =[]
    #playtime = 0.0
    
    #def __init__(self, artist, title, bpm, key, location, sections):
    #    self.bpm = bpm
    #    self.artist = artist
    #    self.title = title
    #    self.location = location
    #    self.key = key
    #    for sec in sections:
    #        self.sections.append(sec)

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
                for sec in sections:
                        if sec.start < middle:
                                self.startsections.append(sec)
                        else:
                                self.endsections.append(sec)
        else:
                for sec in sections:
                        self.sections.append(sec)
                        
    def addSectionList(self, startsecs,endsecs):
        for ssec in startsecs:
                self.startsections.append(ssec)
        for ssec in endsecs:
                self.endsections.append(ssec)
        

    
    #def Song(artist, track,  bpm, key, location, sections):
    #    self.bpm = bpm
    #    self.artist = artist
    #    self.track = track
    #    self.key = key
    #    self.location = location
    #    self.sections = sections


class Playlist(object):
    #songs = []
    #order =[]
        
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
                            if child.get("TYPE")==5:
                                sections.append(Section(child.get("START"),child.get("LEN"), "None"))
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
