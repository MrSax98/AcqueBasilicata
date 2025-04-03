# Mappa Interattiva del Sistema Idrico della Basilicata

## Descrizione

Questo progetto contiene uno script Python (`BasilicataIdrica.py`) che utilizza la libreria `Folium` per generare una mappa HTML interattiva e ricca di dettagli sul sistema di gestione delle risorse idriche della regione Basilicata, Italia.

La mappa visualizza diverse infrastrutture (dighe, traverse, centrali, potabilizzatori), i principali bacini idrografici, confini amministrativi, aree protette (se i dati esterni sono forniti) e altri punti di interesse legati al contesto idrico regionale e interregionale (Puglia, Calabria). Include inoltre una rappresentazione schematica dei principali fiumi e affluenti, **le cui coordinate devono essere inserite manualmente dall'utente nello script**.

## Funzionalità Principali

* **Visualizzazione Layer Multipli:** Dati organizzati in layer sovrapponibili e selezionabili tramite un controllo intuitivo.
* **Viste Tematiche Commutabili:** Possibilità di passare da una vista focalizzata sulle **Infrastrutture Idriche** a una focalizzata sui **Bacini Idrografici** tramite radio button nel controllo layer.
* **Layer Infrastrutture:**
    * Marcatori clusterizzati per Dighe, Traverse, Potabilizzatori, Centrali Idroelettriche.
    * Popup dettagliati per ogni infrastruttura con dati tecnici (capacità, anno, tipo, gestore, stato), schema idrico di appartenenza, connessioni principali e fonti dei dati.
    * Marcatori per Città Principali (Potenza, Matera).
* **Layer Bacini Idrografici:**
    * Marcatori per i principali bacini regionali/interregionali.
    * Popup con informazioni su area stimata, foce e carattere interregionale.
* **Layer Contestuali (Attivabili/Disattivabili):**
    * **Confini Regionali:** Evidenzia la Basilicata (in rosso, se possibile) e le regioni confinanti. Utilizza uno stile semplice come fallback in caso di errori di rendering. (*Dati GeoJSON esterni*).
    * **Confini Provinciali:** Evidenzia le province di Potenza e Matera. (*Richiede URL GeoJSON valido fornito dall'utente*).
    * **Aree Protette Principali:** Visualizza i Parchi Nazionali/Regionali rilevanti (Pollino, Appennino Lucano, Gallipoli Cognato). (*Richiede URL GeoJSON valido fornito dall'utente*).
    * **Idrografia (Manuale):**
        * Disegna i percorsi dei fiumi principali (Bradano, Basento, Cavone, Agri, Sinni, Noce) e degli affluenti specificati, **basandosi esclusivamente sulle coordinate inserite manualmente nel codice**. Le coordinate fornite di default sono **PLACEHOLDER INVENTATI**.
        * Aggiunge marcatori specifici per le **foci** dei fiumi principali.
    * **Punti Rilevanti / Extra:** Include marcatori per punti sulla costa Jonica (legati all'erosione), nodi chiave del sistema in Puglia, sedi stimate dei Consorzi di Bonifica e un punto concettuale per le Sorgenti Appenniniche.
* **Interattività Avanzata:**
    * Zoom, Pan standard.
    * Tooltip informativi al passaggio del mouse su quasi tutti gli elementi.
    * Clustering (`MarkerCluster`) per gestire la densità dei marcatori.
    * Funzione di Ricerca (`Search`) per nome su infrastrutture e bacini.
    * Mini Mappa di contesto (`MiniMap`).
    * Strumento di Misura distanze/aree (`MeasureControl`).
    * Visualizzazione Coordinate Mouse (`MousePosition`).
    * Modalità Schermo Intero (`Fullscreen`).
    * **Strumenti di Disegno (`Draw`):** Permette all'utente di disegnare poligoni, linee, marcatori e cerchi direttamente sulla mappa e di esportarli come GeoJSON.
    * Legenda chiara per i colori assegnati ai fiumi principali disegnati manualmente.

## Fonti dei Dati

Le informazioni visualizzate sulla mappa provengono da una combinazione di fonti:

1.  **Documenti Forniti:**
    * `quarry.pdf`: Articolo (presumibilmente "Quarry & Construction", Sett. 2009) con dati su infrastrutture, schemi idrici, contesto generale ed erosione costiera.
    * `sistema_idrico.pdf`: Documento tecnico con dettagli su schemi, componenti, capacità, anni, stato operativo, gestori e connessioni.
    * `Numero 2025-04-03 alle 13.26.38.jpg`: Immagine con testo e mappa schematica sui bacini idrografici (nomi, aree, foci, interregionalità).
2.  **Dati Esterni (Caricati via URL):**
    * Confini Regionali Italiani: GeoJSON da Openpolis/GitHub (basato su dati ISTAT). *URL nello script.*
    * Confini Provinciali Italiani: **NECESSARIO URL GeoJSON VALIDO** da inserire nello script.
    * Aree Protette: **NECESSARIO URL GeoJSON VALIDO** da inserire nello script.
3.  **Dati Manuali / Stimati:**
    * **Percorsi Fiumi/Affluenti:** **L'utente DEVE inserire manualmente** le coordinate nel dizionario `fiumi_manuali`. Le coordinate presenti nello script sono **PLACEHOLDER INVENTATI e NON ACCURATI**.
    * Coordinate Stimate: Posizione delle foci dei fiumi, sedi dei Consorzi di Bonifica, punti esterni (Puglia), punti costa, località chiave (Senise, Missanello, Ferrandina), punto concettuale sorgenti.

## Requisiti Manuali Fondamentali

Questo script è una *struttura avanzata* che richiede interventi manuali per funzionare al meglio:

1.  **Percorsi Fluviali:** **È indispensabile modificare il dizionario `fiumi_manuali` nel file `.py`.** Sostituire le liste vuote `[]` e i punti placeholder con liste di coordinate `[latitudine, longitudine]` reali (anche approssimate) per ogni fiume e affluente che si desidera visualizzare. Senza questo passaggio, i fiumi non verranno disegnati o appariranno come linee inventate.
2.  **Dati GeoJSON Esterni (Province, Parchi):** Per visualizzare i Confini Provinciali e le Aree Protette, trovare URL GeoJSON validi e i corretti nomi delle proprietà contenenti i nomi identificativi (es. delle province, dei parchi). Aggiornare i placeholder (`geojson_..._url`, `..._name_property`) nello script.

## Tecnologie Utilizzate

* **Python 3**
* **Folium:** Libreria principale per la generazione delle mappe interattive.
* **Requests:** Per scaricare dati GeoJSON da URL.
* **NumPy:** Usato per generare i punti *placeholder* schematici dei fiumi.
* **(Opzionale)** Potrebbe essere utile `geopandas` per manipolare dati GeoJSON più complessi, ma non è richiesto da questo script.

## Setup e Installazione

1.  Assicurati di avere Python 3 installato.
2.  Clona o scarica questo repository.
3.  Installa le librerie necessarie (preferibilmente in un ambiente virtuale):
    ```bash
    pip install folium requests numpy branca
    ```

## Utilizzo

1.  **(OBBLIGATORIO per i fiumi)** Apri il file `BasilicataIdrica.py` con un editor di testo/codice. Localizza il dizionario `fiumi_manuali` e inserisci le coordinate `[lat, lon]` per i fiumi e gli affluenti che vuoi mappare.
2.  **(Opzionale)** Trova e inserisci gli URL e i nomi delle proprietà per i file GeoJSON delle Province e delle Aree Protette nei rispettivi placeholder nello script.
3.  Esegui lo script dal terminale, navigando nella cartella del progetto:
    ```bash
    python BasilicataIdrica.py
    ```
4.  Lo script stamperà messaggi sulla console riguardo al caricamento dei dati (controlla eventuali errori o avvisi) e genererà un file HTML (es. `mappa_super_basilicata_finale_v3.html`) nella stessa cartella.
5.  Apri il file HTML generato con un browser web moderno (Firefox, Chrome, Edge, Safari).

## Output

Un file HTML (`mappa_super_basilicata_finale_v3.html` o simile) contenente la mappa interattiva. Esplora i diversi layer usando il controllo in alto a destra, clicca sui marcatori per i popup, usa gli strumenti di zoom, misura e disegno.

## Limitazioni e Note

* **Accuratezza Fiumi Manuali:** I percorsi fluviali sono **altamente dipendenti dalla qualità e quantità dei punti inseriti manualmente** e non avranno l'accuratezza di dati GIS professionali. Le coordinate placeholder fornite sono **inventate e non geograficamente corrette**.
* **Dati Esterni:** La visualizzazione dei confini (Regioni, Province) e Parchi dipende dalla **disponibilità e correttezza degli URL GeoJSON e dei nomi delle proprietà specificati**. Se un URL non è valido o i dati sono corrotti, il layer corrispondente non verrà aggiunto (controllare l'output della console).
* **Styling Regioni:** Lo script tenta uno stile differenziato per le regioni, ma potrebbe ricadere su uno stile semplice in caso di errori interni di Folium.
* **Coordinate Stimate:** Diverse coordinate (sedi consorzi, foci, ecc.) sono stimate e servono a dare un'indicazione geografica approssimativa.

---

CODICE SCRITTO CON L'AIUTO DI GEMINI (GOOGLE)

*(Puoi aggiungere qui informazioni su Licenza, Contatti, Come Contribuire, ecc. se lo desideri)*
