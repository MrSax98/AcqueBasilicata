# Mappa idrica della Basilicata

Script Python (`build_map.py`) che genera una mappa Folium da `data/*.json`.

- Test: `python -m pytest` (senza rete). Controllo manuale: `python build_map.py --open` e verifica che la console del browser non mostri errori JS.
- I contenuti stanno in `data/`, non nel codice: per aggiungere una diga o un bacino si modifica il JSON.
- Non disegnare mai percorsi o coordinate inventati: `data/fiumi.json` ha solo coordinate reali, altrimenti `coords` resta vuoto.
- Popup HTML sempre tramite `popup_table`; icone Folium solo con colori validi (`lightblue`, non `cyan`).
- Ogni plugin Folium che prende un `layer` (es. `Search`) richiede che il layer sia aggiunto alla mappa.
- Niente tile che richiedono chiave API; la mappa di base è OpenStreetMap.
- Testo utente e commenti in italiano.
