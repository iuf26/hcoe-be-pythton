from speech2Text.utils.api_02 import upload,save_transcript


def convert_to_text(file,textResultFilename):
    print("**In convert to text**")
    audio_url = upload(file)
    data,error = save_transcript(audio_url, './speech2Text/savings/'+textResultFilename)
    return data,error
