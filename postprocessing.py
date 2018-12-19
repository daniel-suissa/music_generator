import mido
from music21 import converter,instrument, note, chord, stream, duration, meter
import numpy as np
import os
duration_lst = [128, 64, 32, 16, 8, 4, 2, 1, 0]

def breakInstances(num):
	if num in duration_lst:
		return [num]
	for d in duration_lst:
		if num > d:
			return [d] + breakInstances(num - d)
	print("Something went terribly wrong")



def createMidiFromMat(noteMat):
	new_notes_lst = []
	for i in range(noteMat.shape[0]):
		j = 0
		while j < noteMat.shape[1]:
			count = 1
			if int(noteMat[i,j]) == 1:
				while int(noteMat[i,j+count]) == 1:
					count += 1
				durations = breakInstances(count)
				newDuration = duration.Duration()
				qlength = 0.0
				#print(durations)
				for d in durations:
					qlength += d / 4.0
				newDuration.quarterLength = qlength
				octave = (i + 4) // 12 + 2
				pitchClass = ((i % 12) + 4) % 12
				newNote = note.Note(pitchClass)
				newNote.octave = octave
				newNote.duration = newDuration
				newNote.offset = j / 4.0
				new_notes_lst.append(newNote)
				#if i == 21:
					#print("NOTE: pitch: {0}, index {3}, duration: {1}, offset: {2}\n\n\n".format(pitchClass, newDuration.quarterLength, newNote.offset, j))

			j = j + count
	reconstructedMidi = stream.Stream(new_notes_lst)
	return reconstructedMidi
'''				
def createMidiFromMat(noteMat):
	
	i = 0
	print(noteMat)
	count = 0
	while i < noteMat.shape[1]:
		vec = noteMat[:,i]
		print(vec)
		instances = 1
		while i + instances < noteMat.shape[1] and np.all(noteMat[:,i + instances] == vec):
			instances += 1
		#print(instances)
		#get the list of durations
		durations = breakInstances(instances)
		#create duration
		newDuration = duration.Duration()
		qlength = 0.0
		#print(durations)
		for d in durations:
			qlength += d / 4.0
		newDuration.quarterLength = qlength
		print("next durations is {0} qlength for {1} instances".format(newDuration.quarterLength, instances))

		#create the note/chord/rest


		new_notes_lst = []
		for j,b in enumerate(vec):
			if int(b) == 1:
				octave = j // 12 + 2
				pitchClass = (j % 12) + 4 % 12
				newNote = note.Note(pitchClass)
				newNote.octave = octave
				newNote.duration = newDuration
				newNote.offset = i / 4.0
				new_notes_lst.append(newNote)
				print("NOTE: pitch: {0}, duration: {1}, offset: {2}\n\n\n".format(pitchClass, newDuration.quarterLength, newNote.offset))
		count += 1
		if count > 3:
			break
		i += instances
	reconstructedMidi = stream.Stream(new_notes_lst)
	return reconstructedMidi


'''

'''
if len(new_notes_lst) == 0:
	reconstructedMidi.append(note.Rest(newDuration.quarterLength))
	print("appended rest of {0} qlength".format(newDuration.quarterLength))
elif len(new_notes_lst) == 1:
	newNote = new_notes_lst[0]
	newNote.duration = newDuration
	reconstructedMidi.append(newNote)
else:
	newChord = chord.Chord(new_notes_lst)
	newChord.duration = newDuration
	reconstructedMidi.append(newChord)
print(reconstructedMidi[-1])
print("==========")
'''	

def fixTempo(filepath, ticks_per_beat):
	midiFile = mido.MidiFile(filepath)
	print('Setting ticks per beat to {0}'.format(midiFile.ticks_per_beat))
	midiFile.ticks_per_beat = ticks_per_beat
	midiFile.save(filepath) #dumpt to the same path

def convertMatToTrack(noteMat, ticks_per_beat, dest_filename):
	midi = createMidiFromMat(noteMat)
	fileDir = os.path.dirname(os.path.realpath('__file__'))
	path = os.path.join(fileDir, "midi-files", dest_filename)
	midi.write('midi', fp=path)
	#fixTempo(dest_filename, ticks_per_beat)
