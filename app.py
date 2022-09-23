from flask import Flask, request, json
from werkzeug.utils import secure_filename
import os
from speech2Text.service import service
from speech2Text.utils.utility_classes import DocumentWord,WordStatus
import string
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here

    return 'Hello World!'


@app.route('/uploadfile/<section>', methods=['GET', 'POST'])
def uploadfile(section):
    api_to_use = request.view_args['section']
    if request.method == 'POST':
        f = request.files['file']
        filename = f.filename
        filePath = "./speech2Text/audio/" + secure_filename(filename)
        f.save(filePath)
        textConversionResult = request.values['destination-file-name']
        data, error = "", ""
        if api_to_use == "assembly":
            data, error = service.convert_to_text(filePath, textConversionResult, 0)
        else:
            if api_to_use == "deepgram":
                data, error = service.convert_to_text(filePath, textConversionResult, 1)
        os.remove(filePath)
        if data:
            return data
        else:
            return error


@app.route('/compare-documents', methods=['POST'])
def compareDocuments():
    doc1 = request.files['doc1']
    doc2 = request.files['doc2']
    filePathDoc1 = "./speech2Text/savings/" + secure_filename("document1")
    filePathDoc2 = "./speech2Text/savings/" + secure_filename("document2")
    doc1.save(filePathDoc1)
    doc2.save(filePathDoc2)
    wordsDocument1 = getWordsListFromDocument(filePathDoc1)
    wordsDocument2 = getWordsListFromDocument(filePathDoc2)
    result = compare2DocumentsText(wordsDocument1,wordsDocument2)
    resultDictionary = [ob.__dict__ for ob in result]
    endpointResult = {"evaluation":resultDictionary,"transcribedWords":wordsDocument1,"originalWords":wordsDocument2}
    json_string = json.dumps(endpointResult)
    return json_string


@app.route('/test-apis', methods=['GET'])
def testApis():
    api_Asssembly, api_DSpeech = testWER()
    value = {
        "Assembly-Ai": api_Asssembly,
        "Deep-Speech": api_DSpeech

    }
    return json.dumps(value)



def recognizeText(filename, api):
    filePath = "./speech2Text/dataset1/" + secure_filename(filename)
    print("In here recognize text with api")
    data, error = service.convert_to_text(filePath, "wer.txt", api)
    if data:
        if api == 1:
            return data
        else:
            return data["text"]
    else:
        return error


def loadRealOutput():
    filename = './speech2Text/translations/trans1.txt'
    res = []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            low = line.lower()
            res.append(low[:len(low) - 1])
    return res


def loadComputedOutput(api):
    print("in here")
    directory = './speech2Text/dataset1'
    output = []
    # iterate over files in
    # that directory
    for filename in os.listdir(directory):
        f = directory + "/" + filename
        # checking if it is a file
        if os.path.isfile(f):
            to_add = [f, recognizeText(filename, api)]

            output.append(to_add)
    return output


def getWordsList(filename):
    res = []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            low = line.lower()
            res.append(low[:len(low) - 1])
    return res


# !/usr/bin/env python


def wer(r, h):
    """
    Calculation of WER with Levenshtein distance.
    Works only for iterables up to 254 elements (uint8).
    O(nm) time ans space complexity.
    Parameters
    ----------
    r : list
    h : list
    Returns
    -------
    int
    Examples
    --------
    >>> wer("who is there".split(), "is there".split())
    1
    >>> wer("who is there".split(), "".split())
    3
    3
    """
    # initialisation
    import numpy

    d = numpy.zeros((len(r) + 1) * (len(h) + 1), dtype=numpy.uint8)
    d = d.reshape((len(r) + 1, len(h) + 1))
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    # computation
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)

    return d[len(r)][len(h)]



def getError(realOut, computedOut):
    print("Calculating error-----")
    print(computedOut)
    i = 0
    totalError = 0
    nr = 0
    for elem in realOut:
        split = elem.split()
        realPhrase = split[1:]
        if i < 3:
            err = wer(realPhrase, computedOut[i][1].split())
            totalError = totalError + err
        i = i + 1
    print("Done calculating error---- ")
    return totalError / len(realOut)


def computeError(realOut, computedOut):
    print("Calculating error-----")
    print(realOut)
    print(computedOut)
    tempWer = wer(realOut, computedOut)
    err = tempWer / len(realOut)
    print("Done calculating error------"
          "Error is {}".format(err))
    return err


def newTestWER(realFilename, computedFilename):
    realOut = getWordsList(realFilename)
    computedOut = getWordsList(computedFilename)
    computeError(realOut, computedOut)


def testWER():
    print("here")
    api = 0
    #  0- identificator pentru Assembly ai
    modelErr_Assembly = getError(loadRealOutput(), loadComputedOutput(api))

    print('Accuracy of the Assembly AI api using WER:', modelErr_Assembly)

    api = 1  # identificator pentru deep speech
    modelErr_DeepSpeech = getError(loadRealOutput(), loadComputedOutput(api))
    print('Accuracy of Deep Speech using WER:', modelErr_DeepSpeech)
    return modelErr_Assembly, modelErr_DeepSpeech

def getWordsDict(wordsList):
    result = {}
    for elem in wordsList:
        if str(elem) in result:
            result[str(elem)] += 1
        else:
            result[str(elem)] = 1
    return result

#words are in order of appearance,document2 should be the original one
def compare2DocumentsText(wordsInDocument1,wordsInDocument2):
    result = []
    index1 = 0
    index2 = 0
    lenWordsDoc1 = len(wordsInDocument1)
    lenWordsDoc2 = len(wordsInDocument2)
    doc1WordsDict = getWordsDict(wordsInDocument1)
    doc2WordsDict = getWordsDict(wordsInDocument2)


    # document: ,word: ,status: wrong,missing,correct
    while index1 < lenWordsDoc1 and index2 < lenWordsDoc2:
        wordDoc2 = wordsInDocument2[index2]
        wordDoc1 = wordsInDocument1[index1]
        docWord = DocumentWord()
        docWord.word = wordDoc2

        if  wordDoc1 == wordDoc2:
            docWord.status = WordStatus.CORRECT.value
            doc2WordsDict[wordDoc1] = doc2WordsDict[wordDoc1] - 1
            doc1WordsDict[wordDoc1] = doc1WordsDict[wordDoc1] - 1
            index1 += 1
            index2 += 1
        else:
            if (wordDoc1 in doc2WordsDict) and doc2WordsDict[wordDoc1] > 0: # wordDoc1 == wordsInDocument2[index2 + 1]
                if not(doc1WordsDict[wordDoc1] > 0):
                    docWord.status = WordStatus.MISSING.value[0]
                else:
                    doc1WordsDict[wordDoc1] = doc1WordsDict[wordDoc1]  - 1
                index2 += 1
            else:
                docWord.status = WordStatus.WRONG.value[0]
                index1 += 1
                index2 += 1
        result.append(docWord)
    while index2 < lenWordsDoc2:
        docWord = DocumentWord()
        docWord.word = wordsInDocument2[index2]
        docWord.status = WordStatus.MISSING.value[0]
        index2 += 1
        result.append(docWord)
    return result


def getWordsListFromDocument(documentPath):
    result = []
    with open(documentPath, 'r') as file:
        for line in file:
            for word in line.split():
                result.append(word.lower().translate(str.maketrans('', '', string.punctuation)))
    return result

if __name__ == '__main__':
    app.run()
