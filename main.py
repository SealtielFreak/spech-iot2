import datetime
import random
import time
from typing import Text

import openai
from rich import pretty
from rich.console import Console
from serial import Serial
from speech_recognition import Recognizer, Microphone

from commands import ScriptCommandManager, ScriptCommand
from speech import Speech

DEBUG_MODE = False
DEFAULT_LANGUAGE = 'es-MX'

MODEL_ENGINE_OPENAIN = "text-davinci-003"
API_KEY_OPENAIN = ""

pretty.install()

console = Console()


class Listener:
    def __init__(self, speech: Speech, err_msg: list[str]):
        self.__last_command = ""
        self.__speech = speech
        self.__err_msg = err_msg

    @property
    def last_command(self):
        return self.__last_command

    def take_command(self, required=True) -> str:
        recognizer = Recognizer()
        query = ""

        with Microphone() as source:
            console.log("Listening command...")

            recognizer.pause_threshold = 1
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            console.log("Recognizing voice...")
            query = recognizer.recognize_google(audio, language=DEFAULT_LANGUAGE, show_all=False)
            console.log(f"User said: {query}\n")
        except Exception as e:
            if required:
                console.log("Unable to Recognize your voice.", e)
                self.__speech.speak(random.sample(self.__err_msg, 1)[-1])

        self.__last_command = query.lower()

        return self.last_command


speech = Speech()
listener = Listener(speech, ['Disculpa pero no te entiendo', '¿Me puedes repetir?'])

random_sample = lambda l: random.sample(l, 1)[0]
random_speak = lambda l: speech.speak(random_sample(l))

openai.api_key = API_KEY_OPENAIN


def send_to_arduino(command: Text):
    try:
        arduino = Serial("COM3", 9600)

        time.sleep(2)

        arduino.write(command.encode())
        arduino.close()
    except:
        return False

    return True


def wish_me():
    hour = int(datetime.datetime.now().hour)

    if 0 <= hour < 12:
        speech.speak("Buenos dias!")
    elif 12 <= hour < 18:
        speech.speak("Buenas tardes!")
    else:
        speech.speak("Buenas noches !")


def user_welcome():
    speech.speak("¿Cual es tu nombre?")
    uname = ""

    while uname == "":
        listener.take_command()
        uname = listener.last_command

        if uname == "":
            speech.speak("No entendi tu nombre, ¡Intentemos una vez mas!")

    speech.speak("¡Bienvenido!")
    speech.speak(uname)
    speech.speak("¿Que puedo hacer por ti hoy?")


if __name__ == '__main__':
    manager = ScriptCommandManager()

    wish_me()

    if not DEBUG_MODE:
        user_welcome()


    @manager.bind("Close", ("adios", "acabamos"))
    class CloseCommand(ScriptCommand):
        def run(self):
            raise SystemExit

    @manager.bind("Time", ("hora", "tiempo"))
    class TimeCommand(ScriptCommand):
        def run(self):
            speech.speak("Consultando tiempo...")


    @manager.bind("CommandClose", ("cerrar", "finalizar", "terminar", "apagar"))
    class VoiceCommandClose(ScriptCommand):
        def run(self):
            speech.speak("Apagando LED del dispositivo")

            if not send_to_arduino("0"):
                speech.speak("Lo lamento, pero parece que el dispositivo no se encuentra conectado")


    @manager.bind("CommandOpen", ("abrir", "iniciar", "ejecutar", 'encender'))
    class VoiceCommandOpen(ScriptCommand):
        def run(self):
            speech.speak("Encendiendo LED del dispositivo")

            if not send_to_arduino("1"):
                speech.speak("Lo lamento, pero parece que el dispositivo no se encuentra conectado")


    @manager.bind("Question", ("quién", "qué", "cuándo", "dónde", "por qué", "cómo"))
    class QuestionCommand(ScriptCommand):
        def run(self):
            speech.speak("Okey")
            random_speak(("Dame un momento", "Dame un segundo", "Deja intentar"))

            prompt = listener.last_command
            completion = openai.Completion.create(
                engine=MODEL_ENGINE_OPENAIN,
                prompt=prompt,
                max_tokens=300,
                n=1,
                stop=None,
                temperature=0.5,
            )

            speech.speak(completion.choices[0].text)


    @manager.bind("Query", ("buscar", "encontrar", "consultar", "obtener"))
    class QueryCommand(ScriptCommand):
        def run(self):
            speech.speak("Okey")
            random_speak(("Dame un momento", "Dame un segundo", "Deja intentar"))

            prompt = listener.last_command
            completion = openai.Completion.create(
                engine=MODEL_ENGINE_OPENAIN,
                prompt=prompt,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.5,
            )

            speech.speak(completion.choices[0].text)


    def main_loop():
        running = True

        while running:
            try:
                listener.take_command(False)
                query = listener.last_command

                if query != "":
                    try:
                        voice_command = manager.search(query)
                        if voice_command is not None:
                            voice_command.run()
                        else:

                            random_speak(
                                ("¿Algo mas?", "¿Necesitas algo mas?", "¿Que otra cosa puedo hacer por ti?")
                            )
                    except KeyboardInterrupt:
                        random_speak(
                            ("No te entiendo, pinche vato estupido", "Habla mas claro, por favor", "No te entiendo")
                        )

            except KeyboardInterrupt | SystemExit:
                running = False

        random_speak(("¡Hasta la proximaaa!", "Adios", "Fue un gusto trabajar contigo"))


    main_loop()
