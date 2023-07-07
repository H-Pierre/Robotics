#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from text2digits import text2digits
from transformers import pipeline


def translate(sentence):
    """ Traduit une phrase française en anglais
    Arguments:
        sentence: String, phrase en français à traduire
    Outputs:
        converted_sentence: String, phrase traduite en anglais
    """
    # model_checkpoint for French to English translation
    model_checkpoint = "Helsinki-NLP/opus-mt-fr-en"
    translator = pipeline("translation_fr_to_en", model=model_checkpoint)
    translated_sentence = translator(sentence)[0]["translation_text"]
    t2d = text2digits.Text2Digits()
    converted_sentence = t2d.convert(translated_sentence)

    return converted_sentence


if __name__ == "__main__":
    print(translate("Modèle pré-entraîné téléchargé avec succès !"))
