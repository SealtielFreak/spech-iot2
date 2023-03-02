import pyttsx3


class Speech:
    def __init__(self):
        self.__engine = pyttsx3.init('sapi5')

    @property
    def volumen(self):
        return self.__engine.getProperty('volumne')

    @volumen.setter
    def volumen(self, value: int):
        self.__engine.setProperty('volumen', value)

    def speak(self, txt: str):
        self.__engine.say(txt)
        self.__engine.runAndWait()
