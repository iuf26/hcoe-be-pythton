from flask import json

from speech2Text.utils.api_02 import upload,save_transcript
from speech2Text.utils.api_deepgram import Transcriber



def convert_to_text_deepGram(filename):
    transcriber = Transcriber()
    mimetype = 'audio/wav'
    transcriber.filepath = filename
    transcriber.mimetype = mimetype
    transcriber.get_transcribed_data()
    response = transcriber.response
    return json.dumps(response, indent=4)


def convert_to_text(file,textResultFilename,api):
    print("**In convert to text**")
    audio_url = upload(file)
    data,error = "",""
    if api == 0:
        data,error = save_transcript(audio_url, './speech2Text/savings/'+textResultFilename)
    elif api == 1:
        data, error = convert_to_text_deepGram(file), ''

    return data, error
