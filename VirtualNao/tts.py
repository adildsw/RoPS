from gtts import gTTS
from playsound import playsound
import sys
import shlex
import os


def main():
	mytext = " ".join(map(shlex.quote, sys.argv[1:]))


	language = 'en'
	tts = gTTS(text=mytext, lang = language, slow=False)
	tts.save("speech.mp3")
	playsound("speech.mp3")
	os.remove("speech.mp3")

if __name__ == '__main__':
	main()