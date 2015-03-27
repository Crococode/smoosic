#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

This program creates a quit
button. When we press the button,
the application terminates. 

author: Jan Bodnar
website: zetcode.com 
last edited: October 2011
"""

import sys
import os
import pb_functions as pb
import pb_nml as nml
from PyQt4 import QtGui, QtCore

class playlistTable(QtGui.QWidget):
    def __init__(self):
        super(playlistTable, self).__init__()
    
    def addList(self, list):
        grid = QtGui.QGridLayout()
        for i, song in enumerate(list):
            grid.addWidget(QtGui.QLabel(song))
        self.setLayout(grid)
    

class Example(QtGui.QMainWindow):
    
    fname = ''
    songs = []
    featureplan = os.path.dirname(os.path.realpath(__file__))+'/featureplan.txt'
    start = str(0)
    
    
    def __init__(self):
        super(Example, self).__init__()
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
        startEdit = QtGui.QLineEdit(self.start)
        grid.addWidget(startEdit, 0, 0, QtCore.Qt.AlignLeft);
        grid.addWidget(self.pbTab, 1, 0,  QtCore.Qt.AlignLeft)
        self.setWindowIcon(QtGui.QIcon('web.png')) 
        qbtn = QtGui.QPushButton('Quit', self)
        qbtn.setToolTip('This is a <b>QPushButton</b> widget')
        #qbtn.clicked.connect(self.closeDialog())
        grid.addWidget(qbtn, 2, 0,  QtCore.Qt.AlignLeft)
        self.setToolTip('This is a <b>QWidget</b> widget')
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
        
        
        
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Quit button')    
        self.show()
        
    def exeDistanceMatrixMtlSmart(self):
        output = QtGui.QFileDialog.getSaveFileName(self, 'Output file', 
                os.path.dirname(os.path.realpath(__file__)))
        mat,sections, sentrys, eentrys = pb.distanceMatrixMtlSmart(self.songs, self.featureplan)
        pb.orderMatrixSmart(self.songs,mat,sections, sentrys, eentrys, int(self.start), output)

    
    def closeDialog(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)			
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()      
    
    def showOpenDialog(self):
        
        self.fname = QtGui.QFileDialog.getOpenFileName(self, 'Load playlist file', 
                os.path.dirname(os.path.realpath(__file__)))
        if QtCore.QFileInfo(self.fname).suffix() == "nml":
            print "Loading NML File: ",  self.fname
            songs,  order = nml.NMLHandler().loadFile(self.fname)
            self.list.add(songs, order)
            txtlist = []
            for i in songs:
                txtlist.append(i.location)
            self.pbTab.addList(txtlist)
            return
        fin = open(self.fname)
        print "Loading TXT File: ",  self.fname
        for line in fin:
            self.songs.append(line.strip())
        fin.close
        #self.centralWidget().layout().itemAtPosition(1, 0).widget().addList(self.songs)
        self.list.add(self.songs, '')
        
    
    def showOpenFeatDialog(self):

        self.featureplan = QtGui.QFileDialog.getOpenFileName(self, 'Load featureplan file', 
                os.path.dirname(os.path.realpath(__file__)))
        

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
