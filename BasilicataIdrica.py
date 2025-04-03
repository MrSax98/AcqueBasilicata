# -*- coding: utf-8 -*-
import folium
import webbrowser
import os
import requests # Per scaricare i GeoJSON
import json
import numpy as np # Usato per generare punti placeholder per i fiumi
from branca.element import Element # Per aggiungere HTML custom (legenda)

# Importa i plugin necessari
from folium.plugins import MarkerCluster, Search, MiniMap, MeasureControl, MousePosition, Fullscreen, Draw

print("--- Inizio Script Creazione Mappa Avanzata Basilicata ---")

# --- URL Dati Esterni (VERIFICARE E AGGIORNARE SE NECESSARIO) ---
# Confini Regionali
geojson_regioni_url = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"
# Aree Protette (Placeholder - DA COMPILARE)
geojson_parchi_url = "INSERISCI_URL_GEOJSON_AREE_PROTETTE_QUI"
park_name_property = "INSERISCI_NOME_PROPRIETA_PARCO_QUI" # Es: 'NOME_PARCO', 'DENOM', 'NAME'
# Province (Placeholder - DA COMPILARE)
geojson_province_url = "INSERISCI_URL_GEOJSON_PROVINCE_QUI" # Es: Cerca "geojson province italiane istat"
province_name_property = "INSERISCI_NOME_PROPRIETA_PROVINCIA_QUI" # Es: 'prov_name', 'DEN_UTS', 'SIGLA'

# --- Dati Mappa 1: Infrastrutture Idriche ---
centro_basilicata = [40.50, 16.05]
# Dizionari dighe, traverse, citta, potabilizzatori, centrali_idroelettriche (Completi)
dighe = {
    'Monte Cotugno': { 'coords': [40.145, 16.30], 'fiume': 'Sinni', 'capacita': '433 Mmc', 'anno': '1983', 'tipo': 'Terra', 'uso': 'Plurimo', 'gestore': 'EIPLI (presunto)', 'schema': 'Jonico-Sinni (Sub: Sinni)', 'status': 'Esercizio Sperimentale (nel PDF)', 'connections': 'Riceve da Traverse Agri, Sauro, Sarmento. Alimenta Adduttore del Sinni ("Canna del Sinni").', 'note': "Più grande diga in terra d'Europa. Nodo schema Jonico-Sinni." },
    'Pertusillo': { 'coords': [40.258, 16.045], 'fiume': 'Agri', 'capacita': '143 Mmc', 'anno': '1963', 'tipo': 'Muraria a volta ad arco a gravità', 'uso': 'Plurimo (Idroelettrico, Potabile Puglia, Irriguo)', 'gestore': 'EIPLI (presunto)', 'schema': 'Jonico-Sinni (Sub: Agri)', 'status': 'Normale (implicito)', 'connections': 'Alimenta Centrale Missanello -> Potab. Missanello / Rilasci per Traversa Agri / Diga Gannano.', 'note': 'Nodo principale sub-schema Agri.' },
    'San Giuliano': { 'coords': [40.63, 16.62], 'fiume': 'Bradano', 'capacita': '107 Mmc (da quarry.pdf)', 'anno': '1955', 'tipo': 'Calcestruzzo a gravità massiccia', 'uso': 'Irriguo (Metapontino, Puglia)', 'gestore': 'Consorzio Bonifica Bradano e Metaponto', 'schema': 'Jonico-Sinni (Sub: Basso Bradano)', 'status': 'Esercizio Normale', 'connections': 'Collegato (teoricamente) a Adduttore del Sinni via Ginosa (Adduttore Ginosa-S.Giuliano, non funzionante nel PDF).', 'note': '' },
    'Camastra': { 'coords': [40.555, 15.98], 'fiume': 'Torrente Camastra (affl. Basento)', 'capacita': '23.6 Mmc', 'anno': 'Fine anni \'60', 'tipo': 'Materiale sciolto, zonata', 'uso': 'Plurimo (Potabile PZ, Irriguo, Industriale Val Basento)', 'gestore': 'EIPLI (presunto)', 'schema': 'Basento-Bradano', 'status': 'Esercizio Sperimentale (nel PDF)', 'connections': 'Alimenta Stazione Pompaggio -> Potab. Romaniello. Rilascia per Traversa Orto del Tufo. Previsto collegamento a Traversa Trivigno.', 'note': '' },
    'Acerenza': { 'coords': [40.80, 15.92], 'fiume': 'Bradano', 'capacita': '38.5 Mmc', 'anno': '1994', 'tipo': 'Materiale sciolto, zonata', 'uso': 'Irriguo (previsto)', 'gestore': 'EIPLI (presunto)', 'schema': 'Basento-Bradano', 'status': 'Non in esercizio (nel PDF)', 'connections': 'Riceve da Traversa Trivigno via Adduttore (~23km). Collega a Diga Genzano via Adduttore (~14km).', 'note': '' },
    'Genzano': { 'coords': [40.86, 16.01], 'fiume': 'Fiumarella di Genzano', 'capacita': '52.95 Mmc', 'anno': '1997', 'tipo': 'Materiale sciolto, zonata', 'uso': 'Irriguo (previsto)', 'gestore': 'EIPLI (presunto)', 'schema': 'Basento-Bradano', 'status': 'Non in esercizio (nel PDF)', 'connections': 'Riceve da Diga Acerenza via Adduttore. Previsto collegamento a Diga Serra del Corvo.', 'note': '' },
    'Pantano di Pignola': { 'coords': [40.59, 15.75], 'fiume': 'Alto Basento', 'capacita': '4.5 Mmc', 'anno': '1981', 'tipo': 'N/D', 'uso': 'Industriale (ASI Potenza/Tito)', 'gestore': 'ASI Potenza', 'schema': 'Basento-Bradano', 'status': 'Normale (implicito)', 'connections': '', 'note': '' },
    'Serra del Corvo (Basentello)': { 'coords': [40.97, 16.10], 'fiume': 'Torrente Basentello', 'capacita': '28.1 Mmc', 'anno': '1974', 'tipo': 'N/D', 'uso': 'Irriguo (Consorzio Bradano Metaponto)', 'gestore': 'EIPLI (presunto)', 'schema': 'Basento-Bradano', 'status': 'Esercizio Sperimentale (nel PDF)', 'connections': 'Previsto collegamento da Diga Genzano.', 'note': 'Situato confine Basilicata/Puglia.' },
    'Masseria Nicodemo (Cogliandrino)': { 'coords': [40.05, 16.1], 'fiume': 'Sinni (confluenza T. Cogliandrino)', 'capacita': '~10 Mmc', 'anno': '1975', 'tipo': 'N/D', 'uso': 'Idroelettrico', 'gestore': 'ENEL S.p.A.', 'schema': 'Jonico-Sinni (Sub: Sinni-Noce)', 'status': 'Esercizio Normale (gestione ENEL)', 'connections': 'Alimenta Centrale Castrocucco (via adduttore ~15km).', 'note': 'Uso sospeso per emergenza idrica 2002.' },
    'Marsico Nuovo': { 'coords': [40.42, 15.73], 'fiume': 'Agri', 'capacita': '~5 Mmc', 'anno': '1996', 'tipo': 'N/D', 'uso': 'Irriguo (regolazione portate)', 'gestore': 'EIPLI (presunto)', 'schema': 'Jonico-Sinni (Sub: Agri)', 'status': 'Esercizio Sperimentale (nel PDF)', 'connections': 'A monte del Pertusillo.', 'note': '' },
    'Gannano': { 'coords': [40.29, 16.31], 'fiume': 'Agri', 'capacita': '~3 Mmc', 'anno': '1959', 'tipo': 'N/D', 'uso': 'Irriguo', 'gestore': 'EIPLI (presunto)', 'schema': 'Jonico-Sinni (Sub: Agri)', 'status': 'Normale (implicito)', 'connections': 'Intercetta rilasci Pertusillo/Centrale Missanello e fluenze interbacino.', 'note': '' },
    'Abate Alonia (Rendina)': { 'coords': [41.05, 15.80], 'fiume': 'Torrente Rendina', 'capacita': '14 Mmc', 'anno': 'N/D', 'tipo': 'N/D', 'uso': 'Irriguo-Industriale', 'gestore': 'N/D', 'schema': 'Ofanto', 'status': 'Sperimentale (da quarry.pdf)', 'connections': '', 'note': 'Schema Ofanto (info da quarry.pdf)' },
}
traverse = {
    'Santa Venere': { 'coords': [41.085, 15.76], 'fiume': 'Ofanto', 'funzione': 'Snodo Schema Ofanto, ripartizione acque', 'stato': 'Normale (da quarry.pdf)', 'schema': 'Ofanto', 'note': 'Alimenta invasi e comprensori irrigui (Puglia/Basilicata). (Info da quarry.pdf)' },
    'Trivigno': { 'coords': [40.61, 16.00], 'fiume': 'Basento', 'funzione': 'Trasferimento acque a invasi Acerenza/Genzano (via Adduttore)', 'stato': 'Realizzata 2000', 'schema': 'Basento-Bradano', 'note': 'Portata max galleria: 10 mc/s.' },
    'Sauro': { 'coords': [40.20, 16.16], 'fiume': 'Torrente Sauro', 'funzione': 'Convoglia acque a M. Cotugno (via Gronda/Adduttore Sauro-Agri?)', 'stato': 'In esercizio (dal 2002?)', 'schema': 'Jonico-Sinni (Sub: Sinni)', 'note': 'Portata max: 12 mc/s.' },
    'Agri (Traversa)': { 'coords': [40.23, 16.22], 'fiume': 'Agri', 'funzione': 'Convoglia acque a M. Cotugno (via Gronda/Adduttore Agri-Sinni)', 'stato': 'In esercizio (dal 1989?)', 'schema': 'Jonico-Sinni (Sub: Sinni)', 'note': 'Portata max: 18 mc/s. A valle di Missanello.' },
    'Sarmento': { 'coords': [40.08, 16.3], 'fiume': 'Torrente Sarmento', 'funzione': 'Convoglia acque a M. Cotugno (via Adduttore Sarmento-Sinni)', 'stato': 'In completamento (nel PDF)', 'schema': 'Jonico-Sinni (Sub: Sinni)', 'note': 'Portata max: 25 mc/s.' },
    'Orto del Tufo': { 'coords': [40.55, 16.35], 'fiume': 'Basento', 'funzione': 'Derivazione per usi industriali Val Basento (ASI Matera)', 'stato': 'Esistente', 'schema': 'Basento-Bradano', 'note': 'Portata max derivabile: 2 mc/s. Riceve rilasci Camastra/Trivigno.' },
}
citta = {
    'Potenza': {'coords': [40.639, 15.805], 'desc': '<b>Potenza</b><br>Capoluogo di Regione'},
    'Matera': {'coords': [40.667, 16.604], 'desc': '<b>Matera</b><br>Capoluogo di Provincia'}
}
potabilizzatori = {
    'Masseria Romaniello': { 'coords': [40.65, 15.83], 'servizio': 'Potenza e provincia', 'alimentato_da': 'Diga del Camastra (via Stazione Pompaggio)', 'schema': 'Basento-Bradano' },
    'Missanello': { 'coords': [40.28, 16.08], 'servizio': 'Territorio Pugliese', 'alimentato_da': 'Centrale Idroelettrica Missanello (da Diga Pertusillo)', 'schema': 'Jonico-Sinni (Sub: Agri)' }
}
centrali_idroelettriche = {
    'Missanello (Centrale)': { 'coords': [40.27, 16.07], 'fiume': 'Agri (derivazione da Pertusillo)', 'alimenta': 'Potabilizzatore Missanello / Rilasci in alveo (per Traversa Agri/Diga Gannano)', 'gestore': 'ENEL (presunto, gestisce adduttore)', 'schema': 'Jonico-Sinni (Sub: Agri)' },
    'Castrocucco': { 'coords': [39.99, 15.80], 'fiume': 'Noce (riceve da Diga Nicodemo/Sinni)', 'alimentato_da': 'Diga Masseria Nicodemo (via adduttore ~15km)', 'gestore': 'ENEL S.p.A.', 'schema': 'Jonico-Sinni (Sub: Sinni-Noce)' }
}

# --- Dati Mappa 2: Bacini Idrografici ---
bacini = {
    'Bradano': { 'coords': [40.7, 16.4], 'area_kmq': '~3000', 'foce': 'Mar Jonio', 'interregionale': 'Sì (Basilicata 66%, Puglia 34%)', 'note': 'Il bacino idrografico più esteso.' },
    'Basento': { 'coords': [40.5, 16.3], 'area_kmq': '~1535', 'foce': 'Mar Jonio', 'interregionale': 'No (Totalmente in Basilicata)', 'note': '' },
    'Cavone': { 'coords': [40.35, 16.5], 'area_kmq': '~684', 'foce': 'Mar Jonio', 'interregionale': 'No (Totalmente in Basilicata)', 'note': '' },
    'Agri': { 'coords': [40.25, 16.2], 'area_kmq': '~1723', 'foce': 'Mar Jonio', 'interregionale': 'No (Totalmente in Basilicata)', 'note': '' },
    'Sinni': { 'coords': [40.15, 16.4], 'area_kmq': '~1360', 'foce': 'Mar Jonio', 'interregionale': 'Sì (Basilicata 96%, Calabria 4%)', 'note': '' },
    'Noce': { 'coords': [40.05, 15.8], 'area_kmq': '~380', 'foce': 'Mar Tirreno', 'interregionale': 'Sì (Basilicata 78%, Calabria 22%)', 'note': "Unico dei principali a sfociare nel Tirreno." },
    'Bacini Minori Tirrenici': { 'coords': [40.1, 15.7], 'area_kmq': '~40', 'foce': 'Mar Tirreno', 'interregionale': 'Sì (Confine Campania)', 'note': 'Corsi d\'acqua minori.' },
    'Torrente San Nicola': { 'coords': [40.0, 16.6], 'area_kmq': '~85', 'foce': 'Mar Jonio', 'interregionale': 'Sì (Basilicata 87%, Calabria 13%)', 'note': 'Bacino minore confine Calabria.' }
}

# --- Dati Fiumi Manuali (!!! PLACEHOLDER - DA COMPILARE MANUALMENTE !!!) ---
# --------------------------------------------------------------------------
#   ATTENZIONE MASSIMA: Le coordinate qui sotto sono INVENTATE e SCHEMATICHE.
#               NON rappresentano i veri percorsi dei fiumi.
#               DEVI SOSTITUIRLE con coordinate reali [lat, lon] trovate da te!
#               Questo è solo un ESEMPIO di struttura con ~10 punti.
# --------------------------------------------------------------------------
def generate_placeholder_coords(start, end, num_points=10):
    """Genera punti placeholder schematici e INVENTATI tra start ed end."""
    lat = np.linspace(start[0], end[0], num_points)
    lon = np.linspace(start[1], end[1], num_points)
    noise_lat = np.random.normal(0, 0.012, num_points) * np.sin(np.linspace(0, np.pi, num_points))
    noise_lon = np.random.normal(0, 0.018, num_points) * np.sin(np.linspace(0, np.pi, num_points))
    # Ensure start and end points are exact
    noise_lat[0], noise_lat[-1] = 0, 0
    noise_lon[0], noise_lon[-1] = 0, 0
    lat += noise_lat
    lon += noise_lon
    return [[float(la), float(lo)] for la, lo in zip(lat, lon)]

fiumi_manuali = {
    # --- Fiumi Principali (con placeholder ~10 punti) ---
    "Bradano": { "coords": generate_placeholder_coords([40.95, 15.85], [40.40, 16.86], 12), "color": "#1f78b4", "weight": 3, "opacity": 0.85 },
    "Basento": { "coords": generate_placeholder_coords([40.63, 15.75], [40.38, 16.82], 10), "color": "#33a02c", "weight": 3, "opacity": 0.85 },
    "Cavone": { "coords": generate_placeholder_coords([40.50, 16.05], [40.28, 16.77], 10), "color": "#e31a1c", "weight": 3, "opacity": 0.85 },
    "Agri": { "coords": generate_placeholder_coords([40.42, 15.73], [40.20, 16.73], 11), "color": "#ff7f00", "weight": 3, "opacity": 0.85 },
    "Sinni": { "coords": generate_placeholder_coords([40.15, 15.90], [40.15, 16.70], 10), "color": "#6a3d9a", "weight": 3, "opacity": 0.85 },
    "Noce": { "coords": generate_placeholder_coords([40.10, 15.75], [39.98, 15.79], 8), "color": "#fb9a99", "weight": 2.5, "opacity": 0.75 },

    # --- Affluenti Principali (Lasciati vuoti - Aggiungere coordinate per disegnarli) ---
    "Torrente Sauro": { "coords": [], "color": "#a6cee3", "weight": 1.5, "opacity": 0.7 }, # VUOTO
    "Torrente Sarmento": { "coords": [], "color": "#a6cee3", "weight": 1.5, "opacity": 0.7 }, # VUOTO
    "Torrente Camastra": { "coords": [], "color": "#a6cee3", "weight": 1.5, "opacity": 0.7 }, # VUOTO
    "Fiumarella di Genzano": { "coords": [], "color": "#a6cee3", "weight": 1.5, "opacity": 0.7 }, # VUOTO
    "Torrente Cogliandrino": { "coords": [], "color": "#a6cee3", "weight": 1.5, "opacity": 0.7 }, # VUOTO
    "Torrente Basentello": { "coords": [], "color": "#a6cee3", "weight": 1.5, "opacity": 0.7 }, # VUOTO
    "Torrente Rendina": { "coords": [], "color": "#a6cee3", "weight": 1.5, "opacity": 0.7 }, # VUOTO
}
# --------------------------------------------------------------------------

# --- Dati Foci Fiumi ---
foci_fiumi = {
    "Foce Bradano": {'coords': [40.40, 16.86], 'fiume': 'Bradano', 'mare': 'Jonio'},
    "Foce Basento": {'coords': [40.38, 16.82], 'fiume': 'Basento', 'mare': 'Jonio'},
    "Foce Cavone":  {'coords': [40.28, 16.77], 'fiume': 'Cavone', 'mare': 'Jonio'},
    "Foce Agri":    {'coords': [40.20, 16.73], 'fiume': 'Agri', 'mare': 'Jonio'},
    "Foce Sinni":   {'coords': [40.15, 16.70], 'fiume': 'Sinni', 'mare': 'Jonio'},
    "Foce Noce":    {'coords': [39.98, 15.79], 'fiume': 'Noce', 'mare': 'Tirreno'},
}
# Colori per Legenda Fiumi
colori_legenda_fiumi = {
    'Bradano': '#1f78b4', 'Basento': '#33a02c', 'Cavone': '#e31a1c',
    'Agri': '#ff7f00', 'Sinni': '#6a3d9a', 'Noce': '#fb9a99',
    'Affluenti': '#a6cee3'
}

# --- Dati Costa e Puglia ---
punti_extra = {
    'Metaponto Lido': { 'coords': [40.38, 16.80], 'desc': '<b>Metaponto Lido</b><br>Area costiera Jonica interessata da fenomeni di erosione, potenzialmente collegati alla riduzione del trasporto solido fluviale (Fonte: quarry.pdf).', 'icon': {'color': 'darkred', 'icon': 'glyphicon-warning-sign'} },
    'Policoro Lido': { 'coords': [40.18, 16.68], 'desc': '<b>Policoro Lido</b><br>Area costiera Jonica interessata da fenomeni di erosione, potenzialmente collegati alla riduzione del trasporto solido fluviale (Fonte: quarry.pdf).', 'icon': {'color': 'darkred', 'icon': 'glyphicon-warning-sign'} },
    'Nodo di Ginosa': { 'coords': [40.55, 16.85], 'desc': '<b>Nodo di Ginosa (Puglia)</b><br>Importante nodo di smistamento dell\'acqua proveniente dall\'Adduttore del Sinni (Monte Cotugno). Collega (teoricamente) a San Giuliano. (Fonte: sistema_idrico.pdf, Grafico 2)', 'icon': {'color': 'purple', 'icon': 'glyphicon-road'} },
    'Potab. Parco d. Marchese': { 'coords': [40.50, 17.15], 'desc': '<b>Potabilizzatore Parco del Marchese (Taranto, Puglia)</b><br>Riceve acqua dall\'Adduttore del Sinni e Pertusillo via Ginosa per servire l\'area di Taranto e il Salento. (Fonte: Grafico 2)', 'icon': {'color': 'orange', 'icon': 'glyphicon-filter'} },
    'Area ILVA Taranto': { 'coords': [40.48, 17.20], 'desc': '<b>Area ILVA (Taranto, Puglia)</b><br>Importante utente industriale servito dal sistema idrico. (Fonte: Grafico 2)', 'icon': {'color': 'gray', 'icon': 'glyphicon-industry'} }
}

# --- Dati Consorzi di Bonifica ---
consorzi_bonifica = {
    "Consorzio Bonifica Bradano e Metaponto": { 'coords': [40.67, 16.61], 'desc': '<b>Consorzio di Bonifica di Bradano e Metaponto</b><br>Gestisce l\'irrigazione nella pianura metapontina e aree circostanti, utilizzando acque da vari invasi (es. San Giuliano, Serra del Corvo).', 'icon': {'color': 'darkgreen', 'icon': 'glyphicon-leaf'} },
    "Consorzio Bonifica Vulture Alto Bradano": { 'coords': [40.95, 15.83], 'desc': '<b>Consorzio di Bonifica Vulture Alto Bradano</b><br>Gestisce l\'irrigazione nelle aree del Vulture e Alto Bradano, servito dagli schemi Ofanto e Basento-Bradano.', 'icon': {'color': 'darkgreen', 'icon': 'glyphicon-leaf'} },
    "Consorzio Bonifica Stornara e Tara": { 'coords': [40.58, 17.00], 'desc': '<b>Consorzio di Bonifica Stornara e Tara (Puglia)</b><br>Importante utente irriguo in Puglia servito dal sistema interregionale (Schema Jonico-Sinni).', 'icon': {'color': 'darkgreen', 'icon': 'glyphicon-leaf'} },
    "Consorzio Bonifica Ferro e Sparviero": { 'coords': [40.10, 16.55], 'desc': '<b>Consorzio di Bonifica Ferro e Sparviero (Calabria)</b><br>Utente irriguo in Calabria servito dallo Schema Jonico-Sinni (acque Sinni).', 'icon': {'color': 'darkgreen', 'icon': 'glyphicon-leaf'} }
}

# --- Dati Sorgenti (Concettuale) ---
punti_sorgenti = {
    "Principali Sorgenti Appenniniche": { 'coords': [40.2, 15.8], 'desc': '<b>Principali Sorgenti Appenniniche</b><br>Numerose sorgenti lungo la dorsale appenninica (es. area Frida, Mercure, Vulture) alimentano la rete idrica minore e, in parte, gli acquedotti locali. La loro mappatura puntuale non è inclusa. (Fonte: quarry.pdf)', 'icon': {'color': 'blue', 'icon': 'glyphicon-certificate'} }
}

# --- Dati Località Chiave ---
localita_chiave = {
     "Senise": {'coords': [40.15, 16.28], 'desc': '<b>Senise</b><br>Località nei pressi della Diga di Monte Cotugno.', 'icon': {'color': 'black', 'icon': 'glyphicon-map-marker'}},
     "Missanello (Paese)": {'coords': [40.27, 16.17], 'desc': '<b>Missanello</b><br>Località vicina alla centrale e al potabilizzatore omonimi, serviti dalla Diga del Pertusillo.', 'icon': {'color': 'black', 'icon': 'glyphicon-map-marker'}},
     "Ferrandina (Area Ind.)": {'coords': [40.50, 16.55], 'desc': '<b>Area Industriale Ferrandina (Val Basento)</b><br>Importante utenza industriale servita dallo schema Basento (es. tramite traversa Orto del Tufo).', 'icon': {'color': 'gray', 'icon': 'glyphicon-cog'}}
}

# --- Creazione della Mappa ---
mappa_multi = folium.Map(location=centro_basilicata, zoom_start=9, tiles='CartoDB positron')

# Layer Tiles
folium.TileLayer('OpenStreetMap', name='Mappa Standard', overlay=True).add_to(mappa_multi)
folium.TileLayer('Stamen Terrain', name='Mappa Terreno', attr='Map tiles by Stamen Design, CC BY 3.0 | Map data &copy; OpenStreetMap contributors', overlay=True).add_to(mappa_multi)
folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satellite Esri', overlay=True, control=True).add_to(mappa_multi)

# --- Confini Regionali (Tentativo con Stile Differenziato Robusto + Fallback) ---
print("\n--- Tentativo di caricamento dati Confini Regionali (Stile Differenziato) ---")
try:
    # ... (Blocco try...except completo per caricare e STILARE regioni, con fallback a stile semplice, come nella risposta precedente) ...
    response_reg = requests.get(geojson_regioni_url, timeout=10); print(f"Richiesta GeoJSON regioni - Status Code: {response_reg.status_code}"); response_reg.raise_for_status()
    regioni_geojson = response_reg.json(); print("Download e parsing GeoJSON regioni riuscito.")
    if not isinstance(regioni_geojson, dict) or 'features' not in regioni_geojson or not isinstance(regioni_geojson['features'], list): raise ValueError("Struttura GeoJSON regioni non valida")
    def style_regioni_robusta(feature): # Funzione stile robusta
        default_style = {'fillOpacity': 0.05,'weight': 0.5,'color': 'grey','fillColor': 'grey'}
        try:
            if not feature or 'properties' not in feature or not isinstance(feature['properties'], dict): return default_style
            nome_regione = feature['properties'].get('reg_name', '').lower(); style = default_style.copy()
            if nome_regione == 'basilicata': style.update({'fillOpacity': 0.1, 'weight': 3, 'color': '#FF0000', 'fillColor': '#FF0000'})
            elif nome_regione in ['puglia', 'campania', 'calabria']: style.update({'weight': 1.5, 'color': '#FFA500', 'fillOpacity': 0.05})
            else: style.update({'fillOpacity': 0, 'weight': 0});
            return style
        except Exception as e_style: print(f"  - Errore stile regione: {e_style}. Uso stile default."); return default_style
    def highlight_regioni(feature): return {'weight': 3, 'fillOpacity': 0.3}
    folium.GeoJson(regioni_geojson, name='Confini Regionali', style_function=style_regioni_robusta, highlight_function=highlight_regioni, tooltip=folium.features.GeoJsonTooltip(fields=['reg_name'], aliases=['Regione:'], sticky=False), overlay=True, show=True).add_to(mappa_multi)
    print("Layer GeoJSON regioni aggiunto alla mappa (con stile differenziato robusto).")
except Exception as e: # Fallback a stile semplice se il blocco sopra fallisce
    print(f"--- ATTENZIONE: Errore confini regionali (Stile Differenziato): {e}. Provo con stile semplice. ---")
    try:
        if 'regioni_geojson' not in locals(): # Ricarica solo se necessario
             response_reg = requests.get(geojson_regioni_url, timeout=10); response_reg.raise_for_status(); regioni_geojson = response_reg.json()
             if not isinstance(regioni_geojson, dict) or 'features' not in regioni_geojson or not isinstance(regioni_geojson['features'], list): raise ValueError("Struttura GeoJSON fallback non valida")
        simple_region_style = {'fillColor': '#DDDDDD', 'color': '#777777', 'weight': 1, 'fillOpacity': 0.1}
        highlight_style = {'weight': 2, 'color': '#333333', 'fillOpacity': 0.2}
        folium.GeoJson(regioni_geojson, name='Confini Regionali', style_function=lambda x: simple_region_style, highlight_function=lambda x: highlight_style, tooltip=folium.features.GeoJsonTooltip(fields=['reg_name'], aliases=['Regione:'], sticky=False), overlay=True, show=True).add_to(mappa_multi)
        print("Layer GeoJSON regioni aggiunto alla mappa (CON STILE SEMPLICE come fallback).")
    except Exception as e_fallback: print(f"--- ATTENZIONE: Fallito anche caricamento confini con stile semplice: {e_fallback}. Layer non aggiunto. ---")

# --- Confini Provinciali (NUOVO) ---
print("\n--- Tentativo di caricamento dati Confini Provinciali ---")
province_layer_aggiunto = False
# ... (Blocco try...except simile a regioni/parchi per caricare geojson_province_url) ...
if not geojson_province_url or "INSERISCI_URL" in geojson_province_url: print("--- ATTENZIONE: URL per GeoJSON province non specificato. Layer non caricato. ---")
elif not province_name_property or "INSERISCI_NOME" in province_name_property: print(f"--- ATTENZIONE: Proprietà nome provincia ('{province_name_property}') non specificata. Layer non caricato o tooltip errati. ---")
else:
     try:
        response_prov = requests.get(geojson_province_url, timeout=10); print(f"Richiesta GeoJSON province - Status Code: {response_prov.status_code}"); response_prov.raise_for_status()
        province_geojson = response_prov.json(); print("Download e parsing GeoJSON province riuscito.")
        if not isinstance(province_geojson, dict) or 'features' not in province_geojson or not isinstance(province_geojson['features'], list): raise ValueError("Struttura GeoJSON province non valida")

        def style_province(feature):
            default_prov_style = {'fillOpacity': 0, 'weight': 0} # Invisibile di default
            try:
                if not feature or 'properties' not in feature or not isinstance(feature['properties'], dict): return default_prov_style
                # Assumiamo province di Basilicata siano 'Potenza' e 'Matera'
                # ADATTARE province_name_property E I NOMI SE NECESSARIO
                nome_prov = feature['properties'].get(province_name_property, '').lower()
                style = default_prov_style.copy()
                if nome_prov == 'potenza':
                     style.update({'fillColor': '#fec44f', 'color': '#fec44f', 'weight': 1, 'fillOpacity': 0.2}) # Giallo chiaro PZ
                elif nome_prov == 'matera':
                     style.update({'fillColor': '#7bccc4', 'color': '#7bccc4', 'weight': 1, 'fillOpacity': 0.2}) # Verde acqua chiaro MT
                # Altrimenti rimane invisibile
                return style
            except Exception as e_style_prov: print(f"  - Errore stile provincia: {e_style_prov}. Uso stile default."); return default_prov_style

        def highlight_province(feature): return {'weight': 2, 'fillOpacity': 0.4}

        folium.GeoJson(
            province_geojson, name='Confini Provinciali (PZ/MT)',
            style_function=style_province, highlight_function=highlight_province,
            tooltip=folium.features.GeoJsonTooltip(fields=[province_name_property], aliases=['Provincia:']),
            overlay=True, show=True # Mostra per default
        ).add_to(mappa_multi)
        province_layer_aggiunto = True; print("Layer GeoJSON province aggiunto alla mappa.")
     except Exception as e: print(f"--- ATTENZIONE: Errore province: {e}. Layer non aggiunto. ---")
if not province_layer_aggiunto: print("--- Layer 'Confini Provinciali (PZ/MT)' NON aggiunto alla mappa. ---")


# --- Aggiunta Aree Protette (Placeholder) ---
print("\n--- Tentativo di caricamento dati Aree Protette ---")
aree_protette_aggiunte = False
# ... (Blocco try...except come prima) ...
if not geojson_parchi_url or "INSERISCI_URL" in geojson_parchi_url: print("--- ATTENZIONE: URL per GeoJSON aree protette non specificato. Layer non caricato. ---")
elif not park_name_property or "INSERISCI_NOME" in park_name_property: print(f"--- ATTENZIONE: Proprietà nome parco ('{park_name_property}') non specificata. Layer non caricato o tooltip errati. ---")
else:
    try:
        response_parchi = requests.get(geojson_parchi_url, timeout=15); print(f"Richiesta GeoJSON parchi - Status Code: {response_parchi.status_code}"); response_parchi.raise_for_status()
        parchi_geojson = response_parchi.json(); print("Download e parsing GeoJSON parchi riuscito.")
        if 'features' in parchi_geojson and len(parchi_geojson['features']) > 0 and isinstance(parchi_geojson['features'], list):
            print(f"Trovate {len(parchi_geojson['features'])} features nel GeoJSON dei parchi.")
            if parchi_geojson['features'][0] and 'properties' in parchi_geojson['features'][0]: print(f"Proprietà della prima feature parco (per debug nome): {parchi_geojson['features'][0]['properties']}")
            nomi_parchi_basilicata = ['pollino', 'appennino lucano', 'gallipoli cognato']; features_filtrate = []
            for feature in parchi_geojson['features']:
                if feature and 'properties' in feature and isinstance(feature['properties'], dict):
                    nome_parco_prop = feature['properties'].get(park_name_property)
                    if nome_parco_prop:
                        nome_parco_lower = str(nome_parco_prop).lower()
                        for nome_interesse in nomi_parchi_basilicata:
                            if nome_interesse in nome_parco_lower: features_filtrate.append(feature); break
            if features_filtrate:
                print(f"Filtrate {len(features_filtrate)} aree protette di interesse per la Basilicata.")
                parchi_geojson_filtrato = {"type": "FeatureCollection", "features": features_filtrate}
                style_parchi = {'fillColor': '#8FBC8F', 'color': '#2E8B57', 'weight': 1.5, 'fillOpacity': 0.4}
                highlight_parchi = {'fillOpacity': 0.6, 'weight': 2.5}
                folium.GeoJson(parchi_geojson_filtrato, name='Aree Protette Principali', style_function=lambda x: style_parchi, highlight_function=lambda x: highlight_parchi, tooltip=folium.features.GeoJsonTooltip(fields=[park_name_property], aliases=['Parco/Area:'], sticky=False), overlay=True, show=False).add_to(mappa_multi)
                aree_protette_aggiunte = True; print("Layer Aree Protette aggiunto alla mappa (nascosto per default).")
            else: print("--- ATTENZIONE: Nessuna area protetta di interesse trovata nel GeoJSON con i nomi specificati. ---")
        else: print("--- ATTENZIONE: GeoJSON dei parchi scaricato ma non ha la struttura attesa. ---")
    except requests.exceptions.RequestException as e: print(f"--- ERRORE: Impossibile scaricare dati aree protette: {e}. ---")
    except json.JSONDecodeError: print(f"--- ERRORE: Il file scaricato per le aree protette non è JSON valido. ---")
    except Exception as e: print(f"--- ERRORE: Errore imprevisto aree protette: {e}. ---")
if not aree_protette_aggiunte: print("--- Layer 'Aree Protette Principali' NON aggiunto alla mappa. ---")


# --- GRUPPO Layer Fiumi Manuali e Foci ---
fg_idrografia_manuale = folium.FeatureGroup(name='Idrografia (Manuale)', overlay=True, show=True).add_to(mappa_multi)
fiumi_disegnati = False
print("\n--- Disegno Fiumi Manuali (USA COORDINATE PLACEHOLDER!) ---")
# Loop per disegnare i fiumi/affluenti definiti manualmente
for nome, dati_fiume in fiumi_manuali.items():
    coords = dati_fiume.get("coords")
    if coords and isinstance(coords, list) and len(coords) >= 2:
        try:
            tooltip_fiume = f"Fiume/Affluente: {nome}"
            # Aggiungi nota nel tooltip se stiamo usando i placeholder (euristica semplice)
            if any("placeholder" in str(p) for p in coords): # Controlla se la lista contiene la stringa placeholder
                 tooltip_fiume += " (PERCORSO SCHEMATICO PLACEHOLDER - SOSTITUIRE!)"
            elif len(coords) < 5: # Segnala se ci sono pochi punti
                 tooltip_fiume += " (Pochi punti definiti)"

            folium.PolyLine(locations=coords, tooltip=tooltip_fiume, color=dati_fiume.get("color", "#0000FF"), weight=dati_fiume.get("weight", 2), opacity=dati_fiume.get("opacity", 0.75)).add_to(fg_idrografia_manuale)
            print(f" - Disegnato: {nome} ({len(coords)} punti{' - PLACEHOLDER!' if 'placeholder' in tooltip_fiume else ''})")
            fiumi_disegnati = True
        except Exception as e: print(f"   - Errore nel disegnare {nome}: {e}")
    elif coords is not None: print(f" - ATTENZIONE: Fiume/Affluente '{nome}' definito ma con coordinate insufficienti/errate ({len(coords) if isinstance(coords, list) else 'N/A'} punti). Non disegnato.")
if not fiumi_disegnati: print(" - ATTENZIONE: Nessun fiume/affluente manuale disegnato. Popolare 'fiumi_manuali'.")
# Marcatori Foci
for nome_foce, dati_foce in foci_fiumi.items():
     desc_foce = f"<b>{nome_foce}</b><br>Fiume: {dati_foce['fiume']}<br>Sbocca in: Mar {dati_foce['mare']}"
     folium.Marker(location=dati_foce['coords'], tooltip=nome_foce, popup=desc_foce, icon=folium.Icon(color='cyan', icon='glyphicon-flag')).add_to(fg_idrografia_manuale)
print("Aggiunti marcatori per le foci dei fiumi principali.")

# --- GRUPPO Layer Punti Extra (Costa/Puglia/Consorzi/Sorgenti/Località) ---
fg_punti_extra = folium.FeatureGroup(name='Punti Rilevanti / Extra', overlay=True, show=True).add_to(mappa_multi)
print("\n--- Aggiunta Punti Extra (Costa/Puglia/Consorzi/Sorgenti/Località) ---")
# ... (Loop per punti_extra, consorzi_bonifica, punti_sorgenti, localita_chiave) ...
all_extra_points = {**punti_extra, **consorzi_bonifica, **punti_sorgenti, **localita_chiave}
for nome, dati in all_extra_points.items():
    icon_details = dati.get('icon', {'color': 'gray', 'icon': 'info-sign'}); popup_text = dati.get('desc', nome); tooltip_text=nome
    folium.Marker(location=dati['coords'], tooltip=tooltip_text, popup=popup_text, icon=folium.Icon(color=icon_details['color'], icon=icon_details['icon'], prefix='glyphicon')).add_to(fg_punti_extra)
print("Aggiunti punti extra.")

# --- GRUPPO Layer 1: Infrastrutture Idriche ---
fg_infrastrutture = folium.FeatureGroup(name='Visualizza: Infrastrutture Idriche', overlay=False, show=True).add_to(mappa_multi)
# ... (Definizione e popolamento SOTTOGRUPPI come prima, con POPUP STILIZZATI) ...
cluster_dighe = MarkerCluster(name='Dighe'); cluster_traverse = MarkerCluster(name='Traverse'); gruppo_citta = folium.FeatureGroup(name='Città Principali'); gruppo_potabilizzatori = folium.FeatureGroup(name='Potabilizzatori'); gruppo_centrali = folium.FeatureGroup(name='Centrali Idroelettriche')
dati_ricerca_totali = []
th_style = "style='text-align:left; padding: 4px; background-color: #f0f0f0; border-bottom: 1px solid #ddd;'"; td_style = "style='padding: 4px; border-bottom: 1px solid #ddd;'"
# Popola Dighe
for nome, dati in dighe.items():
    schema_info = dati.get('schema', 'N/D'); connections_info = dati.get('connections', '')
    html_popup = f"""<h4>{nome}</h4><table style="width:100%; border-collapse: collapse; font-size: 0.9em;"><tr><th {th_style}>Schema Idrico</th><td {td_style}><b>{schema_info}</b></td></tr><tr><th {th_style}>Fiume</th><td {td_style}>{dati.get('fiume', 'N/D')}</td></tr><tr><th {th_style}>Capacità Utile</th><td {td_style}>{dati.get('capacita', 'N/D')}</td></tr><tr><th {th_style}>Anno Realiz.</th><td {td_style}>{dati.get('anno', 'N/D')}</td></tr><tr><th {th_style}>Tipo</th><td {td_style}>{dati.get('tipo', 'N/D')}</td></tr><tr><th {th_style}>Uso Principale</th><td {td_style}>{dati.get('uso', 'N/D')}</td></tr><tr><th {th_style}>Status (nel PDF)</th><td {td_style}>{dati.get('status', 'N/D')}</td></tr><tr><th {th_style}>Gestore</th><td {td_style}>{dati.get('gestore', 'N/D')}</td></tr>{f"<tr><th {th_style}>Collegamenti</th><td {td_style}>{connections_info}</td></tr>" if connections_info else ""}{f"<tr><th {th_style}>Note</th><td {td_style}>{dati['note']}</td></tr>" if dati.get('note') else ""}</table><small><i>Fonte dati: sistema_idrico.pdf / quarry.pdf</i></small>"""
    popup = folium.Popup(html_popup, max_width=400); marker = folium.Marker(location=dati['coords'], popup=popup, tooltip=f"Diga: {nome} ({schema_info})", icon=folium.Icon(color='blue', icon='glyphicon-home')); marker.add_to(cluster_dighe)
    dati_ricerca_totali.append({ "type": "Feature", "geometry": {"type": "Point", "coordinates": [dati['coords'][1], dati['coords'][0]]}, "properties": {"name": f"Diga: {nome}", "popup": html_popup, "layer": "Infrastrutture Idriche"} })
# Popola Traverse
for nome, dati in traverse.items():
    schema_info = dati.get('schema', 'N/D'); connections_info = dati.get('connections', '')
    html_popup = f"""<h4>{nome}</h4><table style="width:100%; border-collapse: collapse; font-size: 0.9em;"><tr><th {th_style}>Schema Idrico</th><td {td_style}><b>{schema_info}</b></td></tr><tr><th {th_style}>Fiume</th><td {td_style}>{dati.get('fiume', 'N/D')}</td></tr><tr><th {th_style}>Funzione</th><td {td_style}>{dati.get('funzione', 'N/D')}</td></tr><tr><th {th_style}>Stato</th><td {td_style}>{dati.get('stato', 'N/D')}</td></tr>{f"<tr><th {th_style}>Collegamenti</th><td {td_style}>{connections_info}</td></tr>" if connections_info else ""}{f"<tr><th {th_style}>Note</th><td {td_style}>{dati['note']}</td></tr>" if dati.get('note') else ""}</table><small><i>Fonte dati: sistema_idrico.pdf / quarry.pdf</i></small>"""
    popup = folium.Popup(html_popup, max_width=400); marker = folium.Marker(location=dati['coords'], popup=popup, tooltip=f"Traversa: {nome} ({schema_info})", icon=folium.Icon(color='green', icon='glyphicon-transfer')); marker.add_to(cluster_traverse)
    dati_ricerca_totali.append({ "type": "Feature", "geometry": {"type": "Point", "coordinates": [dati['coords'][1], dati['coords'][0]]}, "properties": {"name": f"Traversa: {nome}", "popup": html_popup, "layer": "Infrastrutture Idriche"} })
# Popola Città
for nome, dati in citta.items():
     folium.Marker(location=dati['coords'], popup=dati['desc'], tooltip=nome, icon=folium.Icon(color='red', icon='info-sign')).add_to(gruppo_citta)
# Popola Potabilizzatori
for nome, dati in potabilizzatori.items():
    schema_info = dati.get('schema', 'N/D')
    html_popup = f"""<h4>Potabilizzatore: {nome}</h4><table style="width:100%; border-collapse: collapse; font-size: 0.9em;"><tr><th {th_style}>Schema Idrico</th><td {td_style}><b>{schema_info}</b></td></tr><tr><th {th_style}>Al Servizio di</th><td {td_style}>{dati.get('servizio', 'N/D')}</td></tr><tr><th {th_style}>Alimentato Da</th><td {td_style}>{dati.get('alimentato_da', 'N/D')}</td></tr></table><small><i>Fonte dati: sistema_idrico.pdf</i></small>"""
    popup = folium.Popup(html_popup, max_width=350); marker = folium.Marker(location=dati['coords'], popup=popup, tooltip=f"Potabilizzatore: {nome}", icon=folium.Icon(color='orange', icon='glyphicon-filter')); marker.add_to(gruppo_potabilizzatori)
    dati_ricerca_totali.append({ "type": "Feature", "geometry": {"type": "Point", "coordinates": [dati['coords'][1], dati['coords'][0]]}, "properties": {"name": f"Potabilizzatore: {nome}", "popup": html_popup, "layer": "Infrastrutture Idriche"} })
# Popola Centrali Idroelettriche
for nome, dati in centrali_idroelettriche.items():
    schema_info = dati.get('schema', 'N/D')
    html_popup = f"""<h4>Centrale Idroelettrica: {nome}</h4><table style="width:100%; border-collapse: collapse; font-size: 0.9em;"><tr><th {th_style}>Schema Idrico</th><td {td_style}><b>{schema_info}</b></td></tr><tr><th {th_style}>Posizione/Fiume</th><td {td_style}>{dati.get('fiume', 'N/D')}</td></tr><tr><th {th_style}>Alimentato Da</th><td {td_style}>{dati.get('alimentato_da', 'N/D')}</td></tr><tr><th {th_style}>Alimenta</th><td {td_style}>{dati.get('alimenta', 'N/D')}</td></tr><tr><th {th_style}>Gestore</th><td {td_style}>{dati.get('gestore', 'N/D')}</td></tr></table><small><i>Fonte dati: sistema_idrico.pdf</i></small>"""
    popup = folium.Popup(html_popup, max_width=350); marker = folium.Marker(location=dati['coords'], popup=popup, tooltip=f"Centrale Idroelettrica: {nome}", icon=folium.Icon(color='cadetblue', icon='glyphicon-flash')); marker.add_to(gruppo_centrali)
    dati_ricerca_totali.append({ "type": "Feature", "geometry": {"type": "Point", "coordinates": [dati['coords'][1], dati['coords'][0]]}, "properties": {"name": f"Centrale Idroelettrica: {nome}", "popup": html_popup, "layer": "Infrastrutture Idriche"} })
# Aggiungi sottogruppi a fg_infrastrutture
cluster_dighe.add_to(fg_infrastrutture); cluster_traverse.add_to(fg_infrastrutture); gruppo_citta.add_to(fg_infrastrutture); gruppo_potabilizzatori.add_to(fg_infrastrutture); gruppo_centrali.add_to(fg_infrastrutture)

# --- GRUPPO Layer 2: Bacini Idrografici ---
fg_bacini = folium.FeatureGroup(name='Visualizza: Bacini Idrografici', overlay=False, show=False).add_to(mappa_multi)
# Popolamento Bacini
for nome, dati in bacini.items():
    th_style = "style='text-align:left; padding: 4px; background-color: #f0f0f0; border-bottom: 1px solid #ddd;'"; td_style = "style='padding: 4px; border-bottom: 1px solid #ddd;'"
    html_popup = f"""<h4>Bacino: {nome}</h4><table style="width:100%; border-collapse: collapse; font-size: 0.9em;"><tr><th {th_style}>Superficie</th><td {td_style}>{dati.get('area_kmq', 'N/D')} km²</td></tr><tr><th {th_style}>Foce</th><td {td_style}>{dati.get('foce', 'N/D')}</td></tr><tr><th {th_style}>Interregionale</th><td {td_style}>{dati.get('interregionale', 'N/D')}</td></tr>{f"<tr><th {th_style}>Note</th><td {td_style}>{dati['note']}</td></tr>" if dati.get('note') else ""}</table><small><i>Fonte: Immagine Bacini Idrografici</i></small>"""
    popup = folium.Popup(html_popup, max_width=300)
    folium.Marker(location=dati['coords'],popup=popup, tooltip=f"Bacino: {nome}", icon=folium.Icon(color='purple', icon='glyphicon-folder-open')).add_to(fg_bacini)
    dati_ricerca_totali.append({ "type": "Feature", "geometry": {"type": "Point", "coordinates": [dati['coords'][1], dati['coords'][0]]}, "properties": {"name": f"Bacino: {nome}", "popup": html_popup, "layer": "Bacini Idrografici"} })

# --- Plugin Generali e Draw ---
Search(layer=folium.GeoJson({"type": "FeatureCollection", "features": dati_ricerca_totali}, name="geojson_search_layer"), search_label='name', search_zoom=12, geom_type='Point', placeholder='Cerca per nome...', collapsed=True, position='topleft').add_to(mappa_multi)
MiniMap(toggle_display=True, position='bottomright', zoom_level_offset=-4).add_to(mappa_multi)
MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(mappa_multi)
MousePosition(position='topright', separator=' | Lon: ', lng_first=True, prefix="Lat:").add_to(mappa_multi)
Fullscreen(position='topleft').add_to(mappa_multi)
# Aggiunta Plugin Draw per interattività utente
Draw(
    export=True, # Permette di esportare ciò che si disegna
    filename='miei_disegni.geojson',
    position='topleft',
    draw_options={'polyline': {'shapeOptions': {'color': '#FF00FF'}}, # Opzioni per linee (viola)
                  'polygon': {'shapeOptions': {'color': '#FF00FF'}}, # Opzioni per poligoni
                  'rectangle': {'shapeOptions': {'color': '#FF00FF'}},
                  'circle': {'shapeOptions': {'color': '#FF00FF'}},
                  'marker': {}}, # Opzioni per marcatori
    edit_options={'edit': True} # Permette di modificare/cancellare
).add_to(mappa_multi)
print("\nAggiunto plugin 'Draw' per disegno/annotazioni utente.")

# --- Legenda Fiumi (HTML Custom) ---
legend_html = """<div style="position: fixed; bottom: 20px; right: 10px; width: 150px; height: auto; border:2px solid grey; z-index:9999; font-size:11px; background-color: rgba(255, 255, 255, 0.85); padding: 5px; border-radius: 5px;"> <h4 style="margin-top:0; margin-bottom:5px; text-align:center; font-size:13px;">Legenda Fiumi</h4>"""
for nome, colore in colori_legenda_fiumi.items():
    legend_html += f'<i style="background:{colore}; width: 15px; height: 8px; display: inline-block; margin-right: 4px; opacity: 0.85; border: 1px solid #555;"></i>{nome}<br>'
legend_html += """</div>"""; mappa_multi.get_root().html.add_child(Element(legend_html))

# --- Controllo Layer (Alla Fine!) ---
folium.LayerControl(collapsed=False).add_to(mappa_multi) # Non collassato

# --- Salvataggio e Apertura Mappa ---
output_file = 'mappa_super_basilicata_finale_v3.html'
mappa_multi.save(output_file)
print(f"\nMappa finale salvata come '{output_file}'")
print("\n--- AZIONI RICHIESTE DA TE ---")
print("1. *** CRUCIALE *** POPOLA LE COORDINATE 'coords' nel dizionario 'fiumi_manuali' con PUNTI REALI per visualizzare fiumi/affluenti.")
print("   (Le coordinate attuali sono solo placeholder schematici e INVENTATI!)")
print("2. (Opzionale) Trova URL/proprietà validi per GeoJSON Aree Protette e/o Province e aggiorna i placeholder.")
print("3. (Opzionale) Se hai altri dettagli specifici da aggiungere, fammelo sapere.")

full_path = os.path.abspath(output_file)
webbrowser.open('file://' + full_path)
print("\nMappa aperta nel browser.")
# Suggerimento: Assicurati di avere le librerie aggiornate: pip install --upgrade folium branca requests numpy