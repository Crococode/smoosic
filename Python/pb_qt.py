#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import pb_functions as pb
import pb_nml as nml
import pb_afe as afe
from PyQt4 import QtGui, QtCore

class playlistTable(QtGui.QWidget):
    def __init__(self):
        super(playlistTable, self).__init__()
    
    def addList(self, list):
        grid = QtGui.QGridLayout()
        for i, song in enumerate(list):
            grid.addWidget(QtGui.QLabel(song))
        self.setLayout(grid)
    

class Gui(QtGui.QMainWindow):
    
    fname = ''
    songs = []
    featureplan = os.path.dirname(os.path.realpath(sys.argv[0]))+pb.fileHandler('featureplan.txt')
    start = str(0)
    timelineMode = True
    bpmVal = 0.5
    keyVal = 0.5
    
    
    def __init__(self):
        super(Gui, self).__init__()
        grid = QtGui.QGridLayout()
        self.pbTab = playlistTable()
        self.list = nml.Playlist([],[])
        self.initUI()
        
    def initUI(self):               
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        wid = QtGui.QWidget()
        self.setCentralWidget(wid)
        grid = QtGui.QGridLayout()
        wid.setLayout(grid)
        
        timelineEdit = QtGui.QRadioButton(self)
        timelineEdit.setChecked(self.timelineMode)
        grid.addWidget(QtGui.QLabel('Timeline mode: '), 0, 0, QtCore.Qt.AlignLeft)
        grid.addWidget(timelineEdit, 0, 1, QtCore.Qt.AlignLeft)
        startEdit = QtGui.QLineEdit(self.start)
        grid.addWidget(QtGui.QLabel('First Track: '), 1, 0, QtCore.Qt.AlignLeft)
        grid.addWidget(startEdit, 1, 1, QtCore.Qt.AlignLeft)
        bpmEdit = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        bpmEdit.setRange(0,1)
        bpmEdit.setValue(self.bpmVal)
        #bpmEdit.valueChanged.connect(self.bpmVal)
        grid.addWidget(QtGui.QLabel('BPM sensitivity: '), 0, 2, QtCore.Qt.AlignLeft)
        grid.addWidget(bpmEdit,0, 3, QtCore.Qt.AlignLeft)
        keyEdit = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        keyEdit.setRange(0,1)
        keyEdit.setValue(self.keyVal)
        #keyEdit.valueChanged.connect(self.keyVal)
        grid.addWidget(QtGui.QLabel('Key sensitivity: '), 1, 2, QtCore.Qt.AlignLeft)
        grid.addWidget(keyEdit, 1, 3, QtCore.Qt.AlignLeft)        
        grid.addWidget(self.pbTab, 3, 0, 1 , 4)
        
        self.statusBar().showMessage('Ready')
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        self.connect(exitAction, QtCore.SIGNAL("clicked()"), self.closeDialog)
        #exitAction.triggered.connect(self.closeDialog(QtGui.qApp.quit))
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
        
        self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('Smoosic 1.0')    
        self.show()
        
    def exeDistanceMatrixMtlSmart(self):
        output = QtGui.QFileDialog.getSaveFileName(self, 'Output file', 
                os.path.dirname(os.path.realpath(sys.argv[0])))
        self.statusBar().showMessage('Importing music to AFE Database')
        afe.afeImport(self.songs, self.featureplan)
        self.statusBar().showMessage('Updating timelines')
        pb.updateMtlDatabase(self.songs, self.featureplan,4)
        self.statusBar().showMessage('Starting distance matrix calculation')
        mat,sections, sentrys, eentrys = pb.distanceMatrixMtlSmart(self.songs, self.featureplan)
        self.statusBar().showMessage('Sorting distance matrix')
        pb.orderMatrixSmart(self.songs,mat,sections, sentrys, eentrys, int(self.start), output)
        self.statusBar().showMessage('Ready')

    
    def closeDialog(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)			
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()      
    
    def showOpenDialog(self):
        
        self.fname = QtGui.QFileDialog.getOpenFileName(self, 'Load playlist file', 
                os.path.dirname(os.path.realpath(sys.argv[0])))
        self.statusBar().showMessage('Opening: '+self.fname)
        if QtCore.QFileInfo(self.fname).suffix() == "nml":
            print "Loading NML File: ",  self.fname
            songs,  order = nml.NMLHandler().loadFile(self.fname)
            self.list.add(songs, order)
            txtlist = []
            for i in songs:
                txtlist.append(i.location)
            self.pbTab.addList(txtlist)
            self.statusBar().showMessage('Ready')
            return
        fin = open(self.fname)
        print "Loading TXT File: ",  self.fname
        for line in fin:
            self.songs.append(line.strip())
        fin.close
        #self.centralWidget().layout().itemAtPosition(1, 0).widget().addList(self.songs)
        self.list.add(self.songs, '')
        self.pbTab.addList(self.songs)
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
