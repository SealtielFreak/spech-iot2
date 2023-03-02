from abc import abstractmethod, ABC
from typing import Collection, Text

import nltk
from textblob import TextBlob

[nltk.download(s) for s in ('punkt', 'averaged_perceptron_tagger', 'brown')]


class ScriptCommand(ABC):
    def __init__(self, name: Text, alias: Collection[Text]):
        self.__name = name
        self.__alias = alias

    @property
    def name(self):
        return self.__name

    @property
    def alias(self):
        return list(self.__alias)

    @abstractmethod
    def run(self, ): ...


class ScriptCommandManager:
    def __init__(self):
        self.__all_commands = {}
        self.__all_keys = {}

    @property
    def sentences_types(self):
        return self.__all_keys

    def find(self, alias: Text):
        if alias in self.__all_commands:
            return self.__all_commands[alias]

        return None

    def insert(self, script: ScriptCommand):
        self.__all_commands[script.name] = script
        self.__all_keys[script.name] = script.alias

    def bind(self, *args, **kwargs):
        def inner(cls):
            self.insert(cls(*args, **kwargs))
            return cls

        return inner

    def search(self, alias: Text):
        def identify_sentence_type(text):
            sentence_types = self.sentences_types

            blob = TextBlob(text)
            for sentence_type, aliases in sentence_types.items():
                for word in blob.words:
                    if word.lower() in aliases:
                        return sentence_type
            return None

        sentence_type = identify_sentence_type(alias)
        return self.find(sentence_type)


if __name__ == "__main__":
    manager = ScriptCommandManager()


    @manager.bind("Time", ("hora", "tiempo"))
    class TimeCommand(ScriptCommand):
        def run(self):
            print("Consultando tiempo...")


    @manager.bind("Command", ("abrir", "iniciar", "ejecutar", "cerrar", "finalizar", "terminar"))
    class VoiceCommand(ScriptCommand):
        def run(self):
            print("Llamando comando...")


    @manager.bind("Question", ("quién", "qué", "cuándo", "dónde", "por qué", "cómo"))
    class QuestionCommand(ScriptCommand):
        def run(self):
            print("Contestando pregunta...")


    @manager.bind("Query", ("buscar", "encontrar", "consultar", "obtener"))
    class QueryCommand(ScriptCommand):
        def run(self):
            print("Haciendo consulta...")


    manager.search("Dime la hora").run()
