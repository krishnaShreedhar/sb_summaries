"""
"""
import wave
import math
import contextlib
from tqdm import tqdm
import traceback

import speech_recognition as sr
import config

import argparse

tqdm.pandas()


def _transcribe_sphinx(audio_fn):
    r = sr.Recognizer()
    with sr.AudioFile(audio_fn) as source:
        audio = r.record(source)
    try:
        transcript = r.recognize_sphinx(audio)
        print(f"Sphinx thinks you said {transcript}")
        return transcript
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
        return None
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))
        return None


def _transcribe_google_paid(audio_fn):
    """

    :param audio:
    :param r:
    :return:
    """
    r = sr.Recognizer()
    with sr.AudioFile(audio_fn) as source:
        audio = r.record(source)

    try:
        print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""INSERT THE CONTENTS OF THE GOOGLE CLOUD SPEECH JSON CREDENTIALS FILE HERE"""
    try:
        transcript = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
        print(f"Google Cloud Speech thinks you said: {transcript} ")
        return transcript
    except sr.UnknownValueError:
        print("Google Cloud Speech could not understand audio")
        return None
    except sr.RequestError as e:
        print("Could not request results from Google Cloud Speech service; {0}".format(e))
        return None


def _transcribe_google_free(audio_fn):
    with contextlib.closing(wave.open(audio_fn, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)

    total_duration = math.ceil(duration / 60)
    r = sr.Recognizer()

    transcript = f""
    for i in tqdm(range(0, total_duration)):
        with sr.AudioFile(audio_fn) as source:
            audio = r.record(source, offset=i * 60, duration=60)

        try:
            output = r.recognize_google(audio)
        except Exception as e:
            output = "None"
        transcript += f"\n{output}"

    return transcript


def transcribe(audio_fn, transcript_file, option=1):
    """

    :param audio_fn:
    :param transcript_file:
    :param option:
    :return:
    """

    dict_transcribers = {
        1: _transcribe_google_free,
        2: _transcribe_sphinx,
        3: _transcribe_google_paid
    }

    try:
        transcript = dict_transcribers[option](audio_fn)
        with open(transcript_file, "a") as fh:
            fh.write(transcript)
        return True
    except Exception:
        return False


def parse_arguments():
    parser = argparse.ArgumentParser()

    args = parser.parse_args()
    return args


def main():
    # args = parse_arguments()
    # print(args)
    file_path = "../data/SRIP_Reading_CC_1_260316_24.wav"
    out_path = "temp_transcript.txt"
    transcribe(audio_fn=file_path, transcript_file=out_path)


if __name__ == '__main__':
    main()
