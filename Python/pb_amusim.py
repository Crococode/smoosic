import sys
import os
import pb_functions
import pb_afe

if __name__ == '__main__':
	fin = open(sys.argv[1])
	songs = []
	for line in fin:
		songs.append(line.strip())
	fin.close
	pb_afe.afeImport(sys.argv[1], sys.argv[2])
	pb_functions.updateSeg(songs,sys.argv[2],4)
	pb_functions.orderList(sys.argv[1], sys.argv[2], 0)
	#pb_functions.comp2Songs(songs[0],songs[1], sys.argv[2])
	#segs = pb_functions.findSeg(song, sys.argv[2])
	#tfv = pb_functions.timbFV(song, sys.argv[2], segs[0], 50)
	#print tfv
