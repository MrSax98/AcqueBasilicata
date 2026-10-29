# Mappa Interattiva del Sistema Idrico della Basilicata

Script Python (`build_map.py`) che usa [Folium](https://python-visualization.github.io/folium/) per generare una mappa HTML interattiva del sistema di gestione delle risorse idriche della Basilicata, con le connessioni verso Puglia e Calabria.

## Cosa mostra

- **Viste commutabili** (radio button): *Infrastrutture Idriche* e *Bacini Idrografici*.
- **Infrastrutture:** dighe e traverse (clusterizzate), potabilizzatori, centrali idroelettriche e città principali, con popup tecnici (capacità, anno, tipo, gestore, stato, schema idrico, collegamenti, fonte).
- **Bacini idrografici:** area stimata, foce, carattere interregionale.
- **Layer attivabili:** confini regionali (evidenziata la Basilicata), foci dei fiumi principali, punti rilevanti (costa Jonica, nodi pugliesi, consorzi di bonifica, sorgenti, località chiave) e, se forniti, confini provinciali e aree protette.
- **Strumenti:** ricerca per nome, minimappa, misura di distanze/aree, coordinate del mouse, schermo intero, disegno con esportazione GeoJSON, tre mappe di base (standard, terreno, satellite).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
python build_map.py                     # scrive mappa_basilicata.html
python build_map.py --open              # e la apre nel browser
python build_map.py --output mappa.html
```

I confini regionali vengono scaricati da [openpolis/geojson-italy](https://github.com/openpolis/geojson-italy) (basato su dati ISTAT). Per usare un'altra fonte o un file locale: `--regioni-geojson URL_O_FILE`.

Layer opzionali, da attivare indicando sorgente GeoJSON e campo che contiene il nome:

```bash
python build_map.py \
  --province-geojson province.geojson --province-prop DEN_UTS \
  --parchi-geojson aree_protette.geojson --parchi-prop NOME
```

Le province Potenza e Matera vengono colorate; delle aree protette restano Pollino, Appennino Lucano e Gallipoli Cognato. Se un URL o un file non è leggibile, il layer viene saltato con un avviso e la mappa si genera comunque.

## Dati

| File | Contenuto |
|---|---|
| `data/sistema_idrico.json` | dighe, traverse, città, potabilizzatori, centrali, bacini, foci, punti extra |
| `data/fiumi.json` | colore, spessore e **coordinate** dei percorsi fluviali |

**Fiumi.** Le coordinate dei fiumi in `data/fiumi.json` sono vuote: i percorsi reali non erano disponibili, e le versioni precedenti disegnavano linee casuali presentate come fiumi. Un fiume compare in mappa (con la legenda) solo se gli si assegnano almeno due punti `[latitudine, longitudine]` reali, per esempio da un GeoJSON dell'idrografia. Punti non numerici fanno fallire il caricamento con un messaggio che indica il fiume.

**Fonti dei dati.** Documenti usati per compilare il JSON (non inclusi in questa repository): `quarry.pdf` (articolo su infrastrutture, schemi idrici ed erosione costiera), `sistema_idrico.pdf` (schemi, componenti, capacità, anni, stato, gestori), un'immagine con la mappa schematica dei bacini. Posizioni di foci, consorzi, località e sorgenti sono **stimate** e danno solo un'indicazione geografica.

## Test

```bash
pip install -r requirements-dev.txt
python -m pytest
```

I test non usano la rete: i GeoJSON sono generati al volo.

---

Codice scritto con l'aiuto di Gemini (Google).
