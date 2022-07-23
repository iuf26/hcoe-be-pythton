from speech2Text.utils.api_02 import upload,save_transcript


#functia returneaza json-ul returnat de api  deep speech
# daca totul a decurs ok si in rest returneaza un mesaj de eroare
def convert_to_text_Deep_Speech(filename):
    #aici completeaza tu
    pass


def convert_to_text(file,textResultFilename,api):
    print("**In convert to text**")
    audio_url = upload(file)
    data,error = "",""
    if api == 0:
        data,error = save_transcript(audio_url, './speech2Text/savings/'+textResultFilename)
    elif api == 1:
        #data, error = convert_to_text_Deep_Speech(filename)
        data,error = "data",""

    return data, error
