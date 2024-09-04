import streamlit as st
import requests
import xml.etree.ElementTree as ET

# Functie om de `latestItem` te extraheren en de URL aan te passen
def get_latest_item_url(manifest_url):
    response = requests.get(manifest_url)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content)
            # Zoek de waarde van `latestItem`
            latest_item = root.attrib.get('_latestItem')
            if latest_item:
                # Bouw de nieuwe URL op basis van `latestItem`
                latest_item_url = manifest_url.replace('manifest.xml', latest_item)
                return latest_item_url
            else:
                st.error("`_latestItem` niet gevonden in het manifest.")
                return None
        except ET.ParseError as e:
            st.error(f"Fout bij het parsen van de XML: {e}")
            return None
    else:
        st.error(f"Kan de manifest data niet ophalen. Statuscode: {response.status_code}")
        return None

# Hoofdfunctie voor de interface
def intro():
    # Bouw de manifest URL op basis van de keuze van de gebruiker
    base_url = "https://repository.officiele-overheidspublicaties.nl/bwb/"
    manifest_url = f"{base_url}{item_id}/manifest.xml"
    
    st.write(f"Manifest URL: {manifest_url}")  # Debug: Toon de manifest URL

    # Haal de latest item URL op
    latest_item_url = get_latest_item_url(manifest_url)

    if latest_item_url:
        st.write(f"Latest Item URL: {latest_item_url}")  # Debug: Toon de latest item URL

        # Hier kun je verder gaan met het verwerken van de latest item URL
        # Bijvoorbeeld: het ophalen van de XML data voor dit item en het parsen ervan
    else:
        st.write("Kon geen geldige latest item URL vinden.")
    
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

# Roep de hoofdlogica aan
intro()
