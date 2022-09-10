import json
from enum import Enum
class DocumentWord:
    def __int__(self):
        self.word = None
        self.status = None


class WordStatus(Enum):
    WRONG = "wrong",
    MISSING = "missing",
    CORRECT = "correct"
