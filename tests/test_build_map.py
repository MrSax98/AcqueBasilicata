import json

import folium
import pytest
from folium.plugins import MarkerCluster

import build_map

SQUARE = [[[15.8, 40.0], [16.8, 40.0], [16.8, 41.0], [15.8, 41.0], [15.8, 40.0]]]


def feature(prop, value):
    return {"type": "Feature", "properties": {prop: value}, "geometry": {"type": "Polygon", "coordinates": SQUARE}}


def write_geojson(path, features):
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    return path


def walk(element):
    yield element
    for child in element._children.values():
        yield from walk(child)


def of_type(fmap, cls):
    return [e for e in walk(fmap) if isinstance(e, cls)]


@pytest.fixture
def data():
    return build_map.load_data()


@pytest.fixture
def rivers():
    return build_map.load_rivers()


@pytest.fixture
def regioni(tmp_path):
    return write_geojson(tmp_path / "regioni.geojson", [feature("reg_name", "Basilicata"), feature("reg_name", "Lazio")])


def test_dati_completi_e_dentro_l_area(data):
    sizes = {k: len(data[k]) for k in ("dighe", "traverse", "citta", "potabilizzatori", "centrali", "bacini", "foci", "punti_extra")}
    assert sizes == {"dighe": 12, "traverse": 6, "citta": 2, "potabilizzatori": 2, "centrali": 2, "bacini": 8, "foci": 6, "punti_extra": 13}
    for key in sizes:
        for name, d in data[key].items():
            lat, lon = d["coords"]
            assert 39.8 <= lat <= 41.2 and 15.5 <= lon <= 17.4, f"{key}/{name} fuori area: {d['coords']}"


def test_popup_table_omette_righe_vuote():
    html = build_map.popup_table("Titolo", [("A", "1"), ("B", ""), ("C", None)], "fonte.pdf")
    assert "<h4>Titolo</h4>" in html and ">A</th>" in html
    assert ">B</th>" not in html and ">C</th>" not in html
    assert "fonte.pdf" in html


def test_mappa_ha_tutti_i_marcatori_e_i_gruppi(data, rivers, regioni):
    fmap = build_map.build_map(data, rivers, regioni=str(regioni))
    assert len(of_type(fmap, folium.Marker)) == 51
    names = {e.layer_name for e in walk(fmap) if isinstance(e, (folium.FeatureGroup, folium.GeoJson, MarkerCluster))}
    assert {"Visualizza: Infrastrutture Idriche", "Visualizza: Bacini Idrografici", "Idrografia",
            "Punti Rilevanti / Extra", "Confini Regionali", "Dighe", "Traverse"} <= names


def test_layer_di_ricerca_e_sulla_mappa(data, rivers, regioni):
    """Regressione: senza il layer sulla mappa il JS di Search lanciava ReferenceError e la mappa restava incompleta."""
    fmap = build_map.build_map(data, rivers, regioni=str(regioni))
    search = [g for g in of_type(fmap, folium.GeoJson) if g.layer_name == "geojson_search_layer"]
    assert len(search) == 1
    assert len(search[0].data["features"]) == 30  # 12 dighe, 6 traverse, 2 potabilizzatori, 2 centrali, 8 bacini
    assert "initial: false" in fmap.get_root().render()


def test_fiumi_senza_coordinate_reali_non_vengono_disegnati(data, rivers, regioni):
    """Regressione: prima venivano disegnati percorsi inventati con rumore casuale."""
    fmap = build_map.build_map(data, rivers, regioni=str(regioni))
    assert of_type(fmap, folium.PolyLine) == []
    assert "Legenda Fiumi" not in fmap.get_root().render()


def test_fiume_con_coordinate_reali_viene_disegnato_con_legenda(data, rivers, regioni):
    rivers["Bradano"]["coords"] = [[40.9, 15.9], [40.6, 16.4], [40.4, 16.86]]
    fmap = build_map.build_map(data, rivers, regioni=str(regioni))
    assert len(of_type(fmap, folium.PolyLine)) == 1
    html = fmap.get_root().render()
    assert "Legenda Fiumi" in html and "Bradano" in html


def test_coordinate_fiume_non_valide(tmp_path):
    bad = tmp_path / "fiumi.json"
    bad.write_text(json.dumps({"Agri": {"color": "#000", "weight": 1, "opacity": 1, "coords": [[40.2, "x"]]}}))
    with pytest.raises(ValueError, match="Agri"):
        build_map.load_rivers(bad)


def test_geojson_non_valido(tmp_path):
    path = tmp_path / "x.geojson"
    path.write_text('{"type": "Feature"}')
    with pytest.raises(ValueError, match="features"):
        build_map.load_geojson(path)


def test_layer_non_leggibile_viene_saltato_con_avviso(data, rivers, tmp_path, capsys):
    fmap = build_map.build_map(data, rivers, regioni=str(tmp_path / "manca.geojson"))
    assert "Confini Regionali" not in {getattr(e, "layer_name", None) for e in walk(fmap)}
    assert "ATTENZIONE" in capsys.readouterr().out


def test_parchi_filtrati_per_nome(data, rivers, regioni, tmp_path):
    parchi = write_geojson(tmp_path / "parchi.geojson", [feature("NOME", "Parco Nazionale del Pollino"), feature("NOME", "Parco Altrove")])
    fmap = build_map.build_map(data, rivers, regioni=str(regioni), parchi=str(parchi), parchi_prop="NOME")
    layer = next(g for g in of_type(fmap, folium.GeoJson) if g.layer_name == "Aree Protette Principali")
    assert [f["properties"]["NOME"] for f in layer.data["features"]] == ["Parco Nazionale del Pollino"]


def test_province_evidenziate(data, rivers, regioni, tmp_path):
    province = write_geojson(tmp_path / "prov.geojson", [feature("DEN", "Potenza"), feature("DEN", "Roma")])
    fmap = build_map.build_map(data, rivers, regioni=str(regioni), province=str(province), province_prop="DEN")
    layer = next(g for g in of_type(fmap, folium.GeoJson) if g.layer_name == "Confini Provinciali (PZ/MT)")
    style = layer.style_function
    assert style(layer.data["features"][0])["fillColor"] == "#fec44f"
    assert style(layer.data["features"][1])["weight"] == 0


def test_cli_scrive_il_file_e_non_apre_il_browser(regioni, tmp_path, monkeypatch):
    monkeypatch.setattr(build_map.webbrowser, "open", lambda *a, **k: pytest.fail("browser aperto senza --open"))
    out = tmp_path / "mappa.html"
    build_map.main(["--output", str(out), "--regioni-geojson", str(regioni)])
    assert out.stat().st_size > 10_000


def test_cli_open_apre_il_browser(regioni, tmp_path, monkeypatch):
    opened = []
    monkeypatch.setattr(build_map.webbrowser, "open", opened.append)
    build_map.main(["--output", str(tmp_path / "m.html"), "--regioni-geojson", str(regioni), "--open"])
    assert len(opened) == 1 and opened[0].startswith("file://")


def test_cli_geojson_senza_proprieta_nome(regioni):
    with pytest.raises(SystemExit) as exc:
        build_map.main(["--regioni-geojson", str(regioni), "--province-geojson", "x.geojson"])
    assert exc.value.code == 2
