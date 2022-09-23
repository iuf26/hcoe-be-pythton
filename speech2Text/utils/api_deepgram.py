import sys
from speech2Text.utils.api_secrets import API_KEY_DEEPGRAM
from deepgram import Deepgram
import asyncio, json
from typing import Dict


class Transcriber:

    def __int__(self):
        self.filepath = None
        self.mimetype = None
        self.response = None

    async def transcribe(self):
        deepgram = Deepgram(API_KEY_DEEPGRAM)
        audio = open(self.filepath, 'rb')
        source = {
            'buffer': audio,
            'mimetype': self.mimetype
        }

        # Send the audio to Deepgram and get the response
        transcription = await deepgram.transcription.prerecorded(
            source,
            {
                'punctuate': True,
                'diarize': True,
                'utterances': True
            }
         )
        #results = await self.compute_speaking_time(transcription)
        results = transcription["results"]["utterances"]
        self.response = results

    #maybe we'll need this later for something
    #format the diarize result as follow: Speaker number: sentence, time speaking
    async def compute_speaking_time(self, transcript_data: Dict) -> None:
        if 'results' in transcript_data:
            conversation = []
            all_conversation = transcript_data["results"]["channels"][0]["alternatives"][0]["transcript"]
            conversation.append(conversation)
            transcript = transcript_data['results']['channels'][0]['alternatives'][0]['words']

            total_speaker_time = {}
            speaker_words = []
            current_speaker = -1

            for elem in transcript:
                speaker_number = elem["speaker"]

                if speaker_number is not current_speaker:
                    current_speaker = speaker_number
                    speaker_words.append([speaker_number, [], 0])

                    try:
                        total_speaker_time[speaker_number][1] += 1
                    except KeyError:
                        total_speaker_time[speaker_number] = [0, 1]

                get_word = elem["word"]
                speaker_words[-1][1].append(get_word)

                total_speaker_time[speaker_number][0] += elem["end"] - elem["start"]
                speaker_words[-1][2] += elem["end"] - elem["start"]

            for elem, words, time_amount in speaker_words:
                s = f"Speaker {elem}: {' '.join(words)}, Time speaking: {time_amount}"
                conversation.append(s)

            for elem, (total_time, amount) in total_speaker_time.items():
                s = f"Speaker {elem} avg time per phrase: {total_time / amount} "
                ss = f"Total time of conversation: {total_time}"
                conversation.append(s)
                conversation
            return conversation

    def get_transcribed_data(self):
        asyncio.run(self.transcribe())