# Mappa Interattiva del Sistema Idrico della Basilicata

Questo repository contiene uno script Python per generare una mappa web interattiva del sistema idrico e dei bacini idrografici della regione Basilicata, Italia, utilizzando la libreria Folium.

## Descrizione

Lo script crea una mappa HTML interattiva (`.html`) che visualizza diverse componenti del sistema idrico lucano:

* **Infrastrutture Idriche:** Dighe, traverse, potabilizzatori, centrali idroelettriche.
* **Bacini Idrografici:** Principali bacini della regione.
* **Confini Regionali:** Evidenzia la Basilicata e le regioni limitrofe.
* **Rete Idrografica:** *Opzionalmente*, visualizza i principali fiumi (richiede configurazione manuale).

La mappa è navigabile, con funzionalità di zoom, pan, e diversi strumenti interattivi.

## Funzionalità Principali

* Mappa interattiva basata su Folium (e Leaflet.js).
* Visualizzazione di dighe, traverse, potabilizzatori, centrali idroelettriche e città principali.
* Visualizzazione dei principali bacini idrografici.
* Layer per i confini regionali italiani (fonte: Openpolis), con stile differenziato per la Basilicata e le regioni confinanti.
* **Layer opzionale per i fiumi principali** (richiede la configurazione di un URL GeoJSON).
* Colorazione differenziata per i fiumi principali identificati.
* **Clustering dei marker** (per dighe e traverse) per una migliore leggibilità a diversi livelli di zoom.
* **Popup informativi** dettagliati per ogni elemento sulla mappa (accessibili cliccando sui marker).
* Diverse **mappe di base** selezionabili (Standard, Terreno, Satellite).
* **Barra di ricerca** per trovare elementi per nome.
* **MiniMap** per una vista d'insieme.
* **Strumento di misurazione** distanze.
* Visualizzazione delle **coordinate del mouse**.
* Pulsante **Fullscreen**.
* **Controllo Layer** per mostrare/nascondere i diversi set di dati (Infrastrutture vs Bacini, confini, fiumi, sfondi).
* **Legenda dinamica** per i colori dei fiumi (appare solo se il layer fiumi è caricato).

## Prerequisiti

* Python 3.x
* Le seguenti librerie Python:
    * `folium`
    * `requests`
    * `branca`

## Installazione

1.  **Clona il repository:**
    ```bash
    git clone <URL-DEL-TUO-REPOSITORY>
    cd <NOME-CARTELLA-REPOSITORY>
    ```
2.  **Installa le dipendenze:**
    È consigliabile creare un ambiente virtuale.
    ```bash
    python -m venv venv
    source venv/bin/activate  # Su Windows: venv\Scripts\activate
    pip install folium requests branca
    ```
    *(Potresti anche creare un file `requirements.txt` con le dipendenze per un'installazione più semplice: `pip install -r requirements.txt`)*

## Configurazione Essenziale (Dati Fiumi)

Lo script **richiede la configurazione manuale** per visualizzare il layer dei fiumi, poiché i dati GeoJSON specifici per i fiumi della Basilicata non sono inclusi direttamente o disponibili tramite un link fisso nello script originale.

1.  **Trova una fonte dati GeoJSON:** Devi reperire un file GeoJSON che contenga la geometria dei corsi d'acqua della Basilicata (o dell'area di interesse). Fonti possibili potrebbero essere portali open data regionali, nazionali (es. ISPRA, ISTAT), o progetti come OpenStreetMap (estratti tramite strumenti come Overpass Turbo o QGIS).
2.  **Identifica la proprietà del nome:** Apri il file GeoJSON (anche con un editor di testo) e individua quale "proprietà" (property) all'interno delle "features" contiene il nome del fiume (es. `"name"`, `"nome"`, `"NAMN1"`).
3.  **Modifica lo script Python:** Apri il file `.py` (o il notebook `.ipynb`).
4.  **Individua le seguenti righe:**
    ```python
    # Fiumi (Placeholder - DA COMPILARE)
    geojson_fiumi_basilicata_url = "INSERISCI_URL_GEOJSON_FIUMI_BASILICATA_QUI"
    river_name_property = "INSERISCI_NOME_PROPRIETA_FIUME_QUI"
    ```
5.  **Sostituisci i placeholder:**
    * Al posto di `"INSERISCI_URL_GEOJSON_FIUMI_BASILICATA_QUI"`, inserisci l'URL diretto al file GeoJSON che hai trovato. Se il file è locale, potresti doverlo caricare online (es. GitHub Gist, server personale) o adattare lo script per leggere file locali (sconsigliato per la portabilità).
    * Al posto di `"INSERISCI_NOME_PROPRIETA_FIUME_QUI"`, inserisci il nome esatto della proprietà che contiene il nome del fiume (es. `"nome"`).

**ATTENZIONE:** Senza completare questi passaggi, il layer dei fiumi non verrà visualizzato sulla mappa e vedrai un avviso nella console durante l'esecuzione dello script.

## Utilizzo

Una volta installate le dipendenze e (opzionalmente) configurato il layer dei fiumi, esegui lo script Python:

```bash
python nome_del_tuo_script.py
