import json
import os
import requests
import time
from speech2Text.utils.api_secrets import API_KEY_ASSEMBLYAI
from speech2Text.utils.utility_classes import CutAudio
from speech2Text.emotion_audio.detect_emotion import map_emotions, get_emotion_for_each_cut

upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_auth_only = {'authorization': API_KEY_ASSEMBLYAI}

headers = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}

CHUNK_SIZE = 5_242_880  # 5MB
filename_global = ""


def upload(filename):
    def read_file(filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint, headers=headers_auth_only, data=read_file(filename))
    global filename_global
    filename_global = filename
    return upload_response.json()['upload_url']


def transcribe(audio_url):
    transcript_request = {
        'audio_url': audio_url,
        'speaker_labels': True

    }
    headersNow = {
        "authorization": API_KEY_ASSEMBLYAI
    }
    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headersNow)
    return transcript_response.json()['id']


def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)
    return polling_response.json()


def get_transcription_result_url(url):
    transcribe_id = transcribe(url)
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':

            return data, None
        elif data['status'] == 'error':
            return data, data['error']

        print("waiting for  10 seconds")
        time.sleep(10)


def save_transcript(url, title):
    data, error = get_transcription_result_url(url)

    if data:
        create_json(data['utterances'])
        filename = title + '.txt'
        with open(filename, 'w') as f:
            f.write(data['text'])
    return data, error


def create_json(transcript_utterances):
    to_json = []
    audio_chunks_time_list = []
    for elem in transcript_utterances:
        to_json.append(
            {'text': elem['text'], 'start': elem['start'] / 1000, 'end': elem['end'] / 1000, 'speaker': elem['speaker'],
             'voicePrints': {}})
        audio_chunks_time_list.append((elem['start'] / 1000, elem['end'] / 1000))

    emotions = detect_emotion(filename_global, audio_chunks_time_list)
    if len(emotions) == len(to_json):
        for index, elem in enumerate(to_json):
            to_json[index]['voicePrints'] = {'emotion': emotions[index]}

    json_res = json.dumps(to_json, indent=4)
    with open("json_result.json", "w") as outfile:
        outfile.write(json_res)
    return {'data': json_res}


def save_audio_chunks(filename, audio_chunks_time_list):
    audio_cut = CutAudio(filename)
    out_dir = 'speech2Text/audio_cuts'

    for f in os.listdir(out_dir):
        os.remove('speech2Text/audio_cuts/'+f)

    for index, elem in enumerate(audio_chunks_time_list):
        audio_cut.start = elem[0]
        audio_cut.end = elem[1]
        out_filename = '{}/cut{}.wav'.format(out_dir, index)
        audio_cut.read_file()
        audio_cut.write_audio_cut(out_filename)


def detect_emotion(filename, audio_chunks_time_list):
    save_audio_chunks(filename, audio_chunks_time_list)
    detected_emotions_number = get_emotion_for_each_cut('speech2Text/audio_cuts')
    detected_emotions_names = map_emotions(detected_emotions_number)
    return detected_emotions_names

