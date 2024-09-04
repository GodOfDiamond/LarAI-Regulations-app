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

# Functie om hoofdstukken en subheaders te extraheren uit de XML
def parse_xml(url):
    response = requests.get(url)
    if response.status_code == 200:
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()

        # Extract de waarden van <label>Hoofdstuk</label> en <titel status="officieel">Algemene bepalingen</titel>
        hoofdstukken = {}
        current_hoofdstuk = None

        for elem in root.iter():
            if elem.tag == 'label' and elem.text == 'Hoofdstuk':
                current_hoofdstuk = None
            elif elem.tag == 'titel' and elem.attrib.get('status') == 'officieel':
                if current_hoofdstuk is None:
                    current_hoofdstuk = elem.text
                    hoofdstukken[current_hoofdstuk] = []
                else:
                    hoofdstukken[current_hoofdstuk].append(elem.text)

        return hoofdstukken
    else:
        st.error(f"Kan de data niet ophalen. Statuscode: {response.status_code}")
        return {}

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

            # Plaats de hoofdstukken en subheaders in de sidebar
            if hoofdstukken:
                for hoofdstuk, subheaders in hoofdstukken.items():
                    with st.sidebar.expander(hoofdstuk):
                        for subheader in subheaders:
                            st.write(subheader)

            else:
                st.write('Geen hoofdstukken of subheaders gevonden in het XML-bestand.')
        else:
            st.write("Geen geldige URL voor het laatste item gevonden.")
    
    st.sidebar.success("Kies een wetgeving hierboven.")

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

st.subheader("Artikel")
multi = '''De vergunninghouder draagt er voor zorg dat in zijn organisatie een doeltreffend integriteitsbeleid wordt ontwikkeld, toegepast en onderhouden, gericht op het onderkennen en voorkomen van.
'''
st.markdown(multi)

st.header("Tabel")
df = pd.DataFrame(
   [
       {"Topic": "Onderdeel A", "Gap": 4, "Potentiële oplossing": True, "Afhankelijkheid": "placeholder"},
       {"Topic": "Onderdeel B", "Gap": 5, "Potentiële oplossing": False, "Afhankelijkheid": "placeholder"},
       {"Topic": "Onderdeel C", "Gap": 3, "Potentiële oplossing": True, "Afhankelijkheid": "placeholder"},
   ]
)
st.table(df)

with st.expander("Zie uitleg"):
    st.write('''
        Placeholder for the explanation
    ''')

page_names_to_funcs = {
    "—": intro
}
demo_name = st.sidebar.selectbox("Kies een wetgeving", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
