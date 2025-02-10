# This file is a part of:
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#  ███▄▄▄▄   ▀█████████▄     ▄████████     ███      ▄██████▄   ▄██████▄   ▄█
#  ███▀▀▀██▄   ███    ███   ███    ███ ▀█████████▄ ███    ███ ███    ███ ███
#  ███   ███   ███    ███   ███    █▀     ▀███▀▀██ ███    ███ ███    ███ ███
#  ███   ███  ▄███▄▄▄██▀    ███            ███   ▀ ███    ███ ███    ███ ███
#  ███   ███ ▀▀███▀▀▀██▄  ▀███████████     ███     ███    ███ ███    ███ ███
#  ███   ███   ███    ██▄          ███     ███     ███    ███ ███    ███ ███
#  ███   ███   ███    ███    ▄█    ███     ███     ███    ███ ███    ███ ███▌    ▄
#   ▀█   █▀  ▄█████████▀   ▄████████▀     ▄████▀    ▀██████▀   ▀██████▀  █████▄▄██
# __________________________________________________________________________________
# NBSTool is a tool to work with .nbs (Note Block Studio) files.
# Author: IoeCmcomc (https://github.com/IoeCmcomc)
# Programming language: Python
# License: MIT license
# Source codes are hosted on: GitHub (https://github.com/IoeCmcomc/NBSTool)
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾


import sys
from collections import namedtuple
from os.path import abspath, dirname, join, normpath
from typing import Tuple

# from main import __file__ as __mainfile__

MidiInstrument = namedtuple(
    "MidiInstrument", ("name", "nbs_instrument", "octave_shift", "short_name")
)
MidiDrum = namedtuple("MidiDrum", ("pitch", "name", "nbs_instrument", "nbs_pitch"))

# MIDI mapping are adapted from @u3002 mapping table
# https://gist.github.com/u3002/cf4daa83bc82b5917fc86fb23815578a
MIDI_INSTRUMENTS: Tuple[MidiInstrument, ...] = (
    MidiInstrument("Acoustic Grand Piano", 0, 0, "Grand Piano"),
    MidiInstrument("Bright Acoustic Piano", 15, 0, "Acoustic Piano"),
    MidiInstrument("Electric Grand Piano", 15, 0, "E. Grand Piano"),
    MidiInstrument("Honky-tonk Piano", 15, 0, "H.T. Piano"),
    MidiInstrument("Electric Piano 1", 15, 0, "E. Piano 1"),
    MidiInstrument("Electric Piano 2", 15, 0, "E. Piano 2"),
    MidiInstrument("Harpsichord", 5, 1, ""),
    MidiInstrument("Clavinet", 14, 0, ""),
    MidiInstrument("Celesta", 7, -2, ""),
    MidiInstrument("Glockenspiel", 7, -2, ""),
    MidiInstrument("Music Box", 7, -2, ""),
    MidiInstrument("Vibraphone", 10, 0, ""),
    MidiInstrument("Marimba", 10, 0, ""),
    MidiInstrument("Xylophone", 9, -2, ""),
    MidiInstrument("Tubular Bells", 7, -2, "T. Bells"),
    MidiInstrument("Dulcimer", 5, 1, ""),
    MidiInstrument("Drawbar Organ", 6, -1, "D. Organ"),
    MidiInstrument("Percussive Organ", 10, 0, "P. Organ"),
    MidiInstrument("Rock Organ", 6, -1, ""),
    MidiInstrument("Church Organ", 6, -1, ""),
    MidiInstrument("Reed Organ", 6, -1, ""),
    MidiInstrument("Accordion", 6, -1, ""),
    MidiInstrument("Harmonica", 6, -1, ""),
    MidiInstrument("Tango Accordion", 6, -1, "Bandoneon"),
    MidiInstrument("Acoustic Guitar (nylon)", 5, 1, "A.Guitar (nylon)"),
    MidiInstrument("Acoustic Guitar (steel)", 5, 1, "A.Guitar (steel)"),
    MidiInstrument("Electric Guitar (jazz)", 0, 0, "E.Guitar (jazz)"),
    MidiInstrument("Electric Guitar (clean)", 5, 1, "E.Guitar (clean)"),
    MidiInstrument("Electric Guitar (muted)", 1, 2, "E.Guitar (mute)"),
    MidiInstrument("Overdriven Guitar", 12, 2, "OD Guitar"),
    MidiInstrument("Distortion Guitar", 12, 2, "Dist. Guitar"),
    MidiInstrument("Guitar Harmonics", 5, 3, "Guitar H."),
    MidiInstrument("Acoustic Bass", 1, 2, "A. Bass"),
    MidiInstrument("Electric Bass (finger)", 1, 2, "E.Bass (finger)"),
    MidiInstrument("Electric Bass (pick)", 1, 2, "E.Bass (pick)"),
    MidiInstrument("Fretless Bass", 1, 2, ""),
    MidiInstrument("Slap Bass 1", 5, 1, ""),
    MidiInstrument("Slap Bass 2", 5, 1, ""),
    MidiInstrument("Synth Bass 1", 1, 2, ""),
    MidiInstrument("Synth Bass 2", 15, 0, ""),
    MidiInstrument("Violin", 6, -1, ""),
    MidiInstrument("Viola", 6, -1, ""),
    MidiInstrument("Cello", 6, -1, ""),
    MidiInstrument("Contrabass", 6, -1, ""),
    MidiInstrument("Tremolo Strings", 6, -1, "T. Strings"),
    MidiInstrument("Pizzicato Strings", 1, 2, "P. Strings"),
    MidiInstrument("Orchestral Harp", 0, 0, "O. Harp"),
    MidiInstrument("Timpani", 3, 0, ""),
    MidiInstrument("String Ensemble 1", 6, -1, "String E. 1"),
    MidiInstrument("String Ensemble 2", 6, -1, "String E. 2"),
    MidiInstrument("Synth Strings 1", 6, -1, "S. Strings 1"),
    MidiInstrument("Synth Strings 2", 6, -1, "S. Strings 2"),
    MidiInstrument("Choir Aahs", 6, -1, ""),
    MidiInstrument("Voice Oohs", 6, -1, ""),
    MidiInstrument("Synth Choir", 6, -1, ""),
    MidiInstrument("Orchestra Hit", 3, -1, "O. Hit"),
    MidiInstrument("Trumpet", 6, -1, ""),
    MidiInstrument("Trombone", 6, -1, ""),
    MidiInstrument("Tuba", 6, -1, ""),
    MidiInstrument("Muted Trumpet", 12, 2, ""),
    MidiInstrument("French Horn", 6, -1, ""),
    MidiInstrument("Brass Section", 12, 2, ""),
    MidiInstrument("Synth Brass 1", 12, 2, "S. Brass 1"),
    MidiInstrument("Synth Brass 2", 6, -1, "S. Brass 2"),
    MidiInstrument("Soprano Sax", 6, -1, ""),
    MidiInstrument("Alto Sax", 6, -1, ""),
    MidiInstrument("Tenor Sax", 6, -1, ""),
    MidiInstrument("Baritone Sax", 6, -1, ""),
    MidiInstrument("Oboe", 6, -1, ""),
    MidiInstrument("English Horn", 6, -1, ""),
    MidiInstrument("Bassoon", 6, -1, ""),
    MidiInstrument("Clarinet", 6, -1, ""),
    MidiInstrument("Piccolo", 6, -1, ""),
    MidiInstrument("Flute", 6, -1, ""),
    MidiInstrument("Recorder", 6, -1, ""),
    MidiInstrument("Pan Flute", 6, -1, ""),
    MidiInstrument("Blown Bottle", 6, -1, ""),
    MidiInstrument("Shakuhachi", 6, -1, ""),
    MidiInstrument("Whistle", 6, -1, ""),
    MidiInstrument("Ocarina", 6, -1, ""),
    MidiInstrument("Lead 1 (square)", 13, 0, "L.1 (square)"),
    MidiInstrument("Lead 2 (sawtooth)", 6, -1, "L.2 (sawtooth)"),
    MidiInstrument("Lead 3 (calliope)", 6, -1, "L.3 (calliope)"),
    MidiInstrument("Lead 4 (chiff)", 6, -1, "L.4 (chiff)"),
    MidiInstrument("Lead 5 (charang)", 5, 1, "L.5 (charang)"),
    MidiInstrument("Lead 6 (voice)", 6, -1, "L.6 (voice)"),
    MidiInstrument("Lead 7 (fifths)", 6, -1, "L.7 (fifths)"),
    MidiInstrument("Lead 8 (bass + lead)", 1, 2, "L.8 (bass + lead)"),
    MidiInstrument("Pad 1 (new age)", 7, -2, "P.1 (new age)"),
    MidiInstrument("Pad 2 (warm)", 6, -1, "P.2 (warm)"),
    MidiInstrument("Pad 3 (polysynth)", 6, -1, "P.3 (polysynth)"),
    MidiInstrument("Pad 4 (choir)", 6, -1, "P.4 (choir)"),
    MidiInstrument("Pad 5 (bowed)", 6, -1, "P.5 (bowed)"),
    MidiInstrument("Pad 6 (metallic)", 6, -1, "P.6 (metallic)"),
    MidiInstrument("Pad 7 (halo)", 6, -1, "P.7 (halo)"),
    MidiInstrument("Pad 8 (sweep)", 8, -2, "P.8 (sweep)"),
    MidiInstrument("FX 1 (rain)", 8, -2, "Fx (rain)"),
    MidiInstrument("FX 2 (soundtrack)", 6, -1, "Fx (strack)"),
    MidiInstrument("FX 3 (crystal)", 8, -2, "Fx (crystal)"),
    MidiInstrument("FX 4 (atmosphere)", 5, 1, "Fx (atmosph.)"),
    MidiInstrument("FX 5 (brightness)", 15, 0, "Fx (bright.)"),
    MidiInstrument("FX 6 (goblins)", 6, -1, "Fx (goblins)"),
    MidiInstrument("FX 7 (echoes)", 6, -1, "Fx (echoes)"),
    MidiInstrument("FX 8 (sci-fi)", 5, 1, "Fx (sci-fi)"),
    MidiInstrument("Sitar", 14, 0, ""),
    MidiInstrument("Banjo", 14, 0, ""),
    MidiInstrument("Shamisen", 14, 0, ""),
    MidiInstrument("Koto", 5, 1, ""),
    MidiInstrument("Kalimba", 10, 0, ""),
    MidiInstrument("Bag pipe", 6, -1, ""),
    MidiInstrument("Fiddle", 6, -1, ""),
    MidiInstrument("Shanai", 6, -1, ""),
    MidiInstrument("Tinkle Bell", 8, -2, ""),
    MidiInstrument("Agogo", 11, -1, ""),
    MidiInstrument("Steel Drums", 10, 0, ""),
    MidiInstrument("Woodblock", 9, -2, ""),
    MidiInstrument("Taiko Drum", 2, 0, ""),
    MidiInstrument("Melodic Tom", 3, 0, ""),
    MidiInstrument("Synth Drum", 3, 0, ""),
    MidiInstrument("Reverse Cymbal", 8, -2, "Rev. Cymbal"),
    MidiInstrument("Guitar Fret Noise", 4, 1, "Guitar F. Noise"),
    MidiInstrument("Breath Noise", 6, -1, ""),
    MidiInstrument("Seashore", 8, -2, ""),
    MidiInstrument("Bird Tweet", 6, 1, ""),
    MidiInstrument("Telephone Ring", 7, 2, "Telephone"),
    MidiInstrument("Helicopter", 2, 0, ""),
    MidiInstrument("Applause", 3, 0, ""),
    MidiInstrument("Gunshot", 3, 0, ""),
    MidiInstrument("Percussion", -1, 0, ""),
)

MIDI_DRUMS = (
    MidiDrum(24, "Cutting Noise", -1, 0), #13 39
    MidiDrum(25, "Snare Roll", 3, 8),
    MidiDrum(26, "Finger Snap", 4, 25),
    MidiDrum(27, "High Q", 3, 18),
    MidiDrum(28, "Slap", 3, 27),
    MidiDrum(29, "Scratch Push", 4, 16),
    MidiDrum(30, "Scratch Pull", 4, 13),
    MidiDrum(31, "Sticks", 4, 9),
    MidiDrum(32, "Square Click", 4, 6),
    MidiDrum(33, "Metronome Click", 4, 2),
    MidiDrum(34, "Metronome Bell", 4, 17), #8 17
    MidiDrum(35, "Bass Drum 2", 2, 10),
    MidiDrum(36, "Bass Drum 1", 2, 6),
    MidiDrum(37, "Side Stick", 4, 6),
    MidiDrum(38, "Acoustic Snare", 3, 8),
    MidiDrum(39, "Hand Clap", 4, 6),
    MidiDrum(40, "Electric Snare", 3, 4),
    MidiDrum(41, "Low Floor Tam", 2, 6),
    MidiDrum(42, "Closed Hi-hat", 3, 22),
    MidiDrum(43, "High Floor Tom", 2, 13),
    MidiDrum(44, "Pedal Hi-hat", 3, 22),
    MidiDrum(45, "Low Tom", 2, 15),
    MidiDrum(46, "Open Hi-hat", 3, 18),
    MidiDrum(47, "Low-mid Tom", 2, 20),
    MidiDrum(48, "Hi-mid Tom", 2, 23),
    MidiDrum(49, "Crash Cymbal 1", 3, 17),
    MidiDrum(50, "High Tom", 2, 23),
    MidiDrum(51, "Ride Cymbal 1", 3, 24),
    MidiDrum(52, "Chinese Cymbal", 3, 8),
    MidiDrum(53, "Ride Bell", 3, 13),
    MidiDrum(54, "Tambourine", 4, 18),
    MidiDrum(55, "Splash Cymbal", 3, 18),
    MidiDrum(56, "Cowbell", 4, 1), # 11 5
    MidiDrum(57, "Crash Cymbal 2", 3, 13),
    MidiDrum(58, "Vibraslap", 4, 2),
    MidiDrum(59, "Ride Cymbal 2", 3, 13),
    MidiDrum(60, "High Bongo", 4, 9),
    MidiDrum(61, "Low Bongo", 4, 2),
    MidiDrum(62, "Mute High Conga", 4, 8),
    MidiDrum(63, "Open High Conga", 2, 22),
    MidiDrum(64, "Low Conga", 2, 15),
    MidiDrum(65, "High Timbale", 3, 13),
    MidiDrum(66, "Low Timbale", 3, 8),
    MidiDrum(67, "High Agogo", 4, 8), #9 12
    MidiDrum(68, "Low Agogo", 4, 3), #9 15
    MidiDrum(69, "Cabasa", 4, 20),
    MidiDrum(70, "Maracas", 4, 23),
    MidiDrum(71, "Short Whistle", 4, 23), #6 34
    MidiDrum(72, "Long Whistle", 4, 23), #6 33
    MidiDrum(73, "Short Guiro", 4, 17),
    MidiDrum(74, "Long Guiro", 4, 11),
    MidiDrum(75, "Claves", 4, 18),
    MidiDrum(76, "High Wood Block", 4, 10),
    MidiDrum(77, "Low Wood Block", 4, 5),
    MidiDrum(78, "Mute Cuica", 3, 4), #12 25
    MidiDrum(79, "Open Cuica", 3, 16), #12 26
    MidiDrum(80, "Mute Triangle", 4, 16),
    MidiDrum(81, "Open Triangle", 4, 22), #8 19
    MidiDrum(82, "Shaker", 3, 22),
    MidiDrum(83, "Jingle Bell", -1, 0), #8 6
    MidiDrum(84, "Bell Tree", -1, 0), #8 15
    MidiDrum(85, "Castanets", 4, 21),
    MidiDrum(86, "Mute Surdo", 2, 14),
    MidiDrum(87, "Open Surdo", 2, 7),
)

NBS_PITCH_IN_MIDI_PITCHBEND = 40.96
SOUND_FOLDER = "sounds"

BASE_RESOURCE_PATH = ''
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): # PyInstaller
    BASE_RESOURCE_PATH = sys._MEIPASS # type: ignore
elif '__compiled__' in globals(): # Nuitka
    BASE_RESOURCE_PATH = dirname(__file__)
else:
    BASE_RESOURCE_PATH = abspath('.')
assert BASE_RESOURCE_PATH != ''

def resource_path(*args: str):
    return normpath(join(BASE_RESOURCE_PATH, *args))