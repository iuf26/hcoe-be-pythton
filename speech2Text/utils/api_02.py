import json

import requests
import time
from speech2Text.utils.api_secrets import API_KEY_ASSEMBLYAI

upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_auth_only = {'authorization': API_KEY_ASSEMBLYAI}

headers = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}

CHUNK_SIZE = 5_242_880  # 5MB


def upload(filename):
    def read_file(filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint, headers=headers_auth_only, data=read_file(filename))
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
    for elem in transcript_utterances:
        to_json.append(
            {'text': elem['text'], 'start': elem['start'] / 1000, 'end': elem['end'] / 1000, 'speaker': elem['speaker'],
             'voicePrints': {}})
    json_res = json.dumps(to_json, indent=4)
    with open("json_result.json", "w") as outfile:
        outfile.write(json_res)
    return {'data': json_res}
