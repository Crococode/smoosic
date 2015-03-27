from lxml import etree as et

class Song(object):
    bpm = 0
    location = ''
    artist = ''
    track = ''
    key = 0
    sections = []
    
    def __init__(self, artist, track, key, bpm, location, sections):
        self.bpm = bpm
        self.artist = artist
        self.track = track
        self.location = location
        self.sections = sections
    
    def Song(artist, track, key, bpm, location, sections):
        self.bpm = bpm
        self.artist = artist
        self.track = track
        self.location = location
        self.sections = sections


class Playlist(object):
    songs = []
    order =[]
        
    def __init__(self, songs, order):
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
                    location = entry[0].get("VOLUME")+entry[0].get("DIR")+entry[0].get("FILE")
                    songs.append(Song(entry.get("ARTIST"), entry.get("TITLE"),entry[3].get("BPM"), entry[5].get("VALUE"), location, '' ))
            if i.tag =='PLAYLISTS':
                if i[0][0].tag=='SUBNODES':
                    for j in range(int(i[0][0].get("COUNT"))):
                        if i[0][0][j].get("TYPE")=="PLAYLIST":
                            currlist = i[0][0][j][0]
                            for entry in currlist:
                                for i, s in enumerate(songs):
                                    if str(s.location) ==str(entry[0].get("KEY")):
                                        order.append(i)
                                
        nml.close
        print order
        return songs, order

if __name__ == '__main__':
    nmlhandler = NMLHandler()
    one,  two = nmlhandler.loadFile('/home/hugo/EcpliseWorkspaceC++/PlaylistBuilder/test.nml')
    pl = Playlist(one,  two)
    for s in pl.songs:
        print s.track,  s.artist
