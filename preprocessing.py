from music21 import converter,instrument, note, chord, stream, duration, meter
import numpy as np
import mido
import copy
import os
from postprocessing import *
from os import listdir
from os.path import isfile, join, isdir

program_ranges = {\
				  "Piano": range(1,9), 
				  "Chromatic Percussion": range(9,17), 
				  "Organ": range(17,25),
				  "Guitar": range(25,33) , 
				  "Bass": range(33,41),
				  "Strings": range(41,49),
				  "Ensemble": range(49,57),
				  "Brass": range(57,65),
				 }
allowed_programs = ["Guitar"]

durations_to_num = {"whole": 16, "half": 8, "quarter": 4, "eighth": 2, "16th": 1, "32nd": 0, "64th": 0, "zero": 0, "breve": 32, "longa": 64,"maxima": 128}
num_to_durations = {16: "whole", 8: "half", 4: "quarter", 2: "eighth", 1: "16th" , 0: "32nd", 0: "64th", 0: "zero" , 32: "breve", 64: "longa", 128: "maxima"}
duration_lst = [128, 64, 32, 16, 8, 4, 2, 1, 0]

'''
Filesystem functions
'''

def getRelativePathToMidi(name):
	fileDir = os.path.dirname(os.path.realpath('__file__'))
	path = os.path.join(fileDir, 'midi-files', 'Songs', name)
	print("PATH=",path)
	return path

def getTrackRelativePath(name, dirname="Tracks", i=None):
	if i is None:
		i = ""
	fileDir = os.path.dirname(os.path.realpath('__file__'))
	fileDir = os.path.join(fileDir, 'midi-files', dirname, name.strip(".mid"))
	if not os.path.exists(fileDir):
		print("creating new dir: ",fileDir)
		os.makedirs(fileDir)
	return os.path.join(fileDir, "{0}_{1}.mid".format(name.strip(".mid"), i))



'''
Filtering Functions
'''
def convertTimeSignature(midi):
	midiCopy = copy.deepcopy(midi)
	for track in midiCopy.tracks:
		for msg in track:
			if msg.is_meta and msg.type=='time_signature':
				msg.numerator, msg.denominator = 4, 4
	return midiCopy

def filterProgramChangeTracks(midi):
	valid_tracks= []
	#print("filterProgramChangeTracks: Original midi containing {0} tracks".format(len(midi.tracks)))
	for track in midi.tracks:
		is_valid_tr = True
		for msg in track:
			if msg.type == "note_on" and msg.channel == 9:
				is_valid_tr = False
				break
			if msg.is_meta and msg.type=='time_signature':
				if msg.denominator != 4 or (msg.numerator not in [1,2,4]):
					is_valid_tr = False
					break
			if msg.type=="program_change":
				temp = False
				for pr in allowed_programs:
					pr_range = program_ranges[pr]
					if msg.program in pr_range:
						temp = True
						break
				if temp == False:
					#print("track {0} invalid".format(track.name))
					is_valid_tr = False
					break
						 
		if is_valid_tr:
			valid_tracks.append(track)
	#print("filterProgramChangeTracks: {0} Tracks are valid after filtering".format(len(valid_tracks)))
	return valid_tracks




'''
Midi to Matrix and Matrix to Midi
=================
'''

def breakQuarterLength(q):
    q = int(q)
    instances = 0
    
    while q > 4:
        instances += (q // 4) * 16
        q = q % 4
    if q == 3:
        return instances + 10
    if q == 2:
        return instances + 8
    if q == 1:
        return instances + 2
    return instances

def getInstances(element):
	#get number of instances from duration
	#print(element)
	if isinstance(element, str):
		if element in durations_to_num:
			return durations_to_num[element]
		else:
			return 0
	return int(element.duration.quarterLength * 4)
	'''
	else:
		instances = 0
		if element.duration.type == "complex":
			for t, d, q in element.duration.components:
				print((t,d,q))
				instances +=  getInstances(t)
		elif element.duration.type == "inexpressible":
			element.duration.quarterLength = element.duration.quarterLength
			for t, d, q in element.duration.components:
				broken = breakQuarterLength(q)
				#print("broken to {0} instances".format(broken))
				instances +=  breakQuarterLength(q)
			
		elif element.duration.type in durations_to_num:
			instances += durations_to_num[element.duration.type]
		return instances
	'''

def getNoteMatrix(notes_to_parse):
	notes = np.zeros((72,7000), dtype=int)
	#notes = notes.reshape((72,7000))
	for element in notes_to_parse:
		if element.offset > 7000//4:
			break
		#print("============")
		#calculate duration
		instances = getInstances(element)
		#print("element {0}, with {1} qlength is {2} instances at offset {3}".format(element, element.duration.quarterLength, instances, element.offset))		
		if isinstance(element, note.Note):
			noteVec = np.zeros(72, dtype=int)
			pitch_i = (element.pitch.pitchClass - 4) + 12 * (element.octave - 2)
			#print("converted pitch {0} octave {1} to index {2}".format(element.pitch.pitchClass, element.octave, pitch_i))
			for j in range(instances):
				if pitch_i in range(72):
					notes[pitch_i,int(element.offset*4) + j] = 1
		elif isinstance(element, chord.Chord):
			instances = getInstances(element)
			noteVec = np.zeros(72, dtype=int)
			for n in element:
				pitch_i = (n.pitch.pitchClass - 4) + 12 * (n.octave - 2)
				for j in range(instances):
					if pitch_i in range(72):
						notes[pitch_i,int(element.offset*4)+j] = 1
		else:
			#print("got weird element {0}, dropping".format(element))
			continue
	np.set_printoptions(threshold=np.nan)
	#print(notes[:,0:16])
	return notes
		#if instances != 0:
				#notes = np.concatenate((notes,newNotes),axis=1)
	



'''
separate Midi to appropriate tracks
'''
def separateToTracks(filename):
	try:
		path = getRelativePathToMidi(filename)
		midiFile = mido.MidiFile(path)
	except:
	    print("Can't open {0}".format(path))
	    return
	midiFile = mido.MidiFile(getRelativePathToMidi(filename))
	print(midiFile.ticks_per_beat)
	resMidi = convertTimeSignature(midiFile)
	tracks = filterProgramChangeTracks(resMidi)
	count = 1
	for i, track in enumerate(tracks):
		if len(track[:10]) < 10:
			print("separateToTracks: {0} is an empty track", i)
			continue
		mid = mido.MidiFile()
		#print('Track {}: {}'.format(i, track.name))
		mid.tracks.append(track)
		mid.ticks_per_beat = midiFile.ticks_per_beat
		newpath = getTrackRelativePath(filename, count)
		mid.save(newpath) #dump the midi to file
		print("SAVED Track: ", newpath)
		count += 1
	print("Separated tracks with ticks_per_beat: {0}".format(midiFile.ticks_per_beat))
	return midiFile.ticks_per_beat



'''
Convert
'''
def convertTrackToMat(filename, dirname="Tracks", track_no = None, isFullPath=False):
	if not isFullPath:
		midi = converter.parse(getTrackRelativePath(filename, dirname, track_no))
	else:
		try:
			midi = converter.parse(filename)
		except:
			print("Skipping: {0}".format(filename))
			return
	parts = instrument.partitionByInstrument(midi)
	notes_to_parse = None
	if parts: # file has instrument parts
		print(parts)
		notes_to_parse = parts.parts[0].recurse()
		noteMat = getNoteMatrix(notes_to_parse)
		return noteMat
	if notes_to_parse is None:
		print("No instruments to parse")
		return
	
def convertTrackNoInstruments(filepath):
    stream = converter.parseFile(filepath)
    notes_to_parse = None
    if stream: # file has instrument parts
        #stream.show("text")
        print(len(stream))
        noteMat = getNoteMatrix(stream.recurse())
        return noteMat
    if notes_to_parse is None:
        print("No instruments to parse")
        return

def processSongs(filename=None):
	if filename is not None:
		tpb = separateToTracks(filename)
	else:
		# get every song name
		fileDir = os.path.dirname(os.path.realpath('__file__'))
		fileDir = os.path.join(fileDir, 'midi-files', "Songs")
		onlyfiles = [f for f in listdir(fileDir) if isfile(join(fileDir, f))]
		for f in onlyfiles:
			print(f)
			separateToTracks(f)
#Show Time
specific_file = "Offspring_pretty_fly.mid"


def smushSongs(dirname):
	fileDir = os.path.dirname(os.path.realpath('__file__'))
	fileDir = os.path.join(fileDir, 'midi-files', "Tracks", dirname)
	onlyfiles = [f for f in listdir(fileDir) if isfile(join(fileDir, f))]
	mats = []
	for f in onlyfiles:
		if f.split(".")[1] != "mid":
			continue
		print(f)
		converted = convertTrackToMat(os.path.join(fileDir, f), "",None,isFullPath=True)
		if converted is not None:
			mats.append(converted)
	if len(mats) > 0:
		newMat = np.zeros(mats[0].shape, dtype=int)
		for mati, mat in enumerate(mats):
			for i in range(newMat.shape[0]):
				for j in range(newMat.shape[1]):
					if mat[i,j] == 1:
						newMat[i,j] = 1
		convertMatToTrack(newMat, 480, os.path.join("Smushed", dirname+".mid"))

#processSongs()

def smushAll():
	fileDir = os.path.dirname(os.path.realpath('__file__'))
	fileDir = os.path.join(fileDir, 'midi-files', "Tracks")
	onlydirs = [f for f in listdir(fileDir) if isdir(join(fileDir, f))]
	for directory in onlydirs:
		smushSongs(directory)
#smushAll()
#tpb = separateToTracks(filename)
#noteMat = convertTrackToMat(filename, 1)

#if noteMat is not None:
	#convertMatToTrack(noteMat, tpb, "recovered.mid")

