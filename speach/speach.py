import os

import requests
import speech_recognition as sr
from dotenv import load_dotenv

from mqtt_handler import MqttHandler

load_dotenv()

mqtt = MqttHandler(os.getenv("MQTT_BROKER"),
                   int(os.getenv("MQTT_PORT")),
                   os.getenv("MQTT_TOPIC"),
                   os.getenv("MQTT_USER"),
                   os.getenv("MQTT_PASSWORD"))


def process_command(command: str):
    command = command.lower().strip()

    if "weiter" in command:
        print("Weiter...")
        mqtt.send("next")

    if "zurück" in command or "zurück" in command:
        print("Zurück...")
        mqtt.send("back")


def select_microphone():
    # Verfügbare Mikrofone auflisten
    devices = sr.Microphone.list_microphone_names()
    print("Verfügbare Mikrofon-Geräte:")
    for idx, name in enumerate(devices):
        print(f"  {idx}: {name}")
    choice = input("Geräteindex wählen (Enter für Standard): ")
    try:
        if choice.strip() != "":
            idx = int(choice)
            return sr.Microphone(device_index=idx)
    except (ValueError, IndexError):
        print("Ungültige Auswahl; Standardmikrofon wird verwendet.")
    return sr.Microphone()


def main():
    recognizer = sr.Recognizer()
    microphone = select_microphone()

    print("Kalibriere Umgebungsgeräusche. Bitte warten...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Kalibrierung abgeschlossen. Höre auf Sprache. Strg+C zum Beenden.")

    try:
        while True:
            with microphone as source:
                # print("Höre...")
                audio = recognizer.listen(source)

            # print("Erkenne Sprache...")
            try:
                text: str = recognizer.recognize_google(
                    audio, language='de-DE')
                process_command(text)

            except sr.UnknownValueError:
                print("Entschuldigung, Audio konnte nicht verstanden werden.")
            except sr.RequestError as e:
                print(f"API-Anfrage fehlgeschlagen: {e}")
    except KeyboardInterrupt:
        print("\nProgramm beendet. Auf Wiedersehen!")


if __name__ == "__main__":
    main()
    # process_command("ein")
