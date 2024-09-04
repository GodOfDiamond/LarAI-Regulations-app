import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

# Functie om de XML-data te parsen en het nieuwste item te vinden
def parse_xml_and_find_latest(url):
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        
        # Vind het nieuwste item gebaseerd op het _latestItem attribuut
        latest_item = root.attrib.get('_latestItem', None)
        
        if latest_item:
            latest_item_url = url.replace('manifest.xml', latest_item)
            return latest_item_url
        else:
            st.error("Het _latestItem attribuut is niet gevonden in de XML.")
            return None
    else:
        st.error(f"Kan de data niet ophalen. Statuscode: {response.status_code}")
        return None

# Functie om hoofdstukken, subheaders en artikelen te extraheren uit de XML
def parse_xml(url):
    response = requests.get(url)
    if response.status_code == 200:
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()

        # Dictionary om de structuur op te slaan
        structuur = {}
        current_hoofdstuk = None

        for elem in root.iter():
            if elem.tag == 'label' and elem.text == 'Hoofdstuk':
                current_hoofdstuk = None
            elif elem.tag == 'titel' and elem.attrib.get('status') == 'officieel':
                if current_hoofdstuk is None:
                    current_hoofdstuk = elem.text
                    structuur[current_hoofdstuk] = []
                else:
                    structuur[current_hoofdstuk].append(elem.text)

        return structuur
    else:
        st.error(f"Kan de data niet ophalen. Statuscode: {response.status_code}")
        return {}

# Dynamisch navigatiemenu genereren en pagina's aanmaken
def generate_pages_and_sidebar_menu(hoofdstukken):
    page_names_to_funcs = {}
    
    for hoofdstuk, subheaders in hoofdstukken.items():
        # Voor elk hoofdstuk maken we een expander aan in de sidebar
        with st.sidebar.expander(hoofdstuk):
            for index, subheader in enumerate(subheaders):
                # Creëer een unieke key door hoofdstuk, subheader, en index te combineren
                key = f"{hoofdstuk}-{subheader}-{index}"
                
                # Dynamische functie aanmaken voor elk artikel
                def article_page(hoofdstuk=hoofdstuk, subheader=subheader):
                    st.header(f"{hoofdstuk} - {subheader}")
                    st.markdown(f"Dit is de inhoud van het artikel **{subheader}** onder hoofdstuk **{hoofdstuk}**.")
                
                # Voeg de functie toe aan de lijst van pagina's
                page_names_to_funcs[key] = article_page
                
                # Voeg een knop toe aan de sidebar om naar deze pagina te navigeren
                if st.sidebar.button(subheader, key=key):
                    st.session_state.selected_page = key

    return page_names_to_funcs

# Hoofdfunctie voor de interface
def intro():
    # Bouw de URL op basis van de keuze van de gebruiker
    base_url = "https://repository.officiele-overheidspublicaties.nl/bwb/"
    url = f"{base_url}{item_id}/manifest.xml"

    # Knop om de data op te halen
    if st.button('Haal XML-data op'):
        latest_item_url = parse_xml_and_find_latest(url)

        if latest_item_url:
            hoofdstukken = parse_xml(latest_item_url)
            if hoofdstukken:
                page_names_to_funcs = generate_pages_and_sidebar_menu(hoofdstukken)
                st.session_state.page_names_to_funcs = page_names_to_funcs
            else:
                st.write('Geen hoofdstukken of subheaders gevonden in het XML-bestand.')
        else:
            st.write("Geen geldige URL voor het laatste item gevonden.")
    
    st.sidebar.success("Kies een wetgeving hierboven.")

# Functie om een artikelpagina weer te geven
def show_article_page():
    if 'selected_page' in st.session_state and 'page_names_to_funcs' in st.session_state:
        selected_page = st.session_state.selected_page
        page_func = st.session_state.page_names_to_funcs.get(selected_page, intro)
        page_func()
    else:
        intro()

# Interface opzetten
st.title("Officiële Overheidspublicaties Viewer")

# Maak een lijst met tuples voor de selectielijst: (zichtbare tekst, bijbehorende ID)
items = [
    ('Regeling kansspelen op afstand', 'BWBR0044767'),
    ('Item 2 beschrijving', 'ID2'),
    ('Item 3 beschrijving', 'ID3')
]

# Maak een dictionary om de ID's op te halen op basis van de zichtbare tekst
item_dict = {item[0]: item[1] for item in items}

# Selectbox voor de gebruiker met de beschrijvingen als opties
selected_item_description = st.selectbox(
    'Kies een Wetgeving',
    list(item_dict.keys())  # We tonen alleen de zichtbare tekst aan de gebruiker
)

# Haal de bijbehorende ID op van het gekozen item
item_id = item_dict[selected_item_description]

# Check welke pagina momenteel geselecteerd is
show_article_page()
