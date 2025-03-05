from bs4 import BeautifulSoup
import requests
import os
import random
import string
from urllib.parse import urljoin
import time
import textwrap

def create_folder(title):
    # Erstelle einen Ordner mit dem Website-Titel, wenn er noch nicht existiert
    folder_path = os.path.join(os.getcwd(), title)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

url = input("Bitte gültigen Wohnungsboersen-Link eingeben: ")

r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')

# Extrahiere den Website-Titel
title_element = soup.find('title')
title = title_element.text.strip() if title_element else 'unnamed_website'

# Erstelle einen Ordner für die heruntergeladenen Dateien
folder_path = create_folder(title)

images = soup.find_all('img')

downloaded_filenames = set()

def print_loading_dot():
    print(".", end='', flush=True)  # Ausgabe für den Fortschritt

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(letters_and_digits) for _ in range(length))
    return random_string

# Bilder herunterladen und im Ordner speichern
for image in images:
    link = image['src']
    if link.endswith('.svg'):
        continue  # Ignoriere SVG-Dateien
    full_url = urljoin(url, link)
    filename = full_url.split('/')[-1]
    if filename not in downloaded_filenames:
        name = generate_random_string(4)
        file_path = os.path.join(folder_path, name + '.jpg')
        with open(file_path, 'wb') as f:
            im = requests.get(full_url)
            f.write(im.content)
            downloaded_filenames.add(filename)
        (print_loading_dot())
        time.sleep(0.5)

# Text extrahieren und in einer Textdatei speichern
div_element = soup.find('div', class_='md:col-span-8')
if div_element:
    # Finde alle <h2>-Tags innerhalb des gefundenen <div>-Elements und gib den Text aus
    title_texts = [title.text.strip() for title in div_element.find_all('h2')]

    # Gib die extrahierten Texte aus
    for title_text in title_texts:
        dl_elements = soup.find('div', class_='flex p-2 rounded-lg bg-bg-canvas divide-x-1 divide-bg-muted').find_all('dl')

        # Initialisiere Variablen für die gefundenen Informationen
        kaufpreis = zimmer = flaeche = None

        # Durchlaufe alle gefundenen <dl>-Elemente
        for dl_element in dl_elements:
            # Finde das <dt>-Tag innerhalb des <dl>-Elements
            dt_element = dl_element.find('dt')

            # Finde das <dd>-Tag innerhalb des <dl>-Elements
            dd_element = dl_element.find('dd', class_='font-bold md:text-h3')

            if dt_element and dd_element:
                dt_text = dt_element.text.strip()
                dd_text = dd_element.text.strip()

                if dt_text == 'Kaufpreis':
                    kaufpreis = dd_text
                    miete_text = 'Kaufpreis'
                elif dt_text == 'Zimmer':
                    zimmer = dd_text
                elif dt_text == 'Fläche':
                    flaeche = dd_text
                elif dt_text == 'Kaltmiete':
                    kaltmiete = dd_text
                    miete_text = 'Kaltmiete'

        text_element = soup.find('div', class_='mt-4 md:mt-8')

        # Überprüfe, ob das Element gefunden wurde
        if text_element:
            # Extrahiere den Text des Elements
            extracted_text = text_element.get_text(separator='\n').strip()
            wrapped_text = textwrap.fill(extracted_text, width=80)
        else:
            print("Es wurde keine Beschreibung gefunden....")

        # Öffne die Datei im Schreibmodus ('w') und füge den Text am Ende hinzu ('a')
        with open(os.path.join(folder_path, 'output.txt'), 'a', encoding='utf-8') as output_file:
            output_file.write(f'Title: {title_text} \n')
            if miete_text:
                output_file.write(f'{miete_text}: {kaufpreis if miete_text == "Kaufpreis" else kaltmiete}\n')
            output_file.write(f'Zimmer: {zimmer}\n')
            output_file.write(f'Fläche: {flaeche}\n')
            output_file.write(f'Beschreibung: \n {wrapped_text}\n')

print(f"\nScraping abgeschlossen. Dateien im Ordner: {folder_path}")
