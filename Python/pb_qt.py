#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import pb_functions as pb
import pb_nml as nml
import pb_afe as afe
from PyQt4 import QtGui, QtCore

class playlistTable(QtGui.QWidget):
    lay = QtGui.QVBoxLayout()
    def __init__(self):
        super(playlistTable, self).__init__()
        self.setLayout(self.lay)
    
    def addList(self, list, name):
        try:
            currentTable = self.lay.takeAt(0).widget()
            currentTable.deleteLater()
        except AttributeError:
            pass
        table_model = playlistTableModel(self, list, name)
        table_view = QtGui.QTableView()
        table_view.setModel(table_model)
        table_view.resizeColumnsToContents()
        self.lay.addWidget(table_view)

class playlistTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
    def rowCount(self, parent):
        return len(self.mylist)
    def columnCount(self, parent):
        return len(self.mylist[0])
    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None
    

class Gui(QtGui.QMainWindow):
    
    #fname = ''
    #featureplan = os.path.dirname(os.path.realpath(sys.argv[0]))+pb.fileHandler('featureplan.txt')
    start = str(0)
    timelineMode = True
    bpmVal = 50
    keyVal = 50
    
    
    def __init__(self):
        super(Gui, self).__init__()
        grid = QtGui.QGridLayout()
        self.pbTab = playlistTable()
        self.list = nml.Playlist([],[])
        self.keyEdit = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.keyEdit.setRange(0,99)
        self.keyEdit.setValue(self.keyVal)
        self.keyEdit.setStatusTip('Change key sensitivity for playlist optimization')
        self.keyLabel = QtGui.QLabel('Key sensitivity: ')
        self.bpmEdit = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.bpmEdit.setRange(0,99)
        self.bpmEdit.setValue(self.bpmVal)
        self.bpmEdit.setStatusTip('Change BPM sensitivity for playlist optimization')
        self.bpmLabel = QtGui.QLabel('BPM sensitivity: ')
        self.initUI()
        
    def initUI(self):               
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        wid = QtGui.QWidget()
        self.setCentralWidget(wid)
        grid = QtGui.QGridLayout()
        wid.setLayout(grid)
        
        self.timelineEdit = QtGui.QRadioButton(self)
        self.timelineEdit.setChecked(self.timelineMode)
        self.timelineEdit.setStatusTip('Switch between timeline and single vector mode')
        grid.addWidget(QtGui.QLabel('Timeline mode: '), 0, 0, QtCore.Qt.AlignLeft)
        grid.addWidget(self.timelineEdit, 0, 1, QtCore.Qt.AlignLeft)
        self.startEdit = QtGui.QLineEdit(self.start)
        self.startEdit.setStatusTip('Choose first track for optimized playlist')
        grid.addWidget(QtGui.QLabel('First Track: '), 1, 0, QtCore.Qt.AlignLeft)
        grid.addWidget(self.startEdit, 1, 1, QtCore.Qt.AlignLeft)
        grid.addWidget(self.bpmLabel, 0, 2, QtCore.Qt.AlignLeft)
        grid.addWidget(self.bpmEdit,0, 3, QtCore.Qt.AlignLeft)        
        grid.addWidget(self.keyLabel, 1, 2, QtCore.Qt.AlignLeft)
        grid.addWidget(self.keyEdit, 1, 3, QtCore.Qt.AlignLeft)        
        grid.addWidget(self.pbTab, 3, 0, 1 , 8)
        
        self.statusBar().showMessage('Ready')
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        self.connect(exitAction, QtCore.SIGNAL("clicked()"), self.closeDialog)
        openAction = QtGui.QAction( QtGui.QIcon('exit.png'),  '&Load playlist', self)    
        openAction.setShortcut('Ctrl+L')
        openAction.setStatusTip('Load Playlist file')
        openAction.triggered.connect(self.showOpenDialog)
        openFeatAction = QtGui.QAction( QtGui.QIcon('exit.png'),  'Load &featureplan', self)    
        openFeatAction.setShortcut('Ctrl+F')
        openFeatAction.setStatusTip('Load featureplan file')
        openFeatAction.triggered.connect(self.showOpenFeatDialog)
        distanceMatrixSmartAction = QtGui.QAction(QtGui.QIcon(), '&Optimise',  self)
        distanceMatrixSmartAction.setShortcut('Ctrl+O')
        distanceMatrixSmartAction.setStatusTip('Optimise current list')
        distanceMatrixSmartAction.triggered.connect(self.exeDistanceMatrixMtlSmart)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        toolMenu = menubar.addMenu('&Tools')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(openFeatAction)
        toolMenu.addAction(distanceMatrixSmartAction)
        
        self.setGeometry(200, 200, 800, 400)
        self.setWindowTitle('Smoosic 1.0')
        self.featureplan = os.path.dirname(os.path.realpath(sys.argv[0]))+pb.fileHandler('featureplan.txt')
        self.show()
        
    def exeDistanceMatrixMtlSmart(self):
        #output = QtGui.QFileDialog.getSaveFileName(self, 'Output file', 
        #       os.path.dirname(os.path.realpath(sys.argv[0])))
        output = "C:\Users\Hugo\Desktop\Code\AFE\outNu.txt"
        print ""
        print ""
        self.statusBar().showMessage('Importing music to AFE Database')
        afe.afeImport(self.list.songs, self.featureplan)
        self.statusBar().showMessage('Updating timelines')
        pb.updateMtlDatabase(self.list.songs, self.featureplan,4)
        if self.bpmLabel.isEnabled() == True:
            self.statusBar().showMessage('Starting distance matrix calculation')
            if self.timelineEdit.isChecked() == True:
                self.list.songs,mat, ssections, esections = pb.distanceMatrixMtlKB(self.list.songs, self.featureplan, self.bpmEdit.value()/100.0, self.keyEdit.value()/100.0)
                self.statusBar().showMessage('Sorting distance matrix')
                final, ssections, esections = pb.orderMatrixSmart(self.list.songs,mat,ssections, esections, self.list.order[int(self.startEdit.text())])
                pb.printOrder(self.list.songs, final, ssections, esections , output)
            else:
                pb.updateSeg(self.list.sendLocationTable(), self.featureplan, 1)
                mat = pb.distanceMatrixKB(self.list.songs, self.featureplan, self.bpmEdit.value()/100.0, self.keyEdit.value()/100.0)
                self.statusBar().showMessage('Sorting distance matrix')
                final = pb.orderMatrix(self.list.songs,mat, self.list.order[int(self.startEdit.text())], output)
            self.list.updateOrder(final)
            self.pbTab.addList(self.list.sendTable(), ['File','BPM', 'Key'])
            
        else:
            self.statusBar().showMessage('Starting distance matrix calculation')
            if self.timelineEdit.isChecked() == True:
                self.list.songs,mat, ssections, esections = pb.distanceMatrixMtl(self.list.songs, self.featureplan)
                self.statusBar().showMessage('Sorting distance matrix')
                final, ssections, esections = pb.orderMatrixMtl(self.list.songs,mat,ssections, esections, self.list.order[int(self.startEdit.text())])
                pb.printOrder(self.list.songs, final, ssections, esections , output)
            else:
                pb.updateSeg(self.list.songs, self.featureplan, 1)
                mat = pb.distanceMatrix(self.list.songs, self.featureplan)
                self.statusBar().showMessage('Sorting distance matrix')
                final = pb.orderMatrix(self.list.songs,mat, self.list.order[int(self.startEdit.text())], output)
            self.list.updateOrder(final)
            self.pbTab.addList(self.list.sendArtistTitleTable(), ['File','Artist', 'Title'])
        self.statusBar().showMessage('Ready')

    
    def closeDialog(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)			
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()      
    
    def showOpenDialog(self):
        
        #self.fname = QtGui.QFileDialog.getOpenFileName(self, 'Load playlist file', 
        #        os.path.dirname(os.path.realpath(sys.argv[0])))
        self.fname = "C:\Users\Hugo\Desktop\Test.nml"
        self.statusBar().showMessage('Opening: '+self.fname)
        if QtCore.QFileInfo(self.fname).suffix() == "nml":
            print "Loading NML File: ",  self.fname
            songs,  order = nml.NMLHandler().loadFile(self.fname)
            self.list.add(songs, order)
            txtlist = []
            for i in songs:
                txtlist.append(i.location)
            self.pbTab.addList(self.list.sendTable(), ['File','BPM', 'Key'])
            self.statusBar().showMessage('Ready')
            self.bpmLabel.setEnabled(True)
            self.keyLabel.setEnabled(True)
            self.bpmEdit.setEnabled(True)
            self.keyEdit.setEnabled(True)
            return
        fin = open(self.fname)
        print "Loading TXT File: ",  self.fname
        songs = []
        for line in fin:
            songs.append(nml.Song(' ',' ',0,0,line.strip(),[], 0.0))
        fin.close()
        self.list.add(songs,range(len(songs)))
        self.pbTab.addList(self.list.sendArtistTitleTable(), ['File','Artist', 'Title'])
        self.bpmLabel.setEnabled(False)
        self.keyLabel.setEnabled(False)
        self.bpmEdit.setEnabled(False)
        self.keyEdit.setEnabled(False)
        self.statusBar().showMessage('Ready')
        
        
        
    
    def showOpenFeatDialog(self):

        self.featureplan = QtGui.QFileDialog.getOpenFileName(self, 'Load featureplan file', 
                os.path.dirname(os.path.realpath(sys.argv[0])))


        
        

def main():
    
    app = QtGui.QApplication(sys.argv)
    gui = Gui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
