import numpy as np
import pandas as pd
import tensorflow
import librosa
from keras.models import model_from_json
from sklearn.preprocessing import LabelEncoder
import os


def load_model():
    json_file = open('speech2Text/emotion_audio/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new.py model
    loaded_model.load_weights("speech2Text/emotion_audio/saved_models/Emotion_Voice_Detection_Model.h5")
    print("Loaded model from disk")
    opt = tensorflow.keras.optimizers.RMSprop(learning_rate=0.00001, decay=1e-6)
    loaded_model.compile(loss='categorical_crossentropy',optimizer=opt, metrics=['accuracy'])
    return loaded_model


def get_predicted_emotion(model, filename):
    if librosa.get_duration(filename=filename) > 3:
        X, sample_rate = librosa.load(filename, res_type='kaiser_fast', duration=2.5, sr=22050 * 2, offset=0.5)
        sample_rate = np.array(sample_rate)
        mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=13), axis=0)
        featurelive = mfccs
        livedf2 = featurelive
        livedf2 = pd.DataFrame(data=livedf2)
        livedf2 = livedf2.stack().to_frame().T
        twodim = np.expand_dims(livedf2, axis=2)
        livepreds = model.predict(twodim, batch_size=32, verbose=1)
        livepreds1 = livepreds.argmax(axis=1)
        liveabc = livepreds1.astype(int).flatten()
        lb = LabelEncoder()
        # lb.fit()
        # livepredictions = (lb.inverse_transform((liveabc)))
        return liveabc.item(0)
    return -1


def get_emotion_for_each_cut(directory):
    model = load_model()
    emotions = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            emotion = get_predicted_emotion(model, f)
            emotions.append(emotion)
    return emotions


def map_emotions(detected_emotions):
    # dict = {0: 'female_angry', 1: 'female_calm', 2: 'female_fearful', 3: 'female_happy', 4: 'female_sad',
    # 5:'male_angry', 6: 'male_calm', 7: 'male_fearful', 8: 'male_happy', 9: 'male_sad'}
    dict = {0: 'angry', 1: 'calm', 2: 'fearful', 3: 'happy', 4: 'sad',
            5: 'angry',
            6: 'calm', 7: 'fearful', 8: 'happy', 9: 'sad', -1: 'inconclusive'}
    emotion_names = []
    for elem in detected_emotions:
        name = dict.get(elem)
        emotion_names.append(name)
    return emotion_names




