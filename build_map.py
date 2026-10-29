"""Mappa interattiva del sistema idrico della Basilicata (Folium).

Uso:
    python build_map.py [--output mappa_basilicata.html] [--open]
                        [--regioni-geojson URL_O_FILE]
                        [--province-geojson URL_O_FILE --province-prop CAMPO_NOME]
                        [--parchi-geojson URL_O_FILE --parchi-prop CAMPO_NOME]

I dati stanno in data/sistema_idrico.json; i percorsi dei fiumi in data/fiumi.json
(coordinate [lat, lon] reali: i fiumi senza coordinate non vengono disegnati).
"""

import argparse
import json
import webbrowser
from pathlib import Path

import folium
import requests
from branca.element import Element
from folium.plugins import Draw, Fullscreen, MarkerCluster, MeasureControl, MiniMap, MousePosition, Search

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sistema_idrico.json"
RIVERS_FILE = BASE_DIR / "data" / "fiumi.json"
REGIONI_URL = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"
PARCHI_BASILICATA = ("pollino", "appennino lucano", "gallipoli cognato")
TH = "style='text-align:left; padding: 4px; background-color: #f0f0f0; border-bottom: 1px solid #ddd;'"
TD = "style='padding: 4px; border-bottom: 1px solid #ddd;'"


def popup_table(title, rows, source):
    """HTML del popup: titolo, tabella (etichetta, valore) e fonte. Le righe con valore vuoto sono omesse."""
    body = "".join(f"<tr><th {TH}>{label}</th><td {TD}>{value}</td></tr>" for label, value in rows if value)
    return (
        f"<h4>{title}</h4>"
        f'<table style="width:100%; border-collapse: collapse; font-size: 0.9em;">{body}</table>'
        f"<small><i>Fonte dati: {source}</i></small>"
    )


def bold(text):
    return f"<b>{text}</b>"


def nd(d, key):
    return d.get(key, "N/D")


# --- Dati ------------------------------------------------------------------------------------


def load_data(path=DATA_FILE):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_rivers(path=RIVERS_FILE):
    """Carica i fiumi e verifica che ogni punto sia una coppia [lat, lon] di numeri."""
    rivers = json.loads(Path(path).read_text(encoding="utf-8"))
    for name, river in rivers.items():
        for point in river["coords"]:
            if len(point) != 2 or not all(isinstance(x, (int, float)) for x in point):
                raise ValueError(f"fiume '{name}': punto non valido {point!r}, atteso [lat, lon]")
    return rivers


def load_geojson(source, timeout=15):
    """GeoJSON da URL http(s) o da file locale; solleva ValueError se non ha 'features'."""
    if str(source).startswith(("http://", "https://")):
        response = requests.get(source, timeout=timeout)
        response.raise_for_status()
        geojson = response.json()
    else:
        geojson = json.loads(Path(source).read_text(encoding="utf-8"))
    if not isinstance(geojson, dict) or not isinstance(geojson.get("features"), list):
        raise ValueError("GeoJSON non valido: manca l'elenco 'features'")
    return geojson


# --- Layer -----------------------------------------------------------------------------------


def search_feature(label, coords, html, layer):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [coords[1], coords[0]]},
        "properties": {"name": label, "popup": html, "layer": layer},
    }


def add_infrastrutture(fmap, data, search):
    """Gruppo 'Visualizza: Infrastrutture Idriche' (dighe, traverse, città, potabilizzatori, centrali)."""
    group = folium.FeatureGroup(name="Visualizza: Infrastrutture Idriche", overlay=False, show=True).add_to(fmap)
    dighe = MarkerCluster(name="Dighe").add_to(group)
    traverse = MarkerCluster(name="Traverse").add_to(group)
    citta = folium.FeatureGroup(name="Città Principali").add_to(group)
    potabilizzatori = folium.FeatureGroup(name="Potabilizzatori").add_to(group)
    centrali = folium.FeatureGroup(name="Centrali Idroelettriche").add_to(group)

    def add(target, name, d, tooltip, html, width, color, icon, search_label):
        popup = folium.Popup(html, max_width=width)
        folium.Marker(d["coords"], popup=popup, tooltip=tooltip, icon=folium.Icon(color=color, icon=icon)).add_to(target)
        if search_label:
            search.append(search_feature(search_label, d["coords"], html, "Infrastrutture Idriche"))

    for name, d in data["dighe"].items():
        html = popup_table(name, [
            ("Schema Idrico", bold(nd(d, "schema"))), ("Fiume", nd(d, "fiume")),
            ("Capacità Utile", nd(d, "capacita")), ("Anno Realiz.", nd(d, "anno")), ("Tipo", nd(d, "tipo")),
            ("Uso Principale", nd(d, "uso")), ("Status (nel PDF)", nd(d, "status")), ("Gestore", nd(d, "gestore")),
            ("Collegamenti", d.get("connections")), ("Note", d.get("note")),
        ], "sistema_idrico.pdf / quarry.pdf")
        add(dighe, name, d, f"Diga: {name} ({nd(d, 'schema')})", html, 400, "blue", "glyphicon-home", f"Diga: {name}")

    for name, d in data["traverse"].items():
        html = popup_table(name, [
            ("Schema Idrico", bold(nd(d, "schema"))), ("Fiume", nd(d, "fiume")), ("Funzione", nd(d, "funzione")),
            ("Stato", nd(d, "stato")), ("Collegamenti", d.get("connections")), ("Note", d.get("note")),
        ], "sistema_idrico.pdf / quarry.pdf")
        add(traverse, name, d, f"Traversa: {name} ({nd(d, 'schema')})", html, 400, "green", "glyphicon-transfer", f"Traversa: {name}")

    for name, d in data["citta"].items():
        folium.Marker(d["coords"], popup=d["desc"], tooltip=name, icon=folium.Icon(color="red", icon="info-sign")).add_to(citta)

    for name, d in data["potabilizzatori"].items():
        html = popup_table(f"Potabilizzatore: {name}", [
            ("Schema Idrico", bold(nd(d, "schema"))), ("Al Servizio di", nd(d, "servizio")),
            ("Alimentato Da", nd(d, "alimentato_da")),
        ], "sistema_idrico.pdf")
        add(potabilizzatori, name, d, f"Potabilizzatore: {name}", html, 350, "orange", "glyphicon-filter", f"Potabilizzatore: {name}")

    for name, d in data["centrali"].items():
        html = popup_table(f"Centrale Idroelettrica: {name}", [
            ("Schema Idrico", bold(nd(d, "schema"))), ("Posizione/Fiume", nd(d, "fiume")),
            ("Alimentato Da", nd(d, "alimentato_da")), ("Alimenta", nd(d, "alimenta")), ("Gestore", nd(d, "gestore")),
        ], "sistema_idrico.pdf")
        add(centrali, name, d, f"Centrale Idroelettrica: {name}", html, 350, "cadetblue", "glyphicon-flash", f"Centrale Idroelettrica: {name}")


def add_bacini(fmap, data, search):
    group = folium.FeatureGroup(name="Visualizza: Bacini Idrografici", overlay=False, show=False).add_to(fmap)
    for name, d in data["bacini"].items():
        html = popup_table(f"Bacino: {name}", [
            ("Superficie", f"{nd(d, 'area_kmq')} km²"), ("Foce", nd(d, "foce")),
            ("Interregionale", nd(d, "interregionale")), ("Note", d.get("note")),
        ], "Immagine Bacini Idrografici")
        folium.Marker(d["coords"], popup=folium.Popup(html, max_width=300), tooltip=f"Bacino: {name}",
                      icon=folium.Icon(color="purple", icon="glyphicon-folder-open")).add_to(group)
        search.append(search_feature(f"Bacino: {name}", d["coords"], html, "Bacini Idrografici"))


def add_idrografia(fmap, data, rivers):
    """Foci dei fiumi principali e, solo per quelli con coordinate reali, il percorso. Restituisce i fiumi disegnati."""
    group = folium.FeatureGroup(name="Idrografia", overlay=True, show=True).add_to(fmap)
    drawn = {}
    for name, river in rivers.items():
        if len(river["coords"]) >= 2:
            folium.PolyLine(river["coords"], tooltip=f"Fiume/Affluente: {name}", color=river["color"],
                            weight=river["weight"], opacity=river["opacity"]).add_to(group)
            drawn[name] = river["color"]
    for name, d in data["foci"].items():
        popup = f"<b>{name}</b><br>Fiume: {d['fiume']}<br>Sbocca in: Mar {d['mare']}"
        folium.Marker(d["coords"], tooltip=name, popup=popup, icon=folium.Icon(color="lightblue", icon="glyphicon-flag")).add_to(group)
    return drawn


def add_punti_extra(fmap, data):
    group = folium.FeatureGroup(name="Punti Rilevanti / Extra", overlay=True, show=True).add_to(fmap)
    for name, d in data["punti_extra"].items():
        icon = d.get("icon", {"color": "gray", "icon": "info-sign"})
        folium.Marker(d["coords"], tooltip=name, popup=d.get("desc", name),
                      icon=folium.Icon(color=icon["color"], icon=icon["icon"], prefix="glyphicon")).add_to(group)


def add_legenda_fiumi(fmap, drawn):
    if not drawn:
        return
    items = "".join(
        f'<i style="background:{color}; width: 15px; height: 8px; display: inline-block; margin-right: 4px; '
        f'opacity: 0.85; border: 1px solid #555;"></i>{name}<br>' for name, color in drawn.items()
    )
    html = (
        '<div style="position: fixed; bottom: 20px; right: 10px; width: 150px; border:2px solid grey; z-index:9999; '
        'font-size:11px; background-color: rgba(255, 255, 255, 0.85); padding: 5px; border-radius: 5px;">'
        f'<h4 style="margin-top:0; margin-bottom:5px; text-align:center; font-size:13px;">Legenda Fiumi</h4>{items}</div>'
    )
    fmap.get_root().html.add_child(Element(html))


def name_style(prop, styles, default):
    """style_function di GeoJson: stile scelto in base al valore (minuscolo) della proprietà `prop`."""
    def style(feature):
        value = str(feature.get("properties", {}).get(prop, "")).lower()
        return styles.get(value, default)
    return style


def add_geojson_layer(fmap, source, name, prop, style, highlight, show=True, keep=None):
    """Aggiunge un layer GeoJSON; se non è leggibile stampa un avviso e prosegue. `keep` filtra le feature."""
    try:
        geojson = load_geojson(source)
    except (requests.RequestException, OSError, ValueError) as e:
        print(f"ATTENZIONE: layer '{name}' non aggiunto ({source}): {e}")
        return False
    if keep:
        geojson["features"] = [f for f in geojson["features"] if keep(str(f.get("properties", {}).get(prop, "")).lower())]
        if not geojson["features"]:
            print(f"ATTENZIONE: layer '{name}' non aggiunto: nessuna feature corrisponde")
            return False
    folium.GeoJson(geojson, name=name, style_function=style, highlight_function=lambda f: highlight,
                   tooltip=folium.features.GeoJsonTooltip(fields=[prop], aliases=[f"{name}:"], sticky=False),
                   overlay=True, show=show).add_to(fmap)
    return True


def add_confini(fmap, regioni=REGIONI_URL, province=None, province_prop=None, parchi=None, parchi_prop=None):
    default = {"fillOpacity": 0, "weight": 0}
    add_geojson_layer(
        fmap, regioni, "Confini Regionali", "reg_name",
        name_style("reg_name", {
            "basilicata": {"fillOpacity": 0.1, "weight": 3, "color": "#FF0000", "fillColor": "#FF0000"},
            **{r: {"weight": 1.5, "color": "#FFA500", "fillOpacity": 0.05} for r in ("puglia", "campania", "calabria")},
        }, default),
        {"weight": 3, "fillOpacity": 0.3},
    )
    if province:
        add_geojson_layer(
            fmap, province, "Confini Provinciali (PZ/MT)", province_prop,
            name_style(province_prop, {
                "potenza": {"fillColor": "#fec44f", "color": "#fec44f", "weight": 1, "fillOpacity": 0.2},
                "matera": {"fillColor": "#7bccc4", "color": "#7bccc4", "weight": 1, "fillOpacity": 0.2},
            }, default),
            {"weight": 2, "fillOpacity": 0.4},
        )
    if parchi:
        style = {"fillColor": "#8FBC8F", "color": "#2E8B57", "weight": 1.5, "fillOpacity": 0.4}
        add_geojson_layer(
            fmap, parchi, "Aree Protette Principali", parchi_prop, lambda f: style, {"fillOpacity": 0.6, "weight": 2.5},
            show=False, keep=lambda nome: any(p in nome for p in PARCHI_BASILICATA),
        )


def add_tiles(fmap):
    folium.TileLayer("OpenStreetMap", name="Mappa Standard", overlay=False, show=True).add_to(fmap)
    folium.TileLayer("https://tile.opentopomap.org/{z}/{x}/{y}.png", name="Mappa Terreno", overlay=False, show=False,
                     attr="Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)").add_to(fmap)
    folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                     name="Satellite Esri", overlay=False, show=False, attr="Esri").add_to(fmap)


def add_plugins(fmap, search):
    # Il layer deve stare sulla mappa perché Search lo interroghi; è invisibile e fuori dal controllo dei layer.
    layer = folium.GeoJson(
        {"type": "FeatureCollection", "features": search}, name="geojson_search_layer", control=False,
        marker=folium.CircleMarker(radius=8, opacity=0, fill_opacity=0),
        style_function=lambda feature: {"opacity": 0, "fillOpacity": 0},
    ).add_to(fmap)
    Search(layer=layer, search_label="name", search_zoom=12, geom_type="Point", placeholder="Cerca per nome...",
           collapsed=True, position="topleft", initial=False).add_to(fmap)
    MiniMap(toggle_display=True, position="bottomright", zoom_level_offset=-4).add_to(fmap)
    MeasureControl(position="bottomleft", primary_length_unit="kilometers").add_to(fmap)
    MousePosition(position="topright", separator=" | Lon: ", lng_first=True, prefix="Lat:").add_to(fmap)
    Fullscreen(position="topleft").add_to(fmap)
    shape = {"shapeOptions": {"color": "#FF00FF"}}
    Draw(export=True, filename="miei_disegni.geojson", position="topleft",
         draw_options={"polyline": shape, "polygon": shape, "rectangle": shape, "circle": shape, "marker": {}},
         edit_options={"edit": True}).add_to(fmap)


def build_map(data, rivers, **confini):
    """Costruisce la mappa completa. `confini`: argomenti di add_confini (regioni, province, parchi, ...)."""
    fmap = folium.Map(location=data["centro"], zoom_start=9, tiles=None)
    add_tiles(fmap)
    add_confini(fmap, **confini)
    drawn = add_idrografia(fmap, data, rivers)
    add_punti_extra(fmap, data)
    search = []
    add_infrastrutture(fmap, data, search)
    add_bacini(fmap, data, search)
    add_plugins(fmap, search)
    add_legenda_fiumi(fmap, drawn)
    folium.LayerControl(collapsed=False).add_to(fmap)
    return fmap


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=Path("mappa_basilicata.html"), help="file HTML di output")
    parser.add_argument("--open", action="store_true", help="apri la mappa nel browser al termine")
    parser.add_argument("--regioni-geojson", default=REGIONI_URL, help="URL o file GeoJSON dei confini regionali")
    parser.add_argument("--province-geojson", help="URL o file GeoJSON dei confini provinciali")
    parser.add_argument("--province-prop", help="campo con il nome della provincia (es. DEN_UTS)")
    parser.add_argument("--parchi-geojson", help="URL o file GeoJSON delle aree protette")
    parser.add_argument("--parchi-prop", help="campo con il nome dell'area protetta")
    args = parser.parse_args(argv)
    for layer, prop in (("province", args.province_prop), ("parchi", args.parchi_prop)):
        if getattr(args, f"{layer}_geojson") and not prop:
            parser.error(f"--{layer}-geojson richiede --{layer}-prop")

    fmap = build_map(load_data(), load_rivers(), regioni=args.regioni_geojson,
                     province=args.province_geojson, province_prop=args.province_prop,
                     parchi=args.parchi_geojson, parchi_prop=args.parchi_prop)
    fmap.save(args.output)
    print(f"Mappa salvata in {args.output}")
    if args.open:
        webbrowser.open(args.output.resolve().as_uri())


if __name__ == "__main__":
    main()
