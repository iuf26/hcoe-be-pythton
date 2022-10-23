import json
import wave
from enum import Enum


class DocumentWord:
    def __int__(self):
        self.word = None
        self.status = None


class WordStatus(Enum):
    WRONG = "wrong",
    MISSING = "missing",
    CORRECT = "correct"


class CutAudio:
    def __init__(self, filename):
        self.filename = filename
        self.nchannels = None
        self.sampwidth = None
        self.framerate = None
        self.start = None
        self.end = None
        self.cut_section = None

    def read_file(self):
        with wave.open(self.filename, "rb") as infile:
            # get file data
            self.nchannels = infile.getnchannels()
            self.sampwidth = infile.getsampwidth()
            self.framerate = infile.getframerate()
            # set position in wave to start of segment
            infile.setpos(int(self.start * self.framerate))
            # extract data
            self.cut_section = infile.readframes(int((self.end - self.start) * self.framerate))

    def write_audio_cut(self, out_filename):
        with wave.open(out_filename, 'w') as outfile:
            outfile.setnchannels(self.nchannels)
            outfile.setsampwidth(self.sampwidth)
            outfile.setframerate(self.framerate)
            outfile.setnframes(int(len(self.cut_section) / self.sampwidth))
            outfile.writeframes(self.cut_section)




