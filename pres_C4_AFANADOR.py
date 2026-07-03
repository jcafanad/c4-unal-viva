import marimo

__generated_with = "0.23.10"
app = marimo.App(
    width="medium",
    layout_file="layouts/pres_C4_AFANADOR.slides.json",
)


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    return mo, mpatches, np, plt


@app.cell
def intro_territorio(UNAL, mo, np, plt):

    import math as _math
    import io as _io
    import json as _json
    import pathlib as _pathlib
    import shutil as _shutil
    import urllib.request as _urlreq
    import matplotlib.image as _mpimg
    from matplotlib.path import Path as _Path
    import matplotlib.patches as _mpatches
    from pyproj import Transformer as _Transformer
    import shapefile as _sf

    def _deg2tile(lat, lon, zoom):
        _n = 2 ** zoom
        _x = int((lon + 180.0) / 360.0 * _n)
        _lr = _math.radians(lat)
        _y = int((1.0 - _math.asinh(_math.tan(_lr)) / _math.pi) / 2.0 * _n)
        return _x, _y

    def _tile2lon(x, zoom):
        return x / (2 ** zoom) * 360.0 - 180.0

    def _tile2lat(y, zoom):
        return _math.degrees(_math.atan(_math.sinh(_math.pi * (1 - 2 * y / (2 ** zoom)))))

    def _get_osm_tiles():
        _cache_img = _pathlib.Path("/tmp/col_geo/osm_stitched.npy")
        _cache_ext = _pathlib.Path("/tmp/col_geo/osm_extent.json")
        if _cache_img.exists() and _cache_ext.exists():
            return np.load(str(_cache_img)), _json.loads(_cache_ext.read_text())

        _zoom = 11
        _x0, _y0 = _deg2tile(6.10, -74.15, _zoom)
        _x1, _y1 = _deg2tile(5.40, -73.00, _zoom)

        _rows = []
        for _ty in range(_y0, _y1 + 1):
            _cols = []
            for _tx in range(_x0, _x1 + 1):
                _url = f"https://tile.openstreetmap.org/{_zoom}/{_tx}/{_ty}.png"
                _req = _urlreq.Request(
                    _url, headers={"User-Agent": "viva-map/1.0 (academic-educational)"}
                )
                with _urlreq.urlopen(_req, timeout=12) as _r:
                    _tile = _mpimg.imread(_io.BytesIO(_r.read()))
                _cols.append(_tile)
            _rows.append(np.concatenate(_cols, axis=1))

        _img = np.concatenate(_rows, axis=0)
        _ext = [_tile2lon(_x0, _zoom), _tile2lon(_x1 + 1, _zoom),
                _tile2lat(_y1 + 1, _zoom), _tile2lat(_y0, _zoom)]

        np.save(str(_cache_img), _img)
        _cache_ext.write_text(_json.dumps(_ext))
        return _img, _ext

    def _territorio_fig():
        _dst = _pathlib.Path("/tmp/paramo_iguaque/")
        if not (_dst / "paramo.shp").exists():
            _dst.mkdir(exist_ok=True)
            for _f in (_pathlib.Path.home() / "Downloads" / "683747141a4a8").iterdir():
                if _f.suffix in (".shp", ".dbf", ".shx", ".prj", ".cpg"):
                    _shutil.copy2(_f, _dst / ("paramo" + _f.suffix))

        fig, (_ax_map, _ax_photo) = plt.subplots(1, 2, figsize=(13, 5.5))
        fig.patch.set_facecolor("#f0f0f0")

        for _sp in _ax_map.spines.values():
            _sp.set_visible(False)
        _ax_map.set_xticks([])
        _ax_map.set_yticks([])

        _osm, _ext = _get_osm_tiles()
        _ax_map.imshow(_osm, extent=_ext, origin="upper", aspect="auto", zorder=1)

        _boyaca = _json.loads(_pathlib.Path("/tmp/col_geo/boyaca.json").read_text())
        _rings = (_boyaca["geometry"]["coordinates"]
                  if _boyaca["geometry"]["type"] == "Polygon"
                  else [_r for _p in _boyaca["geometry"]["coordinates"] for _r in _p])
        for _ring in _rings:
            _ax_map.plot([_c[0] for _c in _ring], [_c[1] for _c in _ring],
                         color="#00427C", lw=2.0, alpha=0.85, zorder=2)

        _to_wgs = _Transformer.from_crs("EPSG:3116", "EPSG:4326", always_xy=True)
        _shpr = _sf.Reader("/tmp/paramo_iguaque/paramo.shp")
        _shape = _shpr.shape(0)
        _pts = np.array(_shape.points)
        _prts = list(_shape.parts) + [len(_pts)]

        _verts, _codes = [], []
        for _pi in range(len(_prts) - 1):
            _seg = _pts[_prts[_pi]:_prts[_pi + 1]]
            _lx, _ly = _to_wgs.transform(_seg[:, 0], _seg[:, 1])
            _codes += [_Path.MOVETO] + [_Path.LINETO] * (len(_lx) - 2) + [_Path.CLOSEPOLY]
            _verts.extend(zip(_lx, _ly))

        _ax_map.add_patch(_mpatches.PathPatch(
            _Path(_verts, _codes),
            facecolor="none", edgecolor="white", lw=5.5, zorder=3, alpha=0.85,
        ))
        _ax_map.add_patch(_mpatches.PathPatch(
            _Path(_verts, _codes),
            facecolor="#39FF14", alpha=0.28, edgecolor="#FF6B00", lw=2.8, zorder=4,
        ))

        _towns = [
            ("Villa de Leyva", -73.524, 5.633),
            ("Arcabuco", -73.456, 5.763),
            ("Tunja ★", -73.365, 5.535),
        ]
        import matplotlib.patheffects as _pe
        for _tn, _tlo, _tla in _towns:
            _ax_map.plot(_tlo, _tla, "o", ms=4, color="#FFD700", zorder=5, mec="white", mew=0.8)
            _ax_map.text(_tlo + 0.03, _tla + 0.02, _tn, fontsize=7, color="#111",
                         fontweight="bold", zorder=6,
                         path_effects=[_pe.withStroke(linewidth=2.5, foreground="white")])

        _ax_map.text(0.01, 0.01, "© OpenStreetMap contributors · límite páramo: IDEAM–IAvH",
                     transform=_ax_map.transAxes, fontsize=6, color="#555", va="bottom")
        _ax_map.set_xlim(-73.93, -73.13)
        _ax_map.set_ylim(5.53, 5.97)
        _ax_map.set_title("Páramo Iguaque–Merchán · Boyacá",
                          fontsize=11, color=UNAL, pad=6)

        _ax_photo.set_facecolor("#111827")
        for _sp in _ax_photo.spines.values():
            _sp.set_visible(False)
        _ax_photo.set_xticks([])
        _ax_photo.set_yticks([])

        _photo_cache = _pathlib.Path("/tmp/col_geo/iguaque_photo.npy")
        try:
            if _photo_cache.exists():
                _img2 = np.load(str(_photo_cache))
            else:
                _req2 = _urlreq.Request(
                    "https://upload.wikimedia.org/wikipedia/commons/c/c1/Laguna_de_Iguaque_detalle.JPG",
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                with _urlreq.urlopen(_req2, timeout=20) as _resp:
                    _img2 = _mpimg.imread(_io.BytesIO(_resp.read()), format="jpg")
                np.save(str(_photo_cache), _img2)
            _ax_photo.imshow(_img2[::4, ::4], aspect="auto")
            _ax_photo.text(0.5, 0.01,
                           "Petruss · Laguna de Iguaque detalle · Wikimedia Commons · CC BY 3.0",
                           transform=_ax_photo.transAxes, ha="center", fontsize=7,
                           color="#555", alpha=0.75, va="bottom")
        except Exception as _err:
            _ax_photo.text(0.5, 0.5, f"imagen no disponible\n{_err}",
                           ha="center", va="center", transform=_ax_photo.transAxes,
                           color="white", fontsize=8)

        _ax_photo.set_title(
            "Laguna de Iguaque y frailejones\nSantuario de Fauna y Flora · PNN Colombia",
            fontsize=11, color=UNAL, pad=6,
        )

        plt.tight_layout(pad=1.2)
        return fig

    mo.vstack([
        mo.md(r"""
    ## El manejo del Páramo Iguaque-Merchán como Problema de Crowdsourcing en 3 Algoritmos: Introducción a Algoritmos MAB (*Multi-Armed Bandit*) y sus Alternativas

    **Juan Afanador — Computación Social · C4 · UNAL**

    ### El territorio
    """),
        _territorio_fig(),
        mo.md(r"""
    El Santuario de Fauna y Flora Iguaque prohíbe la minería en su páramo delimitado
    (Resolución 1555 de 2016, MinAmbiente). Pero en las zonas rurales bajas de
    Arcabuco opera minería formal activa: el Contrato de Concesión N° 8960
    (SUMICOL/Grupo Corona, 454 ha de arcillas cerámicas, Licencia Ambiental
    Corpoboyacá Resolución 3655 de 2010) y el Título Minero N° 00141-15 (Cerámica
    Italia S.A., arcillolitas/limolitas/areniscas). El caso Cantera La Esperanza
    (vereda Rupavita) muestra la tensión directa: en la confluencia de los límites
    del Santuario, el Parque Regional El Valle y la cuenca alta del río Pómeca, la
    comunidad organizó plantones contra la reactivación de una licencia ambiental
    que — aun formalmente fuera del páramo — amenaza la conectividad ecológica y
    la regulación hídrica del santuario.
    """),
    ])
    return


@app.cell
def intro_actores_plan(mo):
    mo.md(r"""
    ### Los actores (crowdsourcing con topología, no brazos i.i.d.)

    `W0–W2` cadena paramuna comunitaria · `W3` CAR con un enfoque orientado a las ciencias ambientales ·
    `W4` agente que opera en el registro cosmológico-territorial ·
    `EC` reencuadre extractivista en registro ambiental-institucional ·
    `EM` concesión de materiales en registro jurídico-estatal.

    ### El plan de esta clase

    Tres protocolos de asignación multiagente — **UCB1** (*Upper Confidence
    Bound*), **DIG** (*Delegation Game*) y **DEC** (*Delegation Game of
    Coalitions*) —
    que iremos navegando, línea por línea, tal como el intérprete de
    Python les ejecuta. Cada uno introduce una técnica computacional
    — y, al tiempo, expone problemas en sus propios axiomas al
    aplicarse a la delimitación del páramo. Cerramos con un contraste brevecon una aproximación
    distinta que se pregunta por el diálogo y las prácticas discursivas (AAF - *Abstract Argumentation Framework*) en la formación de territorio sin bandidos ni muestreo de recompensas.

    | Bloque | ¿Qué nos enseña? | ¿Qué problematiza? |
    |:---|:---|:---|
    | UCB1 | Cota de confianza, exploración vs. explotación | El algoritmo trata la incidencia territorial de cada actor como un número exógeno y plano sin historia, sin vecinos, sin preguntar de dónde salió |
    | DIG | Cascada de delegación bilateral, posterior Beta | La delegación puede fijarse en una cadena sin nunca revisitar mejor opciones descartadas |
    | DEC | Formación de coalición (**CFORM**, *Coalition Formation*) + Myerson (DEL) | El mismo actor puede decidir dos veces en un episodio — cooperación real, pero sin memoria de ciclo |
    | **AAF** | Extensión fundamentada de Dung + σ*, la fuente de la incidencia territorial | El MAB nunca consulta esta estructura — la pregunta "¿quién debe ejecutar?" ya tenía una respuesta formal disponible, y de hecho fue la que usamos desde el principio sin que UCB1/DIG/DEC lo supieran |
    """)
    return


@app.cell
def territorio_36_setup(
    ACTOR_IDS,
    ARG_IDS,
    ATAQUES_ARG,
    G,
    GRAY,
    PARAMO,
    POS_ARR,
    TIERRA,
    UNAL,
    mo,
    mpatches,
    n,
    np,
    plt,
):

    import graph_tool.all as _gt

    _NVAR36 = 5
    _TYPE_ORDER36 = list(ARG_IDS)
    _NTYPES36 = len(_TYPE_ORDER36)
    _NTOT36 = _NTYPES36 + _NTYPES36 * _NVAR36

    _LAM_BASAL36 = {
        "A1_delimitacion": 2.5307, "A2_concesion": 2.7758, "A3_hidrologico": 6.5458,
        "A4_comunidad": 2.4962, "A5_bachue_iguaque": 34.3115, "A6_cosmo_serpiente": 29.5284,
    }

    def _nid36(ti, vi=None):
        return ti if vi is None else _NTYPES36 + ti * _NVAR36 + vi

    _rng_n36 = np.random.default_rng(42)
    _ntype36 = np.empty(_NTOT36, dtype=int)
    _nlam36 = np.empty(_NTOT36)
    for _ti, _a in enumerate(_TYPE_ORDER36):
        _ntype36[_ti] = _ti
        _nlam36[_ti] = _LAM_BASAL36[_a]
    for _ti, _a in enumerate(_TYPE_ORDER36):
        _sig36 = 0.15 * _LAM_BASAL36[_a]
        for _vi in range(_NVAR36):
            _nidx36 = _nid36(_ti, _vi)
            _ntype36[_nidx36] = _ti
            _nlam36[_nidx36] = max(0.5, float(_rng_n36.normal(_LAM_BASAL36[_a], _sig36)))

    _TYPE_IDX36 = {a: i for i, a in enumerate(_TYPE_ORDER36)}
    _ORIG36 = [(_TYPE_IDX36[_b], _TYPE_IDX36[_a]) for _b, _tgts in ATAQUES_ARG.items() for _a in _tgts]
    _SIM36 = [(_TYPE_IDX36["A3_hidrologico"], _TYPE_IDX36["A4_comunidad"]),
              (_TYPE_IDX36["A4_comunidad"], _TYPE_IDX36["A3_hidrologico"]),
              (_TYPE_IDX36["A1_delimitacion"], _TYPE_IDX36["A2_concesion"]),
              (_TYPE_IDX36["A2_concesion"], _TYPE_IDX36["A1_delimitacion"])]

    _rng_e36 = np.random.default_rng(77)
    _E36 = set()
    for _ti, _tj in _ORIG36:
        _E36.add((_nid36(_ti), _nid36(_tj)))
    for _ti in range(_NTYPES36):
        for _vi in range(_NVAR36):
            for _vj in range(_NVAR36):
                if _vi != _vj:
                    _E36.add((_nid36(_ti, _vi), _nid36(_ti, _vj)))
    for _ti in range(_NTYPES36):
        for _vi in range(_NVAR36):
            _E36.add((_nid36(_ti), _nid36(_ti, _vi)))
            _E36.add((_nid36(_ti, _vi), _nid36(_ti)))
    for _ti, _tj in _ORIG36:
        for _vi in range(_NVAR36):
            for _vj in range(_NVAR36):
                if _rng_e36.random() < 0.05:
                    _E36.add((_nid36(_ti, _vi), _nid36(_tj, _vj)))
            if _rng_e36.random() < 0.10:
                _E36.add((_nid36(_ti), _nid36(_tj, _vi)))
            if _rng_e36.random() < 0.10:
                _E36.add((_nid36(_ti, _vi), _nid36(_tj)))
    for _ti, _tj in _SIM36:
        for _vi in range(_NVAR36):
            for _vj in range(_NVAR36):
                if _rng_e36.random() < 0.03:
                    _E36.add((_nid36(_ti, _vi), _nid36(_tj, _vj)))
    _edges36 = list(_E36)

    _g36 = _gt.Graph(directed=True)
    _g36.add_vertex(_NTOT36)
    _g36.add_edge_list(_edges36)
    _gt.seed_rng(42)
    _state36 = _gt.minimize_blockmodel_dl(_g36)
    _blocks36 = np.array(_state36.get_blocks().a)
    _bmap36 = {}
    _bnext36 = 0
    _blocks36_rel = np.empty_like(_blocks36)
    for _ni in range(_NTOT36):
        _b36 = int(_blocks36[_ni])
        if _b36 not in _bmap36:
            _bmap36[_b36] = _bnext36
            _bnext36 += 1
        _blocks36_rel[_ni] = _bmap36[_b36]
    _nblocks36 = _bnext36

    _AUTOR_DE_TIPO36 = {
        "A1_delimitacion": "EC", "A2_concesion": "EM", "A3_hidrologico": "W1",
        "A4_comunidad": "W0", "A5_bachue_iguaque": "W4", "A6_cosmo_serpiente": "W4",
    }
    _hub_offset36 = {"A5_bachue_iguaque": -0.55, "A6_cosmo_serpiente": 0.55}
    _HUB_Y36 = 3.1
    _hub_xy36 = {}
    for _a in _TYPE_ORDER36:
        _actor = _AUTOR_DE_TIPO36[_a]
        _ax_ = POS_ARR[ACTOR_IDS.index(_actor), 0] + _hub_offset36.get(_a, 0.0)
        _hub_xy36[_a] = (_ax_, _HUB_Y36)

    _pos36 = np.zeros((_NTOT36, 2))
    for _ti, _a in enumerate(_TYPE_ORDER36):
        _hx, _hy = _hub_xy36[_a]
        _pos36[_nid36(_ti)] = (_hx, _hy)
        for _vi in range(_NVAR36):
            _ang = 2 * np.pi * _vi / _NVAR36
            _pos36[_nid36(_ti, _vi)] = (_hx + 0.85 * np.cos(_ang), _hy + 0.85 * np.sin(_ang))

    _BPAL36 = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b",
               "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#aec7e8"]

    _FRAMES36 = [list(range(n))]
    _actor_arg_edges36 = [(ACTOR_IDS.index(_AUTOR_DE_TIPO36[_a]), n + _ti)
                           for _ti, _a in enumerate(_TYPE_ORDER36)]
    _FRAMES36.append(list(_FRAMES36[-1]) + [n + _ti for _ti in range(_NTYPES36)])
    for _step in range(_NVAR36):
        _prev36 = list(_FRAMES36[-1])
        for _ti in range(_NTYPES36):
            _prev36.append(n + _nid36(_ti, _step))
        _FRAMES36.append(_prev36)


    def territorio_36_gif():
        import matplotlib.animation as _manim
        import tempfile as _tempfile
        import os as _os
        import base64 as _b64
        import matplotlib.patheffects as _pe36
        _blk_dom36 = {_b: int(np.bincount(_ntype36[_blocks36_rel == _b]).argmax())
                      for _b in sorted(set(_blocks36_rel.tolist()))}

        _pos_combined = np.zeros((n + _NTOT36, 2))
        _pos_combined[:n] = POS_ARR
        _pos_combined[n:] = _pos36

        _fig_g36, _ax_g36 = plt.subplots(figsize=(12, 7.5))
        _fig_g36.patch.set_facecolor("#f8f9fa")
        _fig_g36.subplots_adjust(bottom=0.12)
        _fig_g36.legend(
            handles=[mpatches.Patch(color=PARAMO, label="Actores comunitarios"),
                     mpatches.Patch(color=TIERRA, label="Actores extractivos")]
            + [mpatches.Patch(color=_BPAL36[_b % len(_BPAL36)],
                              label=f"Bloque {_TYPE_ORDER36[_blk_dom36[_b]].split('_')[0]}")
               for _b in sorted(set(_blocks36_rel.tolist()))],
            loc="lower center", ncol=6, fontsize=7.5, bbox_to_anchor=(0.5, 0.0), framealpha=0.92)

        def _draw_frame36(fi):
            _ax_g36.clear(); _ax_g36.axis("off"); _ax_g36.set_facecolor("#f8f9fa")
            _vis = set(_FRAMES36[fi])

            for _i in range(n):
                for _j in range(_i + 1, n):
                    if G[_i][_j] and _i in _vis and _j in _vis:
                        _ax_g36.plot([_pos_combined[_i, 0], _pos_combined[_j, 0]],
                                     [_pos_combined[_i, 1], _pos_combined[_j, 1]],
                                     color=GRAY, lw=1.2, alpha=0.35, zorder=1)

            for _actor_i, _hub_i in _actor_arg_edges36:
                if _actor_i in _vis and _hub_i in _vis:
                    _ax_g36.annotate("", xy=tuple(_pos_combined[_hub_i]), xytext=tuple(_pos_combined[_actor_i]),
                        arrowprops=dict(arrowstyle="-|>", color=TIERRA, lw=1.0, linestyle="dashed",
                                         alpha=0.55, shrinkA=12, shrinkB=12), zorder=2)

            for _u, _v in _edges36:
                _gu, _gv = n + _u, n + _v
                if _gu in _vis and _gv in _vis:
                    _ax_g36.plot([_pos_combined[_gu, 0], _pos_combined[_gv, 0]],
                                 [_pos_combined[_gu, 1], _pos_combined[_gv, 1]],
                                 color="#aaa", lw=0.4, alpha=0.18, zorder=1)

            for _idx in range(n):
                if _idx not in _vis:
                    continue
                _aid = ACTOR_IDS[_idx]
                _col = TIERRA if _aid in ("EC", "EM") else PARAMO
                _ax_g36.scatter([_pos_combined[_idx, 0]], [_pos_combined[_idx, 1]], s=420, c=_col,
                                alpha=0.85, zorder=3, edgecolors="white", lw=1.3)
                _ax_g36.text(_pos_combined[_idx, 0], _pos_combined[_idx, 1], _aid,
                             ha="center", va="center", fontsize=8, color="white",
                             fontweight="bold", zorder=4)

            for _ni36 in range(_NTOT36):
                _gi = n + _ni36
                if _gi not in _vis:
                    continue
                _ax_g36.scatter([_pos_combined[_gi, 0]], [_pos_combined[_gi, 1]],
                                s=(230 if _ni36 < _NTYPES36 else 85),
                                c=_BPAL36[int(_blocks36_rel[_ni36]) % len(_BPAL36)],
                                marker="D",
                                zorder=3, edgecolors="white", lw=0.8)

            for _ti36 in range(_NTYPES36):
                _gib = n + _ti36
                if _gib not in _vis:
                    continue
                _ax_g36.text(_pos_combined[_gib, 0], _pos_combined[_gib, 1] + 0.22,
                             _TYPE_ORDER36[_ti36].split("_")[0],
                             ha="center", va="center", fontsize=8.5, fontweight="bold",
                             color="#111", zorder=5,
                             path_effects=[_pe36.withStroke(linewidth=2.4, foreground="white")])

            _ax_g36.set_xlim(_pos_combined[:, 0].min() - 1.0, _pos_combined[:, 0].max() + 1.0)
            _ax_g36.set_ylim(_pos_combined[:, 1].min() - 1.0, _pos_combined[:, 1].max() + 1.0)
            _ax_g36.set_title(
                f"Fase {fi}/{len(_FRAMES36)-1} — {len(_vis)} nodos\n"
                "cuadrado = actor . diamante grande = argumento base . diamante pequeño = variante . color = mesoestructura SBM",
                color=UNAL, fontsize=10)

        _anim36 = _manim.FuncAnimation(_fig_g36, _draw_frame36, frames=len(_FRAMES36), interval=1300, repeat=True)
        with _tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as _tf36:
            _p36 = _tf36.name
        _anim36.save(_p36, writer="pillow", fps=1, dpi=88)
        plt.close(_fig_g36)
        with open(_p36, "rb") as _f36:
            _enc36 = _b64.b64encode(_f36.read()).decode()
        _os.unlink(_p36)
        return mo.Html(
            '<div style="width:75%;margin:auto">'
            f'<img src="data:image/gif;base64,{_enc36}" style="width:100%;border-radius:4px"/>'
            '</div>')


    sbm36_pos = _pos36
    sbm36_blocks = _blocks36_rel
    sbm36_nblocks = _nblocks36
    sbm36_edges = _edges36
    sbm36_ntypes = _NTYPES36
    sbm36_nvar = _NVAR36
    sbm36_palette = _BPAL36
    sbm36_type_order = _TYPE_ORDER36
    return (
        sbm36_blocks,
        sbm36_edges,
        sbm36_nblocks,
        sbm36_ntypes,
        sbm36_palette,
        sbm36_pos,
        sbm36_type_order,
        territorio_36_gif,
    )


@app.cell
def territorio_grafo_sketch(mo, territorio_36_gif):

    _grafo_accordion = mo.accordion({
        "Actores del Páramo": mo.md(r"""
    | Actor | Rol territorial | Posición en la red |
    |:---|:---|:---|
    | **W0, W1** | Familias campesinas — monitoreo directo de la vereda | Triángulo local 0–1–2 |
    | **W2** | Junta de Acción Comunal — puente organizativo local | Conecta vereda con red regional |
    | **W3** | CAR — puente organizativo regional | Conecta red regional con territorio distal |
    | **W4** | Guardián del mundo de vida paramuno y campesino | Cadena distal 3–4 |
    | **EC** | Estado colombiano — delimitación técnica | Enlazado a W0 y W1 (Art. 79) — aislado de W2–W4 |
    | **EM** | Empresa de materiales — concesión de explotación | Aislado — único canal hacia la comunidad es vía EC |
    """),
        "Los seis temas argumentativos": mo.md(r"""
    Cada bloque temático arriba tiene un único autor — el actor que lo defiende — y crece
    en la animación desde ese mismo actor:

    | Tema | Autor | De qué trata |
    |:---|:---|:---|
    | **A1 delimitación** | EC | La delimitación técnica del páramo como garantía institucional |
    | **A2 concesión** | EM | Los títulos mineros como derechos adquiridos que el Estado debe respetar |
    | **A3 hidrológico** | W1 | La regulación de acuíferos que depende del ecosistema activo |
    | **A4 comunidad** | W0 | El cuidado campesino como condición del territorio, no un extra |
    | **A5 Bachué-Iguaque** | W4 | El origen mítico del pueblo muisca en la laguna |
    | **A6 cosmológico-serpiente** | W4 | La dualidad Sué/Chía y la ley del frailejón, anterior a cualquier resolución |

    Cada tema se expande en 5 variantes — mismo reclamo, distinto registro o énfasis —
    representando la red territorial argumentativa. El color de cada nodo
    en la animación es la mesoestructura que un modelo estocástico de redes por bloques (SBM) encuentra, no el tema que le dimos:
    compare si coinciden.
    """),
        "¿Cómo crece la red?": mo.md(r"""
    La animación es la misma red de ataques (`ATAQUES_ARG`) o interacción de argumentos 
    que refleja cómo interactúan los actores del páramo. Fase 0: solo los siete actores. Fase 1: aparecen los seis
    argumentos base, conectados a su autor por una flecha punteada. Fases 2 a 6: cada
    tema suma sus cinco variantes, una por fase. Las aristas grises tenues son ataques
    entre argumentos — entre más densa la maraña de un color, más fuerte la
    mesoestructura argumentativa.

    Para el cierre: **el número que UCB1, DIG y DEC usan desde la
    primera diapositiva sale de esta misma red** — no de un dato ad-hoc.
    """),
    })

    mo.vstack([_grafo_accordion, territorio_36_gif()])
    return


@app.cell
def desempeno_sigma_setup(ARG_IDS, ATAQUES_ARG, np):

    _LAM_SIGMA = {"A1_delimitacion": 2.5307, "A2_concesion": 2.7758, "A3_hidrologico": 6.5458,
                  "A4_comunidad": 2.4962, "A5_bachue_iguaque": 34.3115, "A6_cosmo_serpiente": 29.5284}
    _W0_SIGMA = {a: max(0.1, 1.0 - _LAM_SIGMA[a] / 100.0) for a in ARG_IDS}

    # EC (Estado colombiano) es la autoridad legal que delimito el paramo mediante la
    # Resolucion 1555 de 2016 del Ministerio de Ambiente (ver EOT_iguaque.txt, linea 1) --
    # A1 no es un argumento mas entre seis, es el acto administrativo real de delimitacion.
    # Su peso base se ajusta para reflejar esa autoridad institucional, que la fluidez
    # textual (BETO) por si sola no puede medir.
    _EC_AUTORIDAD_LEGAL_MULT = 1.5  # Resolucion 1555/2016, Ministerio de Ambiente
    _W0_SIGMA["A1_delimitacion"] *= _EC_AUTORIDAD_LEGAL_MULT

    _NEW_EDGES_SIGMA_WEIGHT = {("A2_concesion", "A3_hidrologico"): 0.5, ("A2_concesion", "A6_cosmo_serpiente"): 0.5}

    _attackers_sigma = {a: [] for a in ARG_IDS}
    for _b, _tgts in ATAQUES_ARG.items():
        for _a in _tgts:
            _wt = _NEW_EDGES_SIGMA_WEIGHT.get((_b, _a), 1.0)
            _attackers_sigma[_a].append((_b, _wt))

    _sigma_star = dict(_W0_SIGMA)
    for _ in range(400):
        _nxt_sigma = {}
        for _a in ARG_IDS:
            _den = _W0_SIGMA[_a] + sum(_wt * _sigma_star[_b] for _b, _wt in _attackers_sigma[_a])
            _nxt_sigma[_a] = _W0_SIGMA[_a] / _den if _den > 0 else _W0_SIGMA[_a]
        if max(abs(_nxt_sigma[_k] - _sigma_star[_k]) for _k in _nxt_sigma) < 1e-7:
            _sigma_star = _nxt_sigma
            break
        _sigma_star = _nxt_sigma

    _AUTORIA_TIPO_SIGMA = {
        "EC": ["A1_delimitacion"], "EM": ["A2_concesion"], "W1": ["A3_hidrologico"],
        "W0": ["A4_comunidad"], "W4": ["A5_bachue_iguaque", "A6_cosmo_serpiente"],
    }

    _cal_betas_w2w3 = [
        (8.0, 3.0), (4.0, 7.0), (8.0, 2.5), (10.0, 3.0),
        (2.0, 6.0), (12.0, 2.0), (7.0, 2.5),
    ]
    _rng_w2w3 = np.random.default_rng(42)
    _baseline_beta = np.array([_rng_w2w3.beta(_a, _b) for _a, _b in _cal_betas_w2w3])

    _ACTOR_IDS_ORDER = ["W0", "W1", "W2", "W3", "W4", "EC", "EM"]
    cal_original = _baseline_beta.copy()
    desempeno = _baseline_beta.copy()
    for _actor, _args in _AUTORIA_TIPO_SIGMA.items():
        _idx = _ACTOR_IDS_ORDER.index(_actor)
        desempeno[_idx] = float(np.mean([_sigma_star[_a] for _a in _args]))
    # W2, W3: sin argumento propio (actores puente) -> conservan la linea base original
    return cal_original, desempeno


@app.cell
def graph_data(np):

    UNAL   = "#00427C"
    PARAMO = "#225522"
    TIERRA = "#8B5A2B"
    GRAY   = "#888888"
    BSTATE = "#9B2335"
    GOLD   = "#D4880A"

    ACTOR_IDS = ["W0", "W1", "W2", "W3", "W4", "EC", "EM"]
    n = 7
    G = np.zeros((n, n), dtype=bool)
    for _i, _j in [(0, 1), (1, 2), (0, 2)]:
        G[_i, _j] = G[_j, _i] = True
    G[2, 3] = G[3, 2] = True
    G[3, 4] = G[4, 3] = True
    G[5, 6] = G[6, 5] = True
    G[5, 0] = G[0, 5] = True
    G[5, 1] = G[1, 5] = True

    POS = {
        "W1": np.array([-1.5, 0.0]),
        "W0": np.array([-0.5, 0.0]),
        "W2": np.array([0.5, 0.0]),
        "W3": np.array([1.5, 0.0]),
        "W4": np.array([3.0, 0.0]),
        "EC": np.array([1.0, -1.3]),
        "EM": np.array([2.5, -1.3]),
    }
    _SPACING = 1.9
    POS_ARR = np.array([POS[a] for a in ACTOR_IDS]) * _SPACING

    _pairwise = np.linalg.norm(POS_ARR[:, None, :] - POS_ARR[None, :, :], axis=-1)
    np.fill_diagonal(_pairwise, np.inf)
    MIN_DIST = _pairwise.min()
    R_MAX = 0.40 * MIN_DIST
    R_MIN = 0.10 * MIN_DIST
    return (
        ACTOR_IDS,
        BSTATE,
        G,
        GOLD,
        GRAY,
        PARAMO,
        POS_ARR,
        R_MAX,
        R_MIN,
        TIERRA,
        UNAL,
        n,
    )


@app.cell
def ucb1_pure_setup(desempeno, n, np, sys):

    _UCB1_ROUND_SRC = """def _ucb1_round_pure(t, n_i, suma_i, medias, rng):
        mu = suma_i / n_i
        cota = np.sqrt(2.0 * np.log(t + 1) / n_i)
        i = int(np.argmax(mu + cota))
        r = int(rng.binomial(1, medias[i]))
        n_i[i] += 1
        suma_i[i] += r
        return i, r
    """
    UCB1_PURE_LINES = _UCB1_ROUND_SRC.rstrip(chr(10)).split(chr(10))

    _ucb1_pure_ns = {"np": np}
    exec(compile(_UCB1_ROUND_SRC, "<ucb1_round_pure>", "exec"), _ucb1_pure_ns)
    _ucb1_round_pure = _ucb1_pure_ns["_ucb1_round_pure"]

    _UCB1_KEEP_VARS = ["mu", "cota", "i", "r"]

    def _ucb1_snap_locals(loc):
        out = {}
        for k in _UCB1_KEEP_VARS:
            if k in loc:
                v = loc[k]
                out[k] = np.array(v) if isinstance(v, np.ndarray) else v
        return out

    def ucb1_trace_one_round(seed, target_t, T=1000, K=300.0):
        rng = np.random.default_rng(seed)
        n_arms = n
        n_i = np.zeros(n_arms, dtype=int)
        suma_i = np.zeros(n_arms)
        consumo = 0.0
        round_code_obj = _ucb1_round_pure.__code__

        def make_global_tracer(tl):
            def local_tracer(frame, event, arg):
                if frame.f_code is not round_code_obj:
                    return local_tracer
                if event == "line":
                    tl.append(dict(lineno=frame.f_lineno, locals=_ucb1_snap_locals(frame.f_locals), event="line"))
                elif event == "return":
                    tl.append(dict(lineno=frame.f_lineno, locals=_ucb1_snap_locals(frame.f_locals), event="return", returned=arg))
                return local_tracer
            def global_tracer(frame, event, arg):
                if event == "call" and frame.f_code is round_code_obj:
                    return local_tracer
                return None
            return global_tracer

        t = 0
        while t < n_arms and t < T and consumo < K:
            i = t
            r = int(rng.binomial(1, desempeno[i]))
            n_i[i] += 1; suma_i[i] += r
            a = 1.0 + suma_i[i]; b = 1.0 + (n_i[i] - suma_i[i])
            consumo += 1.0 / (a + b)
            t += 1

        while t < T and consumo < K:
            if t == target_t:
                trace_list = []
                sys.settrace(make_global_tracer(trace_list))
                try:
                    i, r = _ucb1_round_pure(t, n_i, suma_i, desempeno, rng)
                finally:
                    sys.settrace(None)
                collapsed = []
                for entry in trace_list:
                    if (collapsed and collapsed[-1]["lineno"] == entry["lineno"] and entry["event"] == "line"):
                        collapsed[-1] = entry
                    else:
                        collapsed.append(entry)
                a = 1.0 + suma_i[i]; b = 1.0 + (n_i[i] - suma_i[i])
                consumo += 1.0 / (a + b)
                return dict(trace=collapsed, t=t, i=i, r=r, n_i_before=n_i.copy(), suma_i_before=suma_i.copy())
            i, r = _ucb1_round_pure(t, n_i, suma_i, desempeno, rng)
            a = 1.0 + suma_i[i]; b = 1.0 + (n_i[i] - suma_i[i])
            consumo += 1.0 / (a + b)
            t += 1
        return None

    ucb1_round_pure_fn = _ucb1_round_pure
    return UCB1_PURE_LINES, ucb1_round_pure_fn, ucb1_trace_one_round


@app.cell
def ucb1_round_dropdown_cell(mo):

    UCB1_ROOT_SEED = 257
    UCB1_CURATED = {
        "primera ronda real, tras calentamiento (t=7)": 7,
        "ronda intermedia, aun explorando (t=100)": 100,
        "ronda tardia, asentada en W1 (t=995)": 995,
    }
    ucb1_round_dropdown = mo.ui.dropdown(
        options=UCB1_CURATED, value="ronda intermedia, aun explorando (t=100)",
        label="ronda UCB1 (curada)")
    return UCB1_ROOT_SEED, ucb1_round_dropdown


@app.cell
def ucb1_trace_state_cell(
    UCB1_ROOT_SEED,
    mo,
    ucb1_round_dropdown,
    ucb1_trace_one_round,
):

    ucb1_step_trace = ucb1_trace_one_round(UCB1_ROOT_SEED, ucb1_round_dropdown.value)
    get_ucb1_step, set_ucb1_step = mo.state(0)
    return get_ucb1_step, set_ucb1_step, ucb1_step_trace


@app.cell
def ucb1_step_buttons_cell(
    UCB1_PURE_LINES,
    get_ucb1_step,
    mo,
    set_ucb1_step,
    ucb1_step_trace,
):

    _ucb1_trace_ref = ucb1_step_trace["trace"]
    _ucb1_max_idx = len(_ucb1_trace_ref) - 1

    def _ucb1_jump_to_line(idx, target_lineno):
        for k in range(idx + 1, len(_ucb1_trace_ref)):
            if _ucb1_trace_ref[k]["lineno"] == target_lineno:
                return k
        for k in range(0, idx + 1):
            if _ucb1_trace_ref[k]["lineno"] == target_lineno:
                return k
        return idx

    ucb1_btn_prev = mo.ui.button(label="◀",
        on_click=lambda _: set_ucb1_step(max(0, get_ucb1_step() - 1)))
    ucb1_btn_next = mo.ui.button(label="▶",
        on_click=lambda _: set_ucb1_step(min(_ucb1_max_idx, get_ucb1_step() + 1)))

    _ucb1_line_options = {f"{_i+1}: {_txt.strip()}": _i + 1 for _i, _txt in enumerate(UCB1_PURE_LINES)}
    ucb1_line_target = mo.ui.dropdown(options=_ucb1_line_options,
        value=f"1: {UCB1_PURE_LINES[0].strip()}", label=None)
    ucb1_btn_jump = mo.ui.button(label="ir",
        on_click=lambda _: set_ucb1_step(_ucb1_jump_to_line(get_ucb1_step(), ucb1_line_target.value)))
    return ucb1_btn_jump, ucb1_btn_next, ucb1_btn_prev, ucb1_line_target


@app.cell
def ucb1_round_display(
    ACTOR_IDS,
    BSTATE,
    G,
    GOLD,
    GRAY,
    PARAMO,
    POS_ARR,
    R_MAX,
    R_MIN,
    TIERRA,
    UCB1_PURE_LINES,
    UNAL,
    get_ucb1_step,
    mo,
    mpatches,
    n,
    np,
    plt,
    ucb1_btn_jump,
    ucb1_btn_next,
    ucb1_btn_prev,
    ucb1_line_target,
    ucb1_round_dropdown,
    ucb1_step_trace,
):

    _uidx = get_ucb1_step()
    _utrace = ucb1_step_trace["trace"]
    _uentry = _utrace[_uidx]
    _uloc = _uentry["locals"]
    _ulineno = _uentry["lineno"]
    _ut = ucb1_step_trace["t"]
    _uis_return = (_uentry.get("event") == "return")
    _uvisited_linenos = {_utrace[k]["lineno"] for k in range(_uidx + 1)}

    _umu = _uloc.get("mu")
    _ucota = _uloc.get("cota")
    _ui_chosen = _uloc.get("i")
    _ur_reward = _uloc.get("r")
    _uscale_max = 5.0

    _fig, (_uaxL, _uaxR) = plt.subplots(1, 2, figsize=(16, 8.2), gridspec_kw={"width_ratios": [1.0, 1.3]})
    _fig.patch.set_facecolor("#f8f9fa")

    _uaxL.axis("off"); _uaxL.set_xlim(0, 1); _uaxL.set_ylim(0, 1)
    _uaxL.set_title(f"_ucb1_round_pure(t = {_ut})  --  paso {_uidx+1}/{len(_utrace)}",
                    fontsize=12.5, color=UNAL, fontweight="bold", loc="left")

    _y0, _dy = 0.90, 0.09
    for _k, _line in enumerate(UCB1_PURE_LINES):
        _this_lineno = _k + 1
        _y = _y0 - _k * _dy
        if _this_lineno == _ulineno:
            _uaxL.add_patch(mpatches.FancyBboxPatch((0.0, _y - 0.038), 1.0, 0.076,
                boxstyle="round,pad=0.003,rounding_size=0.008", linewidth=0,
                facecolor=GOLD, alpha=0.35, transform=_uaxL.transAxes))
            _color, _weight = "#111", "bold"
        elif _this_lineno in _uvisited_linenos:
            _color, _weight = "#333", "normal"
        else:
            _color, _weight = "#bbb", "normal"
        _uaxL.text(0.02, _y, _line, fontsize=10.5, family="monospace", va="center",
                  color=_color, fontweight=_weight, transform=_uaxL.transAxes)

    _y_vals = _y0 - len(UCB1_PURE_LINES) * _dy - 0.05
    _uaxL.text(0.02, _y_vals, "variables locales en este punto:", fontsize=10, color=UNAL,
              fontweight="bold", transform=_uaxL.transAxes)
    _uloc_parts = []
    if _umu is not None:
        _uloc_parts.append("mu=[" + ", ".join(f"{_v:.2f}" for _v in _umu) + "]")
    if _ucota is not None:
        _uloc_parts.append("cota=[" + ", ".join(f"{_v:.2f}" for _v in _ucota) + "]")
    if _ui_chosen is not None:
        _uloc_parts.append(f"i={ACTOR_IDS[_ui_chosen]}")
    if _ur_reward is not None:
        _uloc_parts.append(f"r={_ur_reward}")
    _uaxL.text(0.02, _y_vals - 0.06, "\n".join(_uloc_parts) if _uloc_parts else "(ninguna aun)",
              fontsize=9, family="monospace", color="#444", transform=_uaxL.transAxes, va="top")

    if _uis_return:
        _i_ret, _r_ret = _uentry["returned"]
        _txt = f"RETORNA (i={ACTOR_IDS[_i_ret]}, r={_r_ret})"
        _uaxL.add_patch(mpatches.FancyBboxPatch((0.0, _y_vals - 0.18), 1.0, 0.06,
            boxstyle="round,pad=0.005,rounding_size=0.01", linewidth=0,
            facecolor=(PARAMO if _r_ret == 1 else BSTATE), alpha=0.3, transform=_uaxL.transAxes))
        _uaxL.text(0.02, _y_vals - 0.15, _txt, fontsize=10, family="monospace", va="center",
                  color="#111", fontweight="bold", transform=_uaxL.transAxes)

    _uaxR.set_facecolor("#f8f9fa")
    for _i in range(n):
        for _j in range(_i + 1, n):
            if G[_i, _j]:
                _uaxR.plot([POS_ARR[_i, 0], POS_ARR[_j, 0]], [POS_ARR[_i, 1], POS_ARR[_j, 1]],
                          color=GRAY, lw=1.0, alpha=0.15, zorder=1, linestyle="dashed")

    for _idx, _aid in enumerate(ACTOR_IDS):
        _x, _y = POS_ARR[_idx]
        _mu_v = float(_umu[_idx]) if _umu is not None else 0.0
        _cota_v = float(_ucota[_idx]) if _ucota is not None else 0.0
        _r_outer = R_MIN + np.sqrt(max(_mu_v + _cota_v, 0.0) / _uscale_max) * (R_MAX - R_MIN)
        _r_inner = (R_MIN + np.sqrt(max(_mu_v, 0.0) / _uscale_max) * (R_MAX - R_MIN)) * 0.92 if _umu is not None else 0.0
        if _umu is not None:
            _uaxR.add_patch(plt.Circle((_x, _y), _r_outer, facecolor=GOLD, alpha=0.35, edgecolor="none", zorder=2))
            _uaxR.add_patch(plt.Circle((_x, _y), _r_inner, facecolor=PARAMO, alpha=0.75, edgecolor="white", lw=1.2, zorder=3))
        else:
            _uaxR.add_patch(plt.Circle((_x, _y), R_MIN, facecolor="#cccccc", edgecolor="white", lw=1.2, zorder=3))
        if _ui_chosen == _idx:
            _uaxR.add_patch(plt.Circle((_x, _y), max(_r_outer, R_MIN) + 0.09, facecolor="none", edgecolor=BSTATE, lw=2.4, zorder=5))
            if _ur_reward is not None:
                _uaxR.add_patch(plt.Circle((_x, _y), max(_r_outer, R_MIN) + 0.16, facecolor="none",
                                            edgecolor=(PARAMO if _ur_reward == 1 else TIERRA), lw=2.0, linestyle="dashed", zorder=5))
        _lbl = [_aid]
        if _umu is not None:
            _lbl.append(f"mu={_mu_v:.2f}")
        if _ucota is not None:
            _lbl.append(f"cota={_cota_v:.2f}")
        _uaxR.text(_x, _y - R_MAX - 0.32, "\n".join(_lbl), ha="center", va="top", fontsize=7.8, color="#222", zorder=6)

    _uaxR.set_xlim(POS_ARR[:, 0].min() - 1.2, POS_ARR[:, 0].max() + 1.2)
    _uaxR.set_ylim(POS_ARR[:, 1].min() - 2.4, POS_ARR[:, 1].max() + 1.7)
    _uaxR.set_aspect("equal"); _uaxR.axis("off")
    _uaxR.set_title(f"ronda t={_ut}  -  UCB1 nunca lee las aristas grises (topologia G)",
                   fontsize=10.5, color=UNAL)
    _uaxR.text((POS_ARR[:, 0].min() + POS_ARR[:, 0].max()) / 2, POS_ARR[:, 1].min() - 2.0,
              "verde=mu (media empirica) . dorado=cota de confianza . aro rojo=argmax elegido . aro punteado=recompensa (verde=exito, cafe=fallo)",
              ha="center", va="top", fontsize=7.6, color="#555")

    plt.tight_layout()
    _ucb1_accordion = mo.accordion({
        "🔍 UCB1 — flujo completo (referencia, no interactivo)": mo.md(r"""
    **Entrada:** `medias = desempeno` (incidencia territorial real por actor, derivada de σ* — ver gesto de cierre), `T=1000` (horizonte), `K=300` (presupuesto)

    ```
    PASO 1 — Calentamiento (t = 0..n-1, antes del seguimiento)
      para j = 0, 1, ..., n-1:
        jugar el brazo j una vez                  # garantiza n_i[j] >= 1, evita division por 0

    PASO 2 — Ronda real (t = n..T-1)              # esto es exactamente lo que el seguimiento ejecuta
      mu    = suma_i / n_i                        # media empirica por actor    -> _ucb1_round_pure L.2
      cota  = sqrt(2 ln(t+1) / n_i)                # indice de confianza UCB     -> _ucb1_round_pure L.3
      i     = argmax(mu + cota)                    # brazo elegido                -> _ucb1_round_pure L.4
      r     ~ Bernoulli(medias[i])                 # resultado real observado    -> _ucb1_round_pure L.5
      n_i[i]    += 1                                # actualizar conteo            -> _ucb1_round_pure L.6
      suma_i[i] += r                                # actualizar acumulado         -> _ucb1_round_pure L.7
      retorna (i, r)                                                              -> _ucb1_round_pure L.8
    ```

    **Por que `cota` funciona:** cuando `n_i` crece, `sqrt(2 ln t / n_i) -> 0` (explota al mejor
    conocido). Cuando `n_i` es bajo, la cota domina (fuerza exploracion). El balance garantiza
    arrepentimiento **O(log T)** (Auer et al. 2002).

    **Lo que NO aparece en este pseudocodigo:** ninguna referencia a `G` (la red de actores).
    Compara con el seguimiento de arriba — la mitad derecha dibuja las aristas de `G` en gris
    punteado precisamente para hacer visible esa ausencia.
    """)
    })

    mo.vstack([
        ucb1_round_dropdown,
        mo.hstack([
            mo.vstack([mo.md("**paso**"), mo.hstack([ucb1_btn_prev, ucb1_btn_next], gap=1)]),
            mo.vstack([mo.md("**ir a linea**"), mo.hstack([ucb1_line_target, ucb1_btn_jump], gap=1)]),
        ], justify="start", gap=3, wrap=True),
        _fig,
        _ucb1_accordion,
    ])
    return


@app.cell
def ucb1_full_run_cell(desempeno, n, np, ucb1_round_pure_fn):

    def _ucb1_full_run(seed, T=1000, K=300.0):
        rng = np.random.default_rng(seed)
        n_arms = n
        n_i = np.zeros(n_arms, dtype=int)
        suma_i = np.zeros(n_arms)
        consumo = 0.0
        hist_i = np.zeros(T, dtype=int)
        hist_r = np.zeros(T)
        t = 0
        while t < n_arms and t < T and consumo < K:
            i = t
            r = int(rng.binomial(1, desempeno[i]))
            n_i[i] += 1; suma_i[i] += r
            a = 1.0 + suma_i[i]; b = 1.0 + (n_i[i] - suma_i[i])
            consumo += 1.0 / (a + b)
            hist_i[t] = i; hist_r[t] = r
            t += 1
        while t < T and consumo < K:
            i, r = ucb1_round_pure_fn(t, n_i, suma_i, desempeno, rng)
            a = 1.0 + suma_i[i]; b = 1.0 + (n_i[i] - suma_i[i])
            consumo += 1.0 / (a + b)
            hist_i[t] = i; hist_r[t] = r
            t += 1
        return dict(n_i=n_i, t_real=t, hist_i=hist_i[:t], hist_r=hist_r[:t])

    UCB1_SEED_CMP = 0
    ucb1_full_result = _ucb1_full_run(UCB1_SEED_CMP)
    return (ucb1_full_result,)


@app.cell
def ucb1_problematisacion(ACTOR_IDS, mo, np, ucb1_full_result):

    _ucb1_ni_final = ucb1_full_result["n_i"]
    _ucb1_min_i = int(np.argmin(_ucb1_ni_final))
    _ucb1_max_i = int(np.argmax(_ucb1_ni_final))

    mo.md(f"""
    **Lo que UCB1 nos enseña:** la cota de confianza `μ̂ᵢ + √(2 ln t / nᵢ)` resuelve el
    dilema exploración/explotación con una garantía formal — regret `O(log T)` —
    sin necesitar ningún supuesto sobre la estructura de los actores.

    **Lo que UCB1 problematiza, sin quererlo:** el algoritmo trata a cada actor
    como un brazo i.i.d. `desempeno_i` ya no es un número arbitrario — viene de
    σ*, la supervivencia de cada argumento bajo ataque interactuando en un marco dialógico — pero UCB1 no lo sabe ni le importa: lo usa exactamente igual
    a como usaría un dato numérico ad-hoc aproximado, sin relación con quién ataca el argumento
    de quién ni con la posición de cada actor en la red (que UCB1 nunca lee
    — las aristas grises del seguimiento de arriba nunca entran en `mu` ni en
    `cota`). Después de {ucb1_full_result['t_real']} episodios en esta corrida:
    **{ACTOR_IDS[_ucb1_max_i]}** acumula {int(_ucb1_ni_final[_ucb1_max_i])} activaciones,
    **{ACTOR_IDS[_ucb1_min_i]}** solo {int(_ucb1_ni_final[_ucb1_min_i])} — y noten
    quién se desempeña peor: EC, el reencuadre extractivista de la delimitación técnica,
    es ahora el que menos incidencia territorial logra sostener. UCB1 no "sabe" que está castigando a EC por perder el
    debate — simplemente ve un número bajo y lo trata como cualquier otro.
    Preguntar "¿cómo se concibe el `desempeño`?" es justamente lo que
    UCB1, por diseño, nunca puede preguntarse — esa pregunta ya tenía respuesta
    antes de que empezara esta clase, y la revelamos al cierre.
    """)
    return


@app.cell
def dig_trace_full(G, desempeno, n, np):
    def _dig_decide_logged(i, visitados, alpha, beta_, delta, rng):
        candidatos = [j for j in range(n) if G[i][j] and j not in visitados]
        if not candidatos:
            return dict(actual=i, candidatos=[], theta={}, estrategias={},
                         accion="execute", elegido_m=None, m_argmax=None)
        theta = {k: rng.beta(alpha[k], beta_[k]) for k in range(n)}
        estrategias = {}
        for j in candidatos:
            ad_j = [k for k in range(n) if G[j][k] and k != i and k not in visitados]
            mu_j = alpha[j] / (alpha[j] + beta_[j])
            r_i0 = theta[j]
            r_i1 = max((theta[k] for k in ad_j), default=r_i0)
            r_ij = (r_i0 + r_i1) / 2.0
            denom = r_ij - mu_j
            x_ij = 0.0 if abs(denom) < 1e-12 else max(0.0, min(1.0, (r_i1 - r_i0) / denom))
            estrategias[j] = dict(x_ij=x_ij, r_ij=r_ij, mu_j=mu_j, r_i0=r_i0, r_i1=r_i1, ad_j=ad_j)
        m = max(estrategias, key=lambda j: estrategias[j]["r_ij"])
        x_im = estrategias[m]["x_ij"]
        accion = "delegate" if (1.0 - delta) < x_im else "execute"
        return dict(actual=i, candidatos=candidatos, theta=theta, estrategias=estrategias,
                     accion=accion, elegido_m=m if accion == "delegate" else None, m_argmax=m)

    def _dig_cascade_logged(root, alpha, beta_, delta, rng, max_len=7):
        cadena = [root]
        steps = []
        actual = root
        while True:
            step = _dig_decide_logged(actual, set(cadena), alpha, beta_, delta, rng)
            steps.append(step)
            if step["accion"] == "execute" or step["elegido_m"] is None or len(cadena) >= max_len:
                return cadena, steps
            cadena.append(step["elegido_m"]); actual = step["elegido_m"]

    def _dig_full_trace(root, delta, seed, T, K):
        rng = np.random.default_rng(seed)
        alpha_d = {i: 1.0 for i in range(n)}
        beta_d = {i: 1.0 for i in range(n)}
        consumo = 0.0
        episodes = []
        for t in range(T):
            if consumo >= K:
                break
            alpha_before = dict(alpha_d); beta_before = dict(beta_d)
            cadena, steps = _dig_cascade_logged(root, alpha_d, beta_d, delta, rng)
            ejecutor = cadena[-1]
            resultado = int(rng.binomial(1, desempeno[ejecutor]))
            for ag in cadena:
                if resultado > 0: alpha_d[ag] += 1
                else: beta_d[ag] += 1
            consumo += sum(1.0 / (alpha_d[ag] + beta_d[ag]) for ag in cadena)  # per-hop cost, not just executor
            episodes.append(dict(t=t, cadena=cadena, steps=steps, ejecutor=ejecutor,
                                  resultado=resultado, consumo=consumo,
                                  alpha_before=alpha_before, beta_before=beta_before))
        return episodes

    DIG_ROOT = 1  # W1 -- favorable root, unified between the debugger and the comparison
    DIG_DELTA = 0.10
    DIG_SEED = 0
    DIG_ROOT_CMP = DIG_ROOT  # alias, kept so comparison_display's existing references still work
    DIG_SEED_CMP = DIG_SEED
    dig_episodes = _dig_full_trace(DIG_ROOT, DIG_DELTA, seed=DIG_SEED, T=1000, K=300.0)
    DIG_T_REAL = len(dig_episodes)
    return (
        DIG_DELTA,
        DIG_ROOT,
        DIG_ROOT_CMP,
        DIG_SEED,
        DIG_SEED_CMP,
        dig_episodes,
    )


@app.cell
def dig_pure_setup(G, desempeno, n, np):
    import sys

    _DIG_PURE_SRC = """def _dig_decide_pure(i, visitados, alpha, beta_, delta, rng):
        candidatos = [j for j in range(n) if G[i][j] and j not in visitados]
        if not candidatos:
            return ("execute", None)
        theta = {k: rng.beta(alpha[k], beta_[k]) for k in range(n)}
        estrategias = {}
        for j in candidatos:
            ad_j = [k for k in range(n) if G[j][k] and k != i and k not in visitados]
            mu_j  = alpha[j] / (alpha[j] + beta_[j])
            r_i0  = theta[j]
            r_i1  = max((theta[k] for k in ad_j), default=r_i0)
            r_ij  = (r_i0 + r_i1) / 2.0
            denom = r_ij - mu_j
            x_ij  = 0.0 if abs(denom) < 1e-12 else max(0.0, min(1.0, (r_i1 - r_i0) / denom))
            estrategias[j] = (x_ij, r_ij)
        m = max(estrategias, key=lambda j: estrategias[j][1])
        x_im, _ = estrategias[m]
        if (1.0 - delta) < x_im:
            return ("delegate", m)
        return ("execute", None)
    """
    DIG_PURE_LINES = _DIG_PURE_SRC.rstrip(chr(10)).split(chr(10))
    _dig_pure_ns = {"n": n, "G": G}
    exec(compile(_DIG_PURE_SRC, "<dig_pure>", "exec"), _dig_pure_ns)
    _dig_decide_pure = _dig_pure_ns["_dig_decide_pure"]

    _DIG_KEEP_VARS = ["candidatos", "theta", "estrategias", "j", "ad_j", "mu_j",
                      "r_i0", "r_i1", "r_ij", "denom", "x_ij", "m", "x_im"]

    def _dig_snap_locals(loc):
        out = {}
        for k in _DIG_KEEP_VARS:
            if k in loc:
                v = loc[k]
                out[k] = dict(v) if isinstance(v, dict) else (list(v) if isinstance(v, list) else v)
        return out

    def dig_trace_one_decision(root, delta, seed, target_t, target_hop, K=300.0, T=1000):
        rng = np.random.default_rng(seed)
        alpha_d = {i: 1.0 for i in range(n)}
        beta_d = {i: 1.0 for i in range(n)}
        consumo = 0.0
        dig_code_obj = _dig_decide_pure.__code__

        def make_local_tracer(tl):
            def local_tracer(frame, event, arg):
                if event == "line":
                    tl.append(dict(lineno=frame.f_lineno, locals=_dig_snap_locals(frame.f_locals), event="line"))
                elif event == "return":
                    tl.append(dict(lineno=frame.f_lineno, locals=_dig_snap_locals(frame.f_locals),
                                    event="return", returned=arg))
                return local_tracer
            return local_tracer

        def make_global_tracer(tl):
            lt = make_local_tracer(tl)
            def global_tracer(frame, event, arg):
                if event == "call" and frame.f_code is dig_code_obj:
                    return lt
                return None
            return global_tracer

        for t in range(min(target_t + 1, T)):
            if consumo >= K:
                break
            cadena = [root]
            actual = root
            hop = 0
            while True:
                visitados = set(cadena)
                if t == target_t and hop == target_hop:
                    trace_list = []
                    sys.settrace(make_global_tracer(trace_list))
                    try:
                        result = _dig_decide_pure(actual, visitados, alpha_d, beta_d, delta, rng)
                    finally:
                        sys.settrace(None)
                    collapsed = []
                    for entry in trace_list:
                        if collapsed and collapsed[-1]["lineno"] == entry["lineno"] and entry["event"] == "line":
                            collapsed[-1] = entry
                        else:
                            collapsed.append(entry)
                    return dict(trace=collapsed, i=actual, visitados=set(visitados),
                                result=result, cadena_so_far=list(cadena))
                accion, m = _dig_decide_pure(actual, visitados, alpha_d, beta_d, delta, rng)
                if accion == "execute" or m is None or len(cadena) >= 7:
                    break
                cadena.append(m); actual = m; hop += 1
            ejecutor = cadena[-1]
            resultado = int(rng.binomial(1, desempeno[ejecutor]))
            for ag in cadena:
                if resultado > 0: alpha_d[ag] += 1
                else: beta_d[ag] += 1
            consumo += 1.0 / (alpha_d[ejecutor] + beta_d[ejecutor])
        return None

    return DIG_PURE_LINES, dig_trace_one_decision, sys


@app.cell
def episode_dropdown_cell(mo):

    DIG_CURATED = {
        "ejecución inmediata (W1, 1 nodo)": 0,
        "fallo temprano (W1-W0, 2 nodos)": 8,
        "cascada corta con éxito (W1-W0-W2)": 20,
        "cascada más larga (5 nodos, nunca llega a W4)": 181,
    }
    episode_dropdown = mo.ui.dropdown(
        options=DIG_CURATED, value="cascada corta con éxito (W1-W0-W2)",
        label="episodio DIG (curado)")
    return (episode_dropdown,)


@app.cell
def hop_radio_cell(ACTOR_IDS, dig_episodes, episode_dropdown, mo):
    _ep_preview = dig_episodes[episode_dropdown.value]
    _hop_options = {
        f"Paso {k+1}: {ACTOR_IDS[step['actual']]} decide" + (" (último)" if k == len(_ep_preview['steps']) - 1 else ""): k
        for k, step in enumerate(_ep_preview["steps"])
    }
    hop_radio = mo.ui.radio(options=_hop_options, value=list(_hop_options.keys())[0],
                             label="paso (nodo que decide)")
    return (hop_radio,)


@app.cell
def dig_trace_state_cell(
    DIG_DELTA,
    DIG_ROOT,
    DIG_SEED,
    dig_trace_one_decision,
    episode_dropdown,
    hop_radio,
    mo,
):
    dig_step_trace = dig_trace_one_decision(DIG_ROOT, DIG_DELTA, DIG_SEED, episode_dropdown.value, hop_radio.value)
    get_dig_step, set_dig_step = mo.state(0)
    return dig_step_trace, get_dig_step, set_dig_step


@app.cell
def dig_step_buttons_cell(
    DIG_PURE_LINES,
    dig_step_trace,
    get_dig_step,
    mo,
    set_dig_step,
):
    _dig_trace_ref = dig_step_trace["trace"]
    _dig_max_idx = len(_dig_trace_ref) - 1

    def _dig_effective_j(entry):
        loc = entry["locals"]
        return loc.get("j") if "candidatos" in loc else None

    def _dig_next_candidate(idx):
        cur_j = _dig_effective_j(_dig_trace_ref[idx])
        for k in range(idx + 1, len(_dig_trace_ref)):
            if _dig_effective_j(_dig_trace_ref[k]) != cur_j:
                return k
        return _dig_max_idx

    def _dig_prev_candidate(idx):
        cur_j = _dig_effective_j(_dig_trace_ref[idx])
        for k in range(idx - 1, -1, -1):
            if _dig_effective_j(_dig_trace_ref[k]) != cur_j:
                return k
        return 0

    def _dig_jump_to_line(idx, target_lineno):
        for k in range(idx + 1, len(_dig_trace_ref)):
            if _dig_trace_ref[k]["lineno"] == target_lineno:
                return k
        for k in range(0, idx + 1):
            if _dig_trace_ref[k]["lineno"] == target_lineno:
                return k
        return idx

    dig_btn_prev = mo.ui.button(label="◀",
        on_click=lambda _: set_dig_step(max(0, get_dig_step() - 1)))
    dig_btn_next = mo.ui.button(label="▶",
        on_click=lambda _: set_dig_step(min(_dig_max_idx, get_dig_step() + 1)))
    dig_btn_prev_cand = mo.ui.button(label="◀◀",
        on_click=lambda _: set_dig_step(_dig_prev_candidate(get_dig_step())))
    dig_btn_next_cand = mo.ui.button(label="▶▶",
        on_click=lambda _: set_dig_step(_dig_next_candidate(get_dig_step())))

    _dig_line_options = {f"{_i+1}: {_txt.strip()}": _i + 1 for _i, _txt in enumerate(DIG_PURE_LINES)}
    dig_line_target = mo.ui.dropdown(options=_dig_line_options,
        value=f"2: {DIG_PURE_LINES[1].strip()}", label=None)
    dig_btn_jump = mo.ui.button(label="ir",
        on_click=lambda _: set_dig_step(_dig_jump_to_line(get_dig_step(), dig_line_target.value)))
    return (
        dig_btn_jump,
        dig_btn_next,
        dig_btn_next_cand,
        dig_btn_prev,
        dig_btn_prev_cand,
        dig_line_target,
    )


@app.cell
def dig_cascade_display(
    ACTOR_IDS,
    BSTATE,
    DIG_PURE_LINES,
    G,
    GOLD,
    GRAY,
    PARAMO,
    POS_ARR,
    TIERRA,
    UNAL,
    dig_btn_jump,
    dig_btn_next,
    dig_btn_next_cand,
    dig_btn_prev,
    dig_btn_prev_cand,
    dig_line_target,
    dig_step_trace,
    episode_dropdown,
    get_dig_step,
    hop_radio,
    mo,
    mpatches,
    n,
    plt,
):
    _dig_idx = get_dig_step()
    _trace = dig_step_trace["trace"]
    _entry = _trace[_dig_idx]
    _loc = _entry["locals"]
    _lineno = _entry["lineno"]
    _actual = dig_step_trace["i"]
    _visitados = dig_step_trace["visitados"]
    _cadena_so_far = dig_step_trace["cadena_so_far"]
    _candidatos = _loc.get("candidatos")
    _cur_j = _loc.get("j") if _candidatos is not None else None
    _estrategias_so_far = _loc.get("estrategias", {})
    _m_winner = _loc.get("m")
    _is_return = (_entry.get("event") == "return")
    _visited_linenos = {_trace[k]["lineno"] for k in range(_dig_idx + 1)}

    _fig, (_axL, _axR) = plt.subplots(1, 2, figsize=(16, 8.2), gridspec_kw={"width_ratios": [1.1, 1.3]})
    _fig.patch.set_facecolor("#f8f9fa")

    _axL.axis("off"); _axL.set_xlim(0, 1); _axL.set_ylim(0, 1)
    _axL.set_title(f"_dig_decide(i = {ACTOR_IDS[_actual]})  --  paso {_dig_idx+1}/{len(_trace)}",
                   fontsize=12.5, color=UNAL, fontweight="bold", loc="left")

    _y0, _dy = 0.96, 0.043
    for _k, _line in enumerate(DIG_PURE_LINES):
        _this_lineno = _k + 1
        _y = _y0 - _k * _dy
        if _this_lineno == _lineno:
            _axL.add_patch(mpatches.FancyBboxPatch((0.0, _y - 0.019), 1.0, 0.038,
                boxstyle="round,pad=0.003,rounding_size=0.008", linewidth=0,
                facecolor=GOLD, alpha=0.35, transform=_axL.transAxes))
            _color, _weight = "#111", "bold"
        elif _this_lineno in _visited_linenos:
            _color, _weight = "#333", "normal"
        else:
            _color, _weight = "#bbb", "normal"
        _axL.text(0.02, _y, _line, fontsize=9.3, family="monospace", va="center",
                  color=_color, fontweight=_weight, transform=_axL.transAxes)

    _y_vals = _y0 - len(DIG_PURE_LINES) * _dy - 0.03
    _axL.text(0.02, _y_vals, "variables locales en este punto:", fontsize=10, color=UNAL,
              fontweight="bold", transform=_axL.transAxes)
    _loc_parts = []
    for _key in ["j", "mu_j", "r_i0", "r_i1", "r_ij", "denom", "x_ij", "m", "x_im"]:
        if _key == "j" and _candidatos is None:
            continue
        if _key in _loc:
            _v = _loc[_key]
            _vs = ACTOR_IDS[_v] if _key in ("j", "m") and isinstance(_v, int) else (f"{_v:.3f}" if isinstance(_v, float) else str(_v))
            _loc_parts.append(f"{_key}={_vs}")
    _axL.text(0.02, _y_vals - 0.05, "  ".join(_loc_parts) if _loc_parts else "(ninguna aun)",
              fontsize=9, family="monospace", color="#444", transform=_axL.transAxes)

    if _is_return:
        _accion_ret, _m_ret = _entry["returned"]
        _txt = (f"RETORNA ('{_accion_ret}', {ACTOR_IDS[_m_ret] if _m_ret is not None else None})")
        _axL.add_patch(mpatches.FancyBboxPatch((0.0, _y_vals - 0.13), 1.0, 0.06,
            boxstyle="round,pad=0.005,rounding_size=0.01", linewidth=0,
            facecolor=(PARAMO if _accion_ret == "execute" else GOLD), alpha=0.3, transform=_axL.transAxes))
        _axL.text(0.02, _y_vals - 0.10, _txt, fontsize=10, family="monospace", va="center",
                  color="#111", fontweight="bold", transform=_axL.transAxes)

    _axR.set_facecolor("#f8f9fa")
    for _i in range(n):
        for _j in range(_i + 1, n):
            if G[_i, _j]:
                _axR.plot([POS_ARR[_i, 0], POS_ARR[_j, 0]], [POS_ARR[_i, 1], POS_ARR[_j, 1]],
                          color=GRAY, lw=1.0, alpha=0.22, zorder=1)

    for _k in range(len(_cadena_so_far) - 1):
        _u, _v = _cadena_so_far[_k], _cadena_so_far[_k + 1]
        _axR.annotate("", xy=tuple(POS_ARR[_v]), xytext=tuple(POS_ARR[_u]),
                      arrowprops=dict(arrowstyle="-|>", color=TIERRA, lw=2.6, shrinkA=22, shrinkB=22), zorder=4)

    if _is_return and _entry["returned"][0] == "delegate":
        _mret = _entry["returned"][1]
        _axR.annotate("", xy=tuple(POS_ARR[_mret]), xytext=tuple(POS_ARR[_actual]),
                      arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=2.6, linestyle="dashed",
                                       shrinkA=22, shrinkB=22), zorder=4)

    for _idx, _aid in enumerate(ACTOR_IDS):
        _x, _y = POS_ARR[_idx]
        if _idx in _cadena_so_far[:-1]:
            _fc, _r = PARAMO, 0.30
        elif _idx == _actual:
            _fc, _r = UNAL, 0.38
        elif _candidatos is not None and _idx in _candidatos:
            if _idx in _estrategias_so_far:
                _fc = "#8B5A2B"
            elif _idx == _cur_j:
                _fc = GOLD
            else:
                _fc = "#e8c88c"
            _r = 0.28
        else:
            _fc, _r = "#cccccc", 0.24
        _axR.add_patch(plt.Circle((_x, _y), _r, facecolor=_fc, edgecolor="white", lw=1.3, zorder=3))
        if _idx == _actual:
            _axR.add_patch(plt.Circle((_x, _y), _r + 0.09, facecolor="none", edgecolor=BSTATE, lw=2.4, zorder=5))
        if _idx == _m_winner and _candidatos is not None and _idx in _candidatos:
            _axR.add_patch(plt.Circle((_x, _y), _r + 0.06, facecolor="none", edgecolor=TIERRA, lw=2.2, zorder=5))

        _lbl = [_aid]
        if _idx in _estrategias_so_far:
            _xij, _rij = _estrategias_so_far[_idx]
            _lbl.append(f"r_ij={_rij:.2f} x={_xij:.2f} [OK]")
        elif _idx == _cur_j:
            if "mu_j" in _loc: _lbl.append(f"mu={_loc['mu_j']:.2f}")
            if "r_i0" in _loc: _lbl.append(f"r_i0={_loc['r_i0']:.2f}")
            if "r_i1" in _loc: _lbl.append(f"r_i1={_loc['r_i1']:.2f}")
            if "r_ij" in _loc: _lbl.append(f"r_ij={_loc['r_ij']:.2f}")
            if "x_ij" in _loc: _lbl.append(f"x={_loc['x_ij']:.2f}")
        _axR.text(_x, _y - _r - 0.30, "\\n".join(_lbl), ha="center", va="top", fontsize=8.0, color="#222", zorder=6)

    _axR.set_xlim(POS_ARR[:, 0].min() - 1.2, POS_ARR[:, 0].max() + 1.2)
    _y_top = POS_ARR[:, 1].max() + 1.5
    _axR.set_ylim(POS_ARR[:, 1].min() - 2.1, _y_top + 0.5)
    _axR.set_aspect("equal"); _axR.axis("off")
    _axR.set_title(
        f"episodio {episode_dropdown.value}  -  nodo actual: {ACTOR_IDS[_actual]}  -  "
        f"cadena hasta ahora: {'-'.join(ACTOR_IDS[i] for i in _cadena_so_far)}",
        fontsize=10.5, color=UNAL)
    _axR.text((POS_ARR[:, 0].min() + POS_ARR[:, 0].max()) / 2, POS_ARR[:, 1].min() - 1.9,
              "verde=visitado . azul+aro rojo=decidiendo . dorado=en curso . cafe=finalizado . gris=fuera/desconocido",
              ha="center", va="top", fontsize=8.0, color="#555")

    if _candidatos is None:
        _axR.text((POS_ARR[:, 0].min() + POS_ARR[:, 0].max()) / 2, _y_top,
                  "candidatos aun no calculados en este punto de la ejecucion",
                  ha="center", va="top", fontsize=9.5, color="#777", style="italic")

    if _is_return:
        _res_col = PARAMO if _entry["returned"][0] == "execute" else GOLD

    plt.tight_layout()
    _dig_accordion = mo.accordion({
        "🔍 DIG — flujo completo (referencia, no interactivo)": mo.md(r"""
    **Entrada:** `i` (nodo actual), `visitados` (cadena hasta ahora), `alpha`/`beta_` (posterior Beta
    por actor, compartida entre episodios), `delta=0.10` (umbral de confianza para delegar)

    ```
    PASO 1 — Candidatos directos                    # -> _dig_decide_pure L.2
      candidatos = { j : (i,j) en G, j no visitado }
      si candidatos == vacio: ejecutar(i)             -> L.3-4

    PASO 2 — Muestreo Thompson (para TODOS los actores, no solo candidatos)
      theta_k ~ Beta(alpha_k, beta_k)  para todo k    -> L.5   # posterior de calidad

    PASO 3 — Por cada candidato j                    # -> L.7-15
      ad_j  = vecinos de j de 2do orden (excluye i, visitados)     -> L.8
      mu_j  = alpha_j / (alpha_j + beta_j)             # media Beta (registro historico)  -> L.9
      r_i0  = theta_j                                  # creencia sobre j directo          -> L.10
      r_i1  = max(theta_k para k en ad_j, default=r_i0) # mejor opcion de 2do orden         -> L.11
      r_ij  = (r_i0 + r_i1) / 2                        # promedio de valor delegado         -> L.12
      x_ij  = (r_i1 - r_i0) / (r_ij - mu_j)             # intensidad de delegacion           -> L.13-14

    PASO 4 — Elegir el mejor candidato                # -> L.16-17
      m     = argmax_j r_ij
      x_im  = x_ij del ganador m

    PASO 5 — Decidir                                  # -> L.18-20
      si (1 - delta) < x_im:  delegar en m
      si no:                   ejecutar(i)
    ```

    **Por que `x_ij` mide "intensidad de delegacion":** compara cuanto mejora la opcion de
    segundo orden (`r_i1`) sobre el candidato directo (`r_i0`), relativo a que tan lejos esta
    `r_ij` del registro historico de j (`mu_j`). Si el candidato ya esta muy por encima de su
    propio historial, delegar aporta poco margen adicional.

    **Lo que el seguimiento de arriba no puede ocultar:** `visitados` crece con cada salto real —
    por eso ninguna cascada observada llega a W4 (ver problematizacion abajo): la distancia
    estructural, no una decision activa contra W4, es la causa.
    """)
    })

    mo.vstack([
        mo.hstack([episode_dropdown, hop_radio], justify="start", gap=2, wrap=True),
        mo.hstack([
            mo.vstack([mo.md("**paso**"), mo.hstack([dig_btn_prev, dig_btn_next], gap=1)]),
            mo.vstack([mo.md("**candidato**"), mo.hstack([dig_btn_prev_cand, dig_btn_next_cand], gap=1)]),
            mo.vstack([mo.md("**ir a linea**"), mo.hstack([dig_line_target, dig_btn_jump], gap=1)]),
        ], justify="start", gap=3, wrap=True),
        _fig,
        _dig_accordion,
    ])
    return


@app.cell
def dig_problematisacion(
    ACTOR_IDS,
    desempeno,
    dig_episodes,
    dig_mu_roll,
    mo,
    ucb1_mu_roll,
):

    _dig_far = dig_episodes[181]
    _dig_far_len = len(_dig_far["cadena"])
    _dig_far_ids = "-".join(ACTOR_IDS[_x] for _x in _dig_far["cadena"])
    _ucb1_late = float(ucb1_mu_roll[-100:].mean())
    _dig_late = float(dig_mu_roll[-100:].mean())

    mo.md(f"""
    **Lo que DIG nos enseña:** cada nodo decide con su propio muestreo Thompson
    (`θ ~ Beta(α,β)`) sobre delegar o ejecutar, combinando su creencia sobre un
    candidato directo (`r_i0`) con la mejor opción de un vecino de segundo orden
    (`r_i1`) — una cascada de decisiones distribuidas sin un árbitro central.
    El seguimiento que acabas de recorrer muestra esa decisión línea por línea, sin
    atajos.

    **Lo que DIG problematiza (I) — el mérito se homogeniza en la cadena:** la
    cascada más larga observada en 1000 episodios (`{_dig_far_ids}`,
    {_dig_far_len} nodos) **nunca llega a W4** — el actor de registro
    cosmológico-territorial, el más distante en la red. No es que a través de DIG se decida
    activamente excluir a W4: es que `visitados` crece con cada salto y el
    vecindario de segundo orden (`ad_j`) desde donde la cascada empieza
    simplemente no alcanza esa distancia en la topología de la red. Además, cuando la
    cascada finalmente ejecuta, el resultado binario (éxito/fracaso) actualiza el
    par `(α,β)` de **todos** los actores de la cadena por igual — la reputación
    de quien decidió delegar en el primer salto queda atada al desempeño de quien
    ejecutó al final, sin distinguir cuánto contribuyó cada quien.

    **Lo que DIG problematiza (II) — ganar en promedio no es ganar siempre:**
    esta corrida arranca a DIG en W1, el nodo de mayor incidencia territorial
    ({desempeno[1]:.3f}). Sobre los 1000 episodios completos, DIG termina con
    mejor tasa de éxito y menor arrepentimiento acumulado que UCB1 — pero esa
    ventaja proviene casi enteramente de la ventaja de salida: DIG ya "sabe"
    desde el episodio 1 que W1 es el mejor nodo, mientras UCB1 necesita explorar
    ~50-100 rondas para aprenderlo. Hacia el final del horizonte la historia
    local se invierte: en las últimas 100 rondas UCB1 promedia
    **{_ucb1_late:.3f}** de éxito, DIG solo **{_dig_late:.3f}** — una vez que
    UCB1 converge, permanece en su mejor brazo sin desviarse, mientras la propia
    fórmula de delegación de DIG (`x_ij`) sigue provocando, con la incidencia
    territorial actual, delegaciones fuera de W1 incluso cuando quedarse ahí era
    la mejor opción. Estructura real, ventaja real — pero acumulada a lo largo
    del horizonte completo, no sostenida en cada tramo de él.
    """)
    return


@app.cell
def dig_formula_diagnostic(G, cal_original, desempeno, n, np):

    def _dig_self_exec_diagnostic(quality, seed=257, T=1000, K=300.0, delta=0.10, burn_in=500):
        rng = np.random.default_rng(seed)
        alpha_d = {i: 1.0 for i in range(n)}
        beta_d = {i: 1.0 for i in range(n)}
        consumo = 0.0
        denom_log = []
        self_exec = 0
        total_eps = 0
        for t in range(T):
            if consumo >= K:
                break
            cadena = [0]
            actual = 0
            while True:
                visitados = set(cadena)
                candidatos = [j for j in range(n) if G[actual][j] and j not in visitados]
                if not candidatos:
                    break
                theta = {k: rng.beta(alpha_d[k], beta_d[k]) for k in range(n)}
                estrategias = {}
                for j in candidatos:
                    ad_j = [k for k in range(n) if G[j][k] and k != actual and k not in visitados]
                    mu_j = alpha_d[j] / (alpha_d[j] + beta_d[j])
                    r_i0 = theta[j]
                    r_i1 = max((theta[k] for k in ad_j), default=r_i0)
                    r_ij = (r_i0 + r_i1) / 2.0
                    denom = r_ij - mu_j
                    x_ij = 0.0 if abs(denom) < 1e-12 else max(0.0, min(1.0, (r_i1 - r_i0) / denom))
                    estrategias[j] = (x_ij, r_ij)
                    if t > burn_in:
                        denom_log.append(denom)
                m = max(estrategias, key=lambda j: estrategias[j][1])
                x_im, _ = estrategias[m]
                if (1.0 - delta) < x_im:
                    cadena.append(m); actual = m
                else:
                    break
                if len(cadena) >= 7:
                    break
            if t > burn_in:
                total_eps += 1
                if len(cadena) == 1:
                    self_exec += 1
            ejecutor = cadena[-1]
            resultado = int(rng.binomial(1, quality[ejecutor]))
            for ag in cadena:
                if resultado > 0: alpha_d[ag] += 1
                else: beta_d[ag] += 1
            consumo += 1.0 / (alpha_d[ejecutor] + beta_d[ejecutor])
        denom_arr = np.array(denom_log)
        return dict(self_exec_rate=self_exec / total_eps, denom_mean=float(denom_arr.mean()),
                    denom_near_zero_frac=float((np.abs(denom_arr) < 0.05).mean()))

    dig_diag_new = _dig_self_exec_diagnostic(desempeno)
    dig_diag_old = _dig_self_exec_diagnostic(cal_original)
    return


@app.cell
def dec_pure_setup(G, desempeno, n, np, sys):

    import math
    from itertools import combinations
    from collections import deque

    def compute_positions_dec(root):
        pos, q, orden = {}, deque([root]), 0
        while q:
            u = q.popleft()
            if u in pos: continue
            orden += 1; pos[u] = orden
            for v in range(n):
                if G[u][v] and v not in pos:
                    q.append(v)
        return pos

    _CFORM_SRC = """def _cform_pure(k_agente, rng):
        candidatos = [j for j in range(n) if G[k_agente][j]]
        if not candidatos:
            return [k_agente]
        k_actual  = candidatos[rng.integers(0, len(candidatos))]
        coalicion = [k_agente, k_actual]
        max_len   = rng.integers(2, 4)
        while len(coalicion) < max_len:
            sig = [m for m in range(n) if G[k_actual][m] and m not in coalicion]
            if not sig: break
            m = sig[rng.integers(0, len(sig))]
            coalicion.append(m); k_actual = m
        return coalicion
    """

    _HARM_SRC = """def _harmonic_dec_pure(k):
        return sum(1.0 / i for i in range(1, k + 1))
    """

    _MYERSON_SRC = """def _myerson_within_pure(coalicion, r):
        coalicion = list(coalicion)
        k = len(coalicion)
        if k == 1:
            return {coalicion[0]: r[coalicion[0]]}
        def nu(S):
            S = set(S)
            if not S: return 0.0
            visited, total = set(), 0.0
            for s0 in S:
                if s0 in visited: continue
                comp, pila = set(), [s0]
                while pila:
                    x = pila.pop()
                    if x in visited: continue
                    visited.add(x); comp.add(x)
                    for y in S:
                        if y not in visited and G[x][y]:
                            pila.append(y)
                total += sum(r[i] for i in comp)
            return total
        phi = {i: 0.0 for i in coalicion}
        for i in coalicion:
            resto = [j for j in coalicion if j != i]
            for sz in range(len(resto) + 1):
                for S in combinations(resto, sz):
                    g = math.factorial(sz) * math.factorial(k - sz - 1) / math.factorial(k)
                    phi[i] += g * (nu(set(S) | {i}) - nu(set(S)))
        return phi
    """

    _DEL_SRC = """def _del_pure(k_agente, r, v_alloc_local, V_local, rng, profundidad=0):
        if profundidad > n:
            return k_agente, r[k_agente], [k_agente]
        coalicion = _cform_pure(k_agente, rng)
        my        = _myerson_within_pure(coalicion, r)
        opciones  = {i: my[i] for i in range(n) if G[k_agente][i] and i in my}
        opciones[k_agente] = r[k_agente]
        m = max(opciones, key=lambda i: opciones[i])
        if m != k_agente:
            pos_m = coalicion.index(m) + 1
            o_m   = rng.uniform(v_alloc_local[m], V_local)
            r[m]  = pos_m * o_m / _harmonic_dec_pure(len(coalicion))
            m2, r_final, cola = _del_pure(m, r, v_alloc_local, V_local, rng, profundidad + 1)
            return m2, r_final, [k_agente] + cola
        else:
            o_m = rng.uniform(v_alloc_local[k_agente], V_local)
            r[k_agente] = o_m
            return k_agente, o_m, [k_agente]
    """

    DEC_PURE_LINES = _DEL_SRC.rstrip(chr(10)).split(chr(10))

    _dec_pure_ns = {"n": n, "G": G, "math": math, "combinations": combinations}
    exec(compile(_CFORM_SRC, "<cform_pure>", "exec"), _dec_pure_ns)
    exec(compile(_HARM_SRC, "<harm_pure>", "exec"), _dec_pure_ns)
    exec(compile(_MYERSON_SRC, "<myerson_pure>", "exec"), _dec_pure_ns)
    exec(compile(_DEL_SRC, "<del_pure>", "exec"), _dec_pure_ns)
    _del_pure = _dec_pure_ns["_del_pure"]

    _cform_pure_ref = _dec_pure_ns["_cform_pure"]
    _myerson_within_pure_ref = _dec_pure_ns["_myerson_within_pure"]
    _harmonic_dec_pure_ref = _dec_pure_ns["_harmonic_dec_pure"]

    def _del_pure_costed(k_agente, r, v_alloc_local, V_local, rng, touched, profundidad=0):
        if profundidad > n:
            return k_agente, r[k_agente], [k_agente]
        coalicion = _cform_pure_ref(k_agente, rng)
        touched.extend(coalicion)
        my = _myerson_within_pure_ref(coalicion, r)
        opciones = {i: my[i] for i in range(n) if G[k_agente][i] and i in my}
        opciones[k_agente] = r[k_agente]
        m = max(opciones, key=lambda i: opciones[i])
        if m != k_agente:
            pos_m = coalicion.index(m) + 1
            o_m = rng.uniform(v_alloc_local[m], V_local)
            r[m] = pos_m * o_m / _harmonic_dec_pure_ref(len(coalicion))
            m2, r_final, cola = _del_pure_costed(m, r, v_alloc_local, V_local, rng, touched, profundidad + 1)
            return m2, r_final, [k_agente] + cola
        else:
            o_m = rng.uniform(v_alloc_local[k_agente], V_local)
            r[k_agente] = o_m
            return k_agente, o_m, [k_agente]

    dec_del_pure_costed = _del_pure_costed

    _DEC_KEEP_VARS = ["coalicion", "my", "opciones", "m", "pos_m", "o_m", "m2", "r_final", "cola", "k_agente", "profundidad"]

    def _dec_snap_locals(loc):
        out = {}
        for k in _DEC_KEEP_VARS:
            if k in loc:
                v = loc[k]
                out[k] = dict(v) if isinstance(v, dict) else (list(v) if isinstance(v, list) else v)
        return out

    def dec_trace_episode(raiz, seed, target_t, K=300.0, T=1000):
        rng = np.random.default_rng(seed)
        pos_local = compute_positions_dec(raiz)
        T_n_local = sum(pos_local.values())
        V_local = float(desempeno.sum()) * 2
        v_alloc = {j: (pos_local[j] + 1) * V_local / T_n_local for j in range(n)}
        alpha = {j: 1.0 for j in range(n)}
        beta_ = {j: 1.0 for j in range(n)}
        r = dict(v_alloc)
        consumo = 0.0
        del_code_obj = _del_pure.__code__

        def make_global_tracer(tl):
            def local_tracer(frame, event, arg):
                if frame.f_code is not del_code_obj:
                    return local_tracer
                depth = frame.f_locals.get("profundidad", 0)
                if event == "line":
                    tl.append(dict(depth=depth, lineno=frame.f_lineno,
                                    locals=_dec_snap_locals(frame.f_locals), event="line"))
                elif event == "return":
                    tl.append(dict(depth=depth, lineno=frame.f_lineno,
                                    locals=_dec_snap_locals(frame.f_locals), event="return", returned=arg))
                return local_tracer
            def global_tracer(frame, event, arg):
                if event == "call" and frame.f_code is del_code_obj:
                    return local_tracer
                return None
            return global_tracer

        for t in range(min(target_t + 1, T)):
            if consumo >= K:
                break
            if t == target_t:
                trace_list = []
                sys.settrace(make_global_tracer(trace_list))
                try:
                    m_res, r_final_res, cadena = _del_pure(raiz, r, v_alloc, V_local, rng, 0)
                finally:
                    sys.settrace(None)
                collapsed = []
                for entry in trace_list:
                    if (collapsed and collapsed[-1]["depth"] == entry["depth"]
                            and collapsed[-1]["lineno"] == entry["lineno"] and entry["event"] == "line"):
                        collapsed[-1] = entry
                    else:
                        collapsed.append(entry)
                return dict(trace=collapsed, raiz=raiz, cadena=cadena, m=m_res)
            m_t, _, cadena_t = _del_pure(raiz, r, v_alloc, V_local, rng, 0)
            exito = rng.binomial(1, desempeno[m_t]) > 0
            if exito: alpha[m_t] += 1
            else: beta_[m_t] += 1
            consumo += 1.0 / (alpha[m_t] + beta_[m_t])
        return None

    dec_del_pure = _del_pure
    return (
        DEC_PURE_LINES,
        compute_positions_dec,
        dec_del_pure_costed,
        dec_trace_episode,
    )


@app.cell
def dec_episode_dropdown_cell(mo):

    DEC_ROOT = 3  # W3 -- favorable root, unified between the debugger and the comparison
    DEC_SEED = 0
    DEC_CURATED = {
        "cascada corta, cierre limpio (W3-W2)": 1,
        "coalición de 3, cierre en W1 (W3-W2-W1)": 55,
        "ciclo real: W2 decide dos veces (W3-W2-W0-W2)": 361,
    }
    dec_episode_dropdown = mo.ui.dropdown(
        options=DEC_CURATED, value="ciclo real: W2 decide dos veces (W3-W2-W0-W2)",
        label="episodio DEC (curado)")
    return DEC_ROOT, DEC_SEED, dec_episode_dropdown


@app.cell
def dec_depth_radio_cell(
    ACTOR_IDS,
    DEC_ROOT,
    DEC_SEED,
    dec_episode_dropdown,
    dec_trace_episode,
    mo,
):

    _dec_ep_preview = dec_trace_episode(DEC_ROOT, DEC_SEED, dec_episode_dropdown.value)
    _dec_depths_preview = sorted(set(e["depth"] for e in _dec_ep_preview["trace"]))
    _dec_depth_options = {
        f"profundidad {d}: {ACTOR_IDS[_dec_ep_preview['trace'][[e['depth'] for e in _dec_ep_preview['trace']].index(d)]['locals'].get('k_agente', DEC_ROOT)]} decide": d
        for d in _dec_depths_preview
    }
    dec_depth_radio = mo.ui.radio(options=_dec_depth_options, value=list(_dec_depth_options.keys())[0],
                                   label="profundidad (nodo que decide)")
    return (dec_depth_radio,)


@app.cell
def dec_trace_state_cell(
    DEC_ROOT,
    DEC_SEED,
    dec_episode_dropdown,
    dec_trace_episode,
    mo,
):

    dec_step_trace = dec_trace_episode(DEC_ROOT, DEC_SEED, dec_episode_dropdown.value)
    get_dec_step, set_dec_step = mo.state(0)
    return dec_step_trace, get_dec_step, set_dec_step


@app.cell
def dec_step_buttons_cell(
    DEC_PURE_LINES,
    dec_depth_radio,
    dec_step_trace,
    get_dec_step,
    mo,
    set_dec_step,
):

    _dec_trace_ref = dec_step_trace["trace"]
    _dec_max_idx = len(_dec_trace_ref) - 1

    def _dec_depth_of(idx):
        return _dec_trace_ref[idx]["depth"]

    def _dec_next_depth_change(idx):
        cur_d = _dec_depth_of(idx)
        for k in range(idx + 1, len(_dec_trace_ref)):
            if _dec_depth_of(k) != cur_d:
                return k
        return _dec_max_idx

    def _dec_prev_depth_change(idx):
        cur_d = _dec_depth_of(idx)
        for k in range(idx - 1, -1, -1):
            if _dec_depth_of(k) != cur_d:
                return k
        return 0

    def _dec_jump_to_line(idx, target_lineno):
        for k in range(idx + 1, len(_dec_trace_ref)):
            if _dec_trace_ref[k]["lineno"] == target_lineno:
                return k
        for k in range(0, idx + 1):
            if _dec_trace_ref[k]["lineno"] == target_lineno:
                return k
        return idx

    def _dec_jump_to_depth(idx, target_depth):
        for k in range(len(_dec_trace_ref)):
            if _dec_trace_ref[k]["depth"] == target_depth:
                return k
        return idx

    dec_btn_prev = mo.ui.button(label="◀",
        on_click=lambda _: set_dec_step(max(0, get_dec_step() - 1)))
    dec_btn_next = mo.ui.button(label="▶",
        on_click=lambda _: set_dec_step(min(_dec_max_idx, get_dec_step() + 1)))
    dec_btn_prev_depth = mo.ui.button(label="◀◀",
        on_click=lambda _: set_dec_step(_dec_prev_depth_change(get_dec_step())))
    dec_btn_next_depth = mo.ui.button(label="▶▶",
        on_click=lambda _: set_dec_step(_dec_next_depth_change(get_dec_step())))
    dec_btn_goto_depth = mo.ui.button(label="ir",
        on_click=lambda _: set_dec_step(_dec_jump_to_depth(get_dec_step(), dec_depth_radio.value)))

    _dec_line_options = {f"{_i+1}: {_txt.strip()}": _i + 1 for _i, _txt in enumerate(DEC_PURE_LINES)}
    dec_line_target = mo.ui.dropdown(options=_dec_line_options,
        value=f"3: {DEC_PURE_LINES[2].strip()}", label=None)
    dec_btn_jump = mo.ui.button(label="ir",
        on_click=lambda _: set_dec_step(_dec_jump_to_line(get_dec_step(), dec_line_target.value)))
    return (
        dec_btn_goto_depth,
        dec_btn_jump,
        dec_btn_next,
        dec_btn_next_depth,
        dec_btn_prev,
        dec_btn_prev_depth,
        dec_line_target,
    )


@app.cell
def dec_cascade_display(
    ACTOR_IDS,
    BSTATE,
    DEC_PURE_LINES,
    DEC_ROOT,
    G,
    GOLD,
    GRAY,
    PARAMO,
    POS_ARR,
    TIERRA,
    UNAL,
    dec_btn_goto_depth,
    dec_btn_jump,
    dec_btn_next,
    dec_btn_next_depth,
    dec_btn_prev,
    dec_btn_prev_depth,
    dec_depth_radio,
    dec_episode_dropdown,
    dec_line_target,
    dec_step_trace,
    get_dec_step,
    mo,
    mpatches,
    n,
    plt,
):

    _dec_idx = get_dec_step()
    _dtrace = dec_step_trace["trace"]
    _dentry = _dtrace[_dec_idx]
    _dloc = _dentry["locals"]
    _dlineno = _dentry["lineno"]
    _ddepth = _dentry["depth"]
    _dk_agente = _dloc.get("k_agente", DEC_ROOT)
    _dcoalicion = _dloc.get("coalicion")
    _dmy = _dloc.get("my", {})
    _dopciones = _dloc.get("opciones", {})
    _dm = _dloc.get("m")
    _dis_return = (_dentry.get("event") == "return")
    _dvisited_linenos = {_dtrace[k]["lineno"] for k in range(_dec_idx + 1)}

    _ddepths_seen = sorted(set(_dtrace[k]["depth"] for k in range(_dec_idx + 1)))
    _dchain_so_far = []
    for _d in _ddepths_seen:
        _first_k = next(k for k in range(_dec_idx + 1) if _dtrace[k]["depth"] == _d)
        _dchain_so_far.append(_dtrace[_first_k]["locals"].get("k_agente", DEC_ROOT))

    _fig, (_axL, _axR) = plt.subplots(1, 2, figsize=(16, 8.2), gridspec_kw={"width_ratios": [1.1, 1.3]})
    _fig.patch.set_facecolor("#f8f9fa")

    _axL.axis("off"); _axL.set_xlim(0, 1); _axL.set_ylim(0, 1)
    _axL.set_title(f"_del_pure(k_agente = {ACTOR_IDS[_dk_agente]}, profundidad = {_ddepth})  --  paso {_dec_idx+1}/{len(_dtrace)}",
                   fontsize=12.5, color=UNAL, fontweight="bold", loc="left")

    _y0, _dy = 0.96, 0.052
    for _k, _line in enumerate(DEC_PURE_LINES):
        _this_lineno = _k + 1
        _y = _y0 - _k * _dy
        if _this_lineno == _dlineno:
            _axL.add_patch(mpatches.FancyBboxPatch((0.0, _y - 0.022), 1.0, 0.044,
                boxstyle="round,pad=0.003,rounding_size=0.008", linewidth=0,
                facecolor=GOLD, alpha=0.35, transform=_axL.transAxes))
            _color, _weight = "#111", "bold"
        elif _this_lineno in _dvisited_linenos:
            _color, _weight = "#333", "normal"
        else:
            _color, _weight = "#bbb", "normal"
        _axL.text(0.02, _y, _line, fontsize=9.0, family="monospace", va="center",
                  color=_color, fontweight=_weight, transform=_axL.transAxes)

    _y_vals = _y0 - len(DEC_PURE_LINES) * _dy - 0.03
    _axL.text(0.02, _y_vals, f"variables locales (profundidad {_ddepth}):", fontsize=10, color=UNAL,
              fontweight="bold", transform=_axL.transAxes)
    _loc_parts = [f"k_agente={ACTOR_IDS[_dk_agente]}"]
    if _dcoalicion is not None:
        _loc_parts.append("coalicion=[" + ",".join(ACTOR_IDS[_x] for _x in _dcoalicion) + "]")
    if "m" in _dloc:
        _loc_parts.append(f"m={ACTOR_IDS[_dloc['m']]}")
    for _key in ["pos_m", "o_m", "r_final"]:
        if _key in _dloc:
            _v = _dloc[_key]
            _loc_parts.append(f"{_key}={_v:.3f}" if isinstance(_v, float) else f"{_key}={_v}")
    _axL.text(0.02, _y_vals - 0.05, "  ".join(_loc_parts), fontsize=8.6, family="monospace",
              color="#444", transform=_axL.transAxes, wrap=True)

    if _dis_return:
        _m2_ret, _rf_ret, _cola_ret = _dentry["returned"]
        _txt = f"RETORNA (m={ACTOR_IDS[_m2_ret]}, r={_rf_ret:.3f}, cola=[{','.join(ACTOR_IDS[_x] for _x in _cola_ret)}])"
        _axL.add_patch(mpatches.FancyBboxPatch((0.0, _y_vals - 0.13), 1.0, 0.06,
            boxstyle="round,pad=0.005,rounding_size=0.01", linewidth=0,
            facecolor=PARAMO, alpha=0.3, transform=_axL.transAxes))
        _axL.text(0.02, _y_vals - 0.10, _txt, fontsize=9.3, family="monospace", va="center",
                  color="#111", fontweight="bold", transform=_axL.transAxes)

    _axR.set_facecolor("#f8f9fa")
    for _i in range(n):
        for _j in range(_i + 1, n):
            if G[_i, _j]:
                _axR.plot([POS_ARR[_i, 0], POS_ARR[_j, 0]], [POS_ARR[_i, 1], POS_ARR[_j, 1]],
                          color=GRAY, lw=1.0, alpha=0.22, zorder=1)

    for _k in range(len(_dchain_so_far) - 1):
        _u, _v = _dchain_so_far[_k], _dchain_so_far[_k + 1]
        _axR.annotate("", xy=tuple(POS_ARR[_v]), xytext=tuple(POS_ARR[_u]),
                      arrowprops=dict(arrowstyle="-|>", color=TIERRA, lw=2.6, shrinkA=22, shrinkB=22), zorder=4)

    if _dis_return and _dentry["returned"][0] != _dk_agente:
        _mret = _dentry["returned"][0]
    elif _dm is not None and _dm != _dk_agente:
        _mret = _dm
    else:
        _mret = None
    if _mret is not None and not (_dis_return and _ddepth == 0 and len(_dchain_so_far) > 1):
        pass

    for _idx, _aid in enumerate(ACTOR_IDS):
        _x, _y = POS_ARR[_idx]
        if _idx in _dchain_so_far[:-1]:
            _fc, _rad = PARAMO, 0.30
        elif _idx == _dk_agente:
            _fc, _rad = UNAL, 0.38
        elif _dcoalicion is not None and _idx in _dcoalicion:
            if _idx in _dmy:
                _fc = "#8B5A2B"
            else:
                _fc = GOLD
            _rad = 0.28
        else:
            _fc, _rad = "#cccccc", 0.24
        _axR.add_patch(plt.Circle((_x, _y), _rad, facecolor=_fc, edgecolor="white", lw=1.3, zorder=3))
        if _idx == _dk_agente:
            _axR.add_patch(plt.Circle((_x, _y), _rad + 0.09, facecolor="none", edgecolor=BSTATE, lw=2.4, zorder=5))
        if _idx == _dm and _dcoalicion is not None and _idx in _dcoalicion:
            _axR.add_patch(plt.Circle((_x, _y), _rad + 0.06, facecolor="none", edgecolor=TIERRA, lw=2.2, zorder=5))

        _lbl = [_aid]
        if _idx in _dmy:
            _lbl.append(f"my={_dmy[_idx]:.2f}")
        if _idx in _dopciones:
            _lbl.append(f"opc={_dopciones[_idx]:.2f}")
        _axR.text(_x, _y - _rad - 0.30, "\n".join(_lbl), ha="center", va="top", fontsize=7.6, color="#222", zorder=6)

    if _dcoalicion is not None and _dlineno >= 11 and _dm is not None and _dm != _dk_agente:
        _axR.annotate("", xy=tuple(POS_ARR[_dm]), xytext=tuple(POS_ARR[_dk_agente]),
                      arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=2.6, linestyle="dashed",
                                       shrinkA=22, shrinkB=22), zorder=4)

    _axR.set_xlim(POS_ARR[:, 0].min() - 1.2, POS_ARR[:, 0].max() + 1.2)
    _y_top = POS_ARR[:, 1].max() + 1.5
    _axR.set_ylim(POS_ARR[:, 1].min() - 2.1, _y_top + 0.5)
    _axR.set_aspect("equal"); _axR.axis("off")
    _axR.set_title(
        f"episodio DEC t={dec_episode_dropdown.value}  -  nodo actual: {ACTOR_IDS[_dk_agente]}  -  "
        f"cadena hasta ahora: {'-'.join(ACTOR_IDS[_i] for _i in _dchain_so_far)}",
        fontsize=10.2, color=UNAL)
    _axR.text((POS_ARR[:, 0].min() + POS_ARR[:, 0].max()) / 2, POS_ARR[:, 1].min() - 1.9,
              "verde=ya decidio . azul+aro rojo=decidiendo ahora . dorado=en coalicion . cafe=valor Myerson calculado . cafe con aro=ganador m",
              ha="center", va="top", fontsize=7.8, color="#555")

    if _dcoalicion is None:
        _axR.text((POS_ARR[:, 0].min() + POS_ARR[:, 0].max()) / 2, _y_top,
                  "coalicion aun no formada en este punto de la ejecucion",
                  ha="center", va="top", fontsize=9.5, color="#777", style="italic")

    plt.tight_layout()
    _dec_accordion = mo.accordion({
        "🔍 DEC — flujo completo (referencia, no interactivo)": mo.md(r"""
    **Entrada:** `k_agente` (nodo que decide), `r` (valor compartido por actor, mutado entre
    episodios), `v_alloc_local`/`V_local` (asignacion base por posicion), `profundidad` (nivel de
    recursion — cada nivel es un salto de delegacion)

    ```
    PASO 0 — Corte de recursion                        # -> _del_pure L.2-3
      si profundidad > n: retornar (k_agente, r[k_agente], [k_agente])

    PASO 1 — Formar coalicion (CFORM, caminata aleatoria sobre vecinos de G)
      coalicion = cform(k_agente)                       # 2 a 4 nodos conectados   -> L.4

    PASO 2 — Valor de Myerson dentro de la coalicion (Shapley sobre componentes conexas)
      my = myerson_within(coalicion, r)                 # reparto justo, sum(my) = sum(r(coalicion)) -> L.5

    PASO 3 — Opciones de k_agente                       # -> L.6-7
      opciones = { vecinos directos de k_agente en la coalicion : su valor my }
      opciones[k_agente] = r[k_agente]                  # opcion de auto-ejecutar

    PASO 4 — Decidir                                    # -> L.8
      m = argmax(opciones)                              # delegar o auto-ejecutar?

    PASO 5a — Delegar (m != k_agente)                    # -> L.9-14
      pos_m = posicion de m en la coalicion
      o_m   = valor de ejecucion muestreado ~ Uniform(v_alloc[m], V_local)
      r[m]  = pos_m * o_m / harmonic(len(coalicion))    # actualiza r COMPARTIDO — persiste entre episodios
      DEL(m, ..., profundidad + 1)                       # recursion real de Python — el siguiente salto

    PASO 5b — Auto-ejecutar (m == k_agente)              # -> L.15-18
      o_m = valor muestreado ~ Uniform(v_alloc[k_agente], V_local)
      r[k_agente] = o_m
      retornar (k_agente, o_m, [k_agente])
    ```

    **Por que esto es cooperacion, no competencia por un solo brazo:** `myerson_within` reparte
    `sum(my) = sum(r)` entre los miembros de la coalicion — un teorema (Myerson 1977), no una esperanza
    estadistica. Pero la decision de SEGUIR delegando (PASO 4) compara ese reparto contra el
    valor de auto-ejecutar de `k_agente`, no contra los otros miembros — de ahi que el mismo actor
    pueda ser convocado dos veces en una cadena (ver el episodio con ciclo en el seguimiento de
    arriba): `DEL` no lleva un conjunto de visitados como si lo hace DIG.
    """)
    })

    mo.vstack([
        mo.hstack([dec_episode_dropdown, dec_depth_radio], justify="start", gap=2, wrap=True),
        mo.hstack([
            mo.vstack([mo.md("**paso**"), mo.hstack([dec_btn_prev, dec_btn_next], gap=1)]),
            mo.vstack([mo.md("**profundidad**"), mo.hstack([dec_btn_prev_depth, dec_btn_next_depth], gap=1)]),
            mo.vstack([mo.md("**ir a profundidad**"), mo.hstack([dec_btn_goto_depth], gap=1)]),
            mo.vstack([mo.md("**ir a linea**"), mo.hstack([dec_line_target, dec_btn_jump], gap=1)]),
        ], justify="start", gap=3, wrap=True),
        _fig,
        _dec_accordion,
    ])
    return


@app.cell
def dec_full_run_cell(
    DEC_ROOT,
    DEC_SEED,
    compute_positions_dec,
    dec_del_pure_costed,
    desempeno,
    n,
    np,
):

    def _dec_full_run(raiz, seed, K=300.0, T=1000):
        rng = np.random.default_rng(seed)
        pos_local = compute_positions_dec(raiz)
        T_n_local = sum(pos_local.values())
        V_local = float(desempeno.sum()) * 2
        v_alloc = {j: (pos_local[j] + 1) * V_local / T_n_local for j in range(n)}
        alpha = {j: 1.0 for j in range(n)}
        beta_ = {j: 1.0 for j in range(n)}
        r = dict(v_alloc)
        consumo = 0.0
        ejecutor, long_cadena, psd = [], [], []
        for _t in range(T):
            if consumo >= K:
                break
            _touched = []
            m_t, _, cadena_t = dec_del_pure_costed(raiz, r, v_alloc, V_local, rng, _touched, 0)
            exito = rng.binomial(1, desempeno[m_t]) > 0
            # true coalition cost: every CFORM member at every recursion depth, not just the executor
            _cost = sum(1.0 / (alpha[j] + beta_[j]) for j in _touched if j != m_t)
            if exito: alpha[m_t] += 1
            else: beta_[m_t] += 1
            _cost += 1.0 / (alpha[m_t] + beta_[m_t])
            consumo += _cost
            ejecutor.append(m_t)
            long_cadena.append(len(cadena_t))
            psd.append(1.0 if exito else 0.0)
        return dict(ejecutor=ejecutor, long_cadena=long_cadena, psd=psd, r_final=dict(r))

    DEC_ROOT_CMP = DEC_ROOT  # alias, kept so comparison_display's existing references still work
    DEC_SEED_CMP = DEC_SEED
    dec_full_result = _dec_full_run(DEC_ROOT_CMP, DEC_SEED_CMP, K=1100.0)  # K sized for root=W3's cost trajectory (~1011 at t=1000)
    return DEC_ROOT_CMP, dec_full_result


@app.cell
def dec_problematisacion(
    ACTOR_IDS,
    DEC_ROOT_CMP,
    dec_full_result,
    desempeno,
    mo,
    n,
    np,
):

    _dec_cnt = np.bincount(dec_full_result["ejecutor"], minlength=n)
    _dec_top = int(np.argmax(_dec_cnt))
    _dec_share = _dec_cnt[_dec_top] / len(dec_full_result["ejecutor"])
    _dec_zero = [ACTOR_IDS[i] for i in range(n) if _dec_cnt[i] == 0]

    mo.md(f"""
    **Lo que DEC nos enseña:** a diferencia de UCB1 y DIG, DEC no compara el desempeño de delegatarios
    individuales — forma una coalición (CFORM) y usa el valor de Myerson
    (Shapley sobre componentes conexas, Def. 3–4 de Afanador/Oren/Baptista 2019)
    para clasificarlos y elegir quién recibe la tarea territorial. Pero ese valor
    decide *solo eso*, quién gana la comparación — no cuánto recibe nadie. La
    recompensa real la fija una regla aparte, inversamente proporcional a la
    posición en la cadena (`r_m = pos_m·o_m/H_k`, una regla de distribución de los beneficios territoriales).
    Σφᵢ = v(N) es, en
    efecto, un teorema — pero de la función característica,
    ν(D) = Σ E[oᵢ] (Def. 2), puramente aditiva: sin sinergia entre agentes, el
    valor de Shapley/Myerson de cada jugador es *exactamente* su aporte
    individual (φᵢ = rᵢ, verificado aquí numéricamente en 500 ensayos,
    diferencia de punto flotante). El resultado tiene soporte teórico; lo que
    no describe es un reparto — describe las propiedades matemáticas de una
    interacción que sin estar predeterminada por el comportamiento colectivo es conducente a
    formas de cooperación.

    **Lo que DEC problematiza:** el episodio recorrido en el seguimiento
    (`W3→W2→W0→W2`, raíz W3) muestra que **DEL no lleva un conjunto de
    visitados** — a diferencia de DIG, el mismo actor (W2) puede ser convocado a
    decidir dos veces en una sola cadena, sin que el algoritmo lo note como
    ciclo. A escala completa, esta corrida arranca en {ACTOR_IDS[DEC_ROOT_CMP]}
    ({len(dec_full_result['ejecutor'])} episodios) — y la misma ausencia de
    memoria estructural produce aquí el resultado inverso al de la raíz W0:
    como {ACTOR_IDS[DEC_ROOT_CMP]} está topológicamente lejos de EC (el único
    puente hacia EM), la cascada simplemente nunca alcanza esa rama de la red.
    Concentra **{_dec_share:.0%}** de las ejecuciones en **{ACTOR_IDS[_dec_top]}**
    (incidencia {desempeno[_dec_top]:.3f}), mientras {', '.join(_dec_zero)} nunca
    ejecutan ni una vez en esta corrida — la raíz misma, {ACTOR_IDS[DEC_ROOT_CMP]},
    tampoco autoejecuta (por diseño, delegar siempre resulta al menos
    tan bueno como ejecutar directamente). El mecanismo es idéntico al de la raíz W0, cuando la injerencia territorial se concentraba en torno a EC
    (incidencia {desempeno[5]:.3f}, la más baja entre los seis con argumento):
    La ceguera estructural
    de DEC no cambia entre una raíz y otra — solo cambia si esa ceguera termina
    premiando o castigando, según quien origine la acción sobre el territorio.
    """)
    return


@app.cell
def comparison_metrics(
    dec_full_result,
    desempeno,
    dig_episodes,
    n,
    np,
    ucb1_full_result,
):

    ventana_cmp = 50

    def _gini(x):
        x = np.asarray(x, dtype=float)
        if x.sum() == 0: return 0.0
        x = np.sort(x)
        nx = len(x); cum = np.cumsum(x)
        return float((nx + 1 - 2 * np.sum(cum) / cum[-1]) / nx)

    # ── UCB1 ───────────────────────────────────────────────────────────────────
    ucb1_t_real   = ucb1_full_result["t_real"]
    ucb1_hist_i   = ucb1_full_result["hist_i"]
    ucb1_hist_r   = ucb1_full_result["hist_r"]
    ucb1_mejor    = desempeno.max()
    ucb1_regret_h = np.cumsum(ucb1_mejor - desempeno[ucb1_hist_i])
    ucb1_mu_roll  = np.convolve(ucb1_hist_r, np.ones(ventana_cmp) / ventana_cmp, mode="valid")
    ucb1_lc       = np.ones(ucb1_t_real)

    # ── DIG ────────────────────────────────────────────────────────────────────
    dig_t_real    = len(dig_episodes)
    dig_ejec_h    = np.array([_ep["ejecutor"] for _ep in dig_episodes])
    dig_res_h     = np.array([_ep["resultado"] for _ep in dig_episodes], dtype=float)
    dig_lc        = np.array([len(_ep["cadena"]) for _ep in dig_episodes])
    dig_regret_h  = np.cumsum(ucb1_mejor - desempeno[dig_ejec_h])
    dig_mu_roll   = np.convolve(dig_res_h, np.ones(ventana_cmp) / ventana_cmp, mode="valid")

    # ── DEC ────────────────────────────────────────────────────────────────────
    dec_ejec_h    = np.array(dec_full_result["ejecutor"])
    dec_psd_h     = np.array(dec_full_result["psd"])
    dec_lc        = np.array(dec_full_result["long_cadena"])
    dec_regret_h  = np.cumsum(ucb1_mejor - desempeno[dec_ejec_h])
    dec_mu_roll   = np.convolve(dec_psd_h, np.ones(ventana_cmp) / ventana_cmp, mode="valid")

    # ── Gini sobre la variable de valor NATIVA de cada mecanismo (no sobre conteos
    # de éxito) — cada una es exactamente lo que el propio algoritmo consulta al
    # decidir, sin descomposición externa. UCB1 no tiene una "creencia" aislable
    # de su criterio real (mu+cota mezcla valor con un término de exploración
    # ligado a visitas, no a recompensa), así que usa su acumulador de recompensa
    # bruto (post-calentamiento). DIG y DEC sí tienen una variable de creencia/
    # valor final referenciada directamente por sus propias fórmulas de decisión.
    _ex_ucb1 = np.array([ucb1_hist_r[n:][ucb1_hist_i[n:] == i].sum() for i in range(n)])
    gini_ucb1 = _gini(_ex_ucb1)

    _alpha_dig_final = {i: 1.0 for i in range(n)}
    _beta_dig_final  = {i: 1.0 for i in range(n)}
    for _ep in dig_episodes:
        for _ag in _ep["cadena"]:
            if _ep["resultado"] > 0: _alpha_dig_final[_ag] += 1
            else: _beta_dig_final[_ag] += 1
    _mu_dig_final = np.array([_alpha_dig_final[i] / (_alpha_dig_final[i] + _beta_dig_final[i]) for i in range(n)])
    gini_dig = _gini(_mu_dig_final)

    _r_dec_final = np.array([dec_full_result["r_final"][i] for i in range(n)])
    gini_dec = _gini(_r_dec_final)

    coop_ucb1 = 0.0
    coop_dig  = float((dig_lc >= 2).mean() * 100)
    coop_dec  = float((dec_lc >= 2).mean() * 100)

    return (
        coop_dec,
        coop_dig,
        coop_ucb1,
        dec_ejec_h,
        dec_lc,
        dec_mu_roll,
        dec_psd_h,
        dec_regret_h,
        dig_lc,
        dig_mu_roll,
        dig_regret_h,
        dig_t_real,
        gini_dec,
        gini_dig,
        gini_ucb1,
        ucb1_lc,
        ucb1_mu_roll,
        ucb1_regret_h,
        ucb1_t_real,
        ventana_cmp,
    )


@app.cell
def comparison_display(
    ACTOR_IDS,
    DEC_ROOT_CMP,
    DIG_ROOT_CMP,
    DIG_SEED_CMP,
    GRAY,
    PARAMO,
    TIERRA,
    UNAL,
    coop_dec,
    coop_dig,
    coop_ucb1,
    dec_ejec_h,
    dec_lc,
    dec_mu_roll,
    dec_psd_h,
    dec_regret_h,
    desempeno,
    dig_lc,
    dig_mu_roll,
    dig_regret_h,
    dig_t_real,
    gini_dec,
    gini_dig,
    gini_ucb1,
    mo,
    n,
    np,
    plt,
    ucb1_lc,
    ucb1_mu_roll,
    ucb1_regret_h,
    ucb1_t_real,
    ventana_cmp,
):

    import matplotlib.gridspec as _gridspec

    fig_cmp = plt.figure(figsize=(14, 10))
    _gs_out = _gridspec.GridSpec(2, 2, figure=fig_cmp, hspace=0.38, wspace=0.32)

    _ax = fig_cmp.add_subplot(_gs_out[0, 0])
    _ax.plot(np.arange(ventana_cmp, ucb1_t_real + 1), ucb1_mu_roll, color=GRAY, lw=2, label="UCB1")
    _ax.plot(np.arange(ventana_cmp, dig_t_real + 1),  dig_mu_roll,  color=TIERRA, lw=2, label="DIG")
    _ax.plot(np.arange(ventana_cmp, len(dec_psd_h) + 1), dec_mu_roll, color=PARAMO, lw=2, label="DEC")
    _ax.set_ylim(0, 1); _ax.legend(fontsize=8, loc="lower right")
    _ax.set_xlabel("Ronda/episodio t"); _ax.set_ylabel(f"Tasa de exito (ventana={ventana_cmp})")
    _ax.set_title("Tasa de exito", color=UNAL, fontsize=11)

    _ax2 = fig_cmp.add_subplot(_gs_out[0, 1])
    _ax2.plot(np.arange(1, ucb1_t_real + 1), ucb1_regret_h, color=GRAY, lw=2, label="UCB1")
    _ax2.plot(np.arange(1, dig_t_real + 1),  dig_regret_h,  color=TIERRA, lw=2, label="DIG")
    _ax2.plot(np.arange(1, len(dec_regret_h) + 1), dec_regret_h, color=PARAMO, lw=2, label="DEC")
    _t_ref = np.arange(1, ucb1_t_real + 1)
    _ax2.plot(_t_ref, np.log(_t_ref + 1) * ucb1_regret_h[-1] / np.log(ucb1_t_real + 1),
              color=GRAY, lw=1.2, linestyle=":", label="O(log T)")
    _ax2.legend(fontsize=8); _ax2.set_xlabel("Ronda/episodio t")
    _ax2.set_ylabel("Arrepentimiento acumulado")
    _ax2.set_title("Arrepentimiento", color=UNAL, fontsize=11)

    _ax3 = fig_cmp.add_subplot(_gs_out[1, 0])
    for _lc, _col, _lbl, _ls in [(ucb1_lc, GRAY, "UCB1", "-"), (dig_lc, TIERRA, "DIG", "-"),
                                  (dec_lc, PARAMO, "DEC", "-")]:
        _mm = np.convolve(_lc, np.ones(ventana_cmp) / ventana_cmp, mode="valid")
        _ax3.plot(np.arange(ventana_cmp, len(_lc) + 1), _mm, color=_col, lw=2, linestyle=_ls, label=_lbl)
    _ax3.legend(fontsize=8); _ax3.set_xlabel("Ronda/episodio t")
    _ax3.set_ylabel(f"Largo de cadena (ventana={ventana_cmp})")
    _ax3.set_title("Largo de cadena de delegacion", color=UNAL, fontsize=11)

    _gs_in = _gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=_gs_out[1, 1], hspace=0.65, height_ratios=[1, 1])
    _ax4a = fig_cmp.add_subplot(_gs_in[0])
    _ax4b = fig_cmp.add_subplot(_gs_in[1])

    _mecs = ["UCB1", "DIG", "DEC"]
    _cs = [GRAY, TIERRA, PARAMO]
    _gs_v = [gini_ucb1, gini_dig, gini_dec]
    _ax4a.bar(_mecs, _gs_v, color=_cs, edgecolor="white", lw=1.0)
    _ax4a.axhline((n - 1) / n, color="#B23A48", lw=1.2, linestyle="--", label=f"max. = {(n-1)/n:.3f}")
    _ax4a.set_ylim(0, 1); _ax4a.legend(fontsize=7)
    _ax4a.set_ylabel("Gini", fontsize=9)
    _ax4a.set_title("Concentracion de la variable de valor nativa (arriba = mas concentrado)", color=UNAL, fontsize=9)
    for _i, _g in enumerate(_gs_v):
        _ax4a.text(_i, _g + 0.035, f"{_g:.3f}", ha="center", fontsize=8, fontweight="bold")

    _coops = [coop_ucb1, coop_dig, coop_dec]
    _ax4b.bar(_mecs, _coops, color=_cs, edgecolor="white", lw=1.0)
    _ax4b.set_ylim(0, 118)
    _ax4b.set_ylabel("% episodios", fontsize=9)
    _ax4b.set_title("Activacion cooperativa >=2 actores (arriba = mas colaborativo)", color=UNAL, fontsize=9)
    for _i, _c in enumerate(_coops):
        _ax4b.text(_i, _c + 2.5, f"{_c:.1f}%", ha="center", fontsize=8, fontweight="bold")

    fig_cmp.suptitle("Cuatro metricas — exito, arrepentimiento, largo de cadena, concentracion vs. cooperacion",
                      fontsize=11, color=UNAL, y=1.01)

    _dec_counts_note = np.bincount(dec_ejec_h, minlength=n)
    _dec_top_note = int(np.argmax(_dec_counts_note))
    _dec_share_note = _dec_counts_note[_dec_top_note] / len(dec_ejec_h)
    _dig_self_exec_note = float((dig_lc == 1).mean())

    _ucb1_win_nota = mo.callout(mo.md(f"""
    **¿Por que DIG y DEC ganan aqui? — y ¿por qué no es un resultado universal?** Esta corrida
    arranca DIG en {ACTOR_IDS[DIG_ROOT_CMP]} y DEC en {ACTOR_IDS[DEC_ROOT_CMP]}, con semilla
    {DIG_SEED_CMP} para los tres mecanismos. No son raices arbitrarias: un barrido de 2000
    semillas x 7 raices muestra que DIG solo supera a UCB1 (éxito y arrepentimiento a la vez)
    partiendo de {ACTOR_IDS[DIG_ROOT_CMP]} o W2 — las dos raices de mayor incidencia — y DEC
    solo lo supera partiendo de W3 o W4 — las dos raices topologicamente mas lejanas de EC.
    Nunca ambas desde la misma raiz. 

    **DIG:** la fórmula de intensidad de delegacion `x_ij = (r_i1-r_i0)/(r_ij-mu_j)` es la
    misma de siempre — el denominador se acerca a cero cuando la incidencia territorial está
    agrupada en valores altos, introduciendo ruido en la decisión. En esta corrida, DIG autoejecuta
    en el **{_dig_self_exec_note:.1%}** de los episodios. La diferencia frente a partir de W0
    no es que la formula se haya estabilizado — es que autoejecutar en
    {ACTOR_IDS[DIG_ROOT_CMP]} (incidencia {desempeno[DIG_ROOT_CMP]:.3f}, la más alta en la
    red) es la mejor decision posible. La misma inestabilidad que hundía a DIG en W0 aqui es
    inofensiva.

    **DEC:** el mecanismo es idéntico al de la raiz W0 — la cascada de coalición nunca
    consulta la incidencia territorial para decidir quién ejecuta, solo la posición en la red.
    Desde {ACTOR_IDS[DEC_ROOT_CMP]}, esa ceguera estructural nunca alcanza a EC/EM
    (topologicamente lejos): concentra **{_dec_share_note:.0%}** de las ejecuciones en
    **{ACTOR_IDS[_dec_top_note]}** (incidencia {desempeno[_dec_top_note]:.3f}). Desde W0, la
    misma ceguera concentraba en EC (incidencia {desempeno[5]:.3f}, la mas baja).

    **Lo que esto no prueba:** que DIG o DEC sean "mejores" que UCB1 en general. Prueba que su
    sensibilidad estructural — a diferencia del muestreo plano de UCB1, que no depende de
    ningun punto de partida — tiene efectos importantes según donde arranque la cascada.
    """), kind="warn")

    _gini_warn = mo.callout(mo.md(f"""
    **¿Qué mide este Gini? — una variable de recompensa NATIVA a cada mecanismo, diferente
    a conteos de exito:** cada barra usa exactamente la cantidad que ese algoritmo
    consulta al decidir. **UCB1** no tiene una
    creencia aislable de su criterio de asignación (`mu+cota` mezcla valor con un término
    de exploración ligado a visitas, no a recompensa) — usa su acumulador de
    recompensa bruto post-calentamiento (`suma_i`). **DIG** usa la creencia final
    `mu_j = alpha_j/(alpha_j+beta_j)` — la misma cantidad que cualquier otro
    agente consulta al evaluar a j como candidato. **DEC** usa el `r_i` final —
    la misma cantidad que su comparacion argmax lee directamente.

    **Resultado:** DIG **{gini_dig:.3f}**, DEC **{gini_dec:.3f}**, UCB1
    **{gini_ucb1:.3f}**. DIG tiene la
    creencia final mas equitativa de los tres — su actualización de reputación
    alcanza a TODOS los actores de cada cadena, no solo a quien ejecuta, así que
    la creencia final refleja cuantas cadenas pasaron por cada actor, no sólo
    cuantas veces ejecuto. DEC queda en el intermedio: `r` se redibuja con un muestreo
    Uniforme acotado cada vez que alguien gana, asi que no se acumula sin limite
    como un conteo — pero W3/EC/EM no ganan ni una vez en esta corrida, así
    que su `r` nunca se actualiza desde la asignacion inicial. UCB1 muestra mayor
    concentracion que DIG/DEC porque `suma_i` es un conteo bruto que se acumula
    sin limite en los brazos mas visitados.

    *Activación cooperativa* (% episodios con >=2 actores en la cadena): **UCB1: 0%** — un solo brazo por episodio, por definicion. **DIG y DEC** involucran multiples actores por
    episodio, pero por mecanismos distintos: DIG se detiene cuando la confianza
    delegada supera el umbral; DEC siempre delega desde la raiz salvo que la raiz
    misma gane su propia comparación Myerson.
    """), kind="warn")

    _comparacion_detalle = mo.accordion({
        "¿Por qué DIG y DEC ganan aquí?": _ucb1_win_nota,
        "¿Qué mide este Gini?": _gini_warn,
    })

    mo.vstack([fig_cmp, _comparacion_detalle])
    return


@app.cell
def aaf_data():

    ATAQUES_ARG = {
        "A1_delimitacion":    ["A4_comunidad"],
        "A2_concesion":       ["A4_comunidad", "A5_bachue_iguaque", "A3_hidrologico", "A6_cosmo_serpiente"],
        "A3_hidrologico":     ["A1_delimitacion"],
        "A4_comunidad":       ["A1_delimitacion", "A2_concesion"],
        "A5_bachue_iguaque":  ["A2_concesion"],
        "A6_cosmo_serpiente": ["A2_concesion"],
    }
    # A2 (concesión) también ataca A3 (hidrológico) y A6 (cosmológico): una concesión
    # minera necesita descalificar tanto la preocupación hidrológica como el reclamo
    # territorial cosmológico, no solo a la comunidad (A4) y a Bachué (A5).
    ARG_IDS = [
        "A1_delimitacion", "A2_concesion", "A3_hidrologico",
        "A4_comunidad", "A5_bachue_iguaque", "A6_cosmo_serpiente",
    ]
    ARG_ACTOR = {
        "A1_delimitacion": "Estado colombiano (EC)",
        "A2_concesion": "Empresa de materiales (EM)",
        "A3_hidrologico": "Manejo Comunitario del Agua (W1)",
        "A4_comunidad": "Comunidades campesinas paramunas (W0)",
        "A5_bachue_iguaque": "Pueblo Muisca (W4)",
        "A6_cosmo_serpiente": "Pueblo Muisca (W4)",
    }
    return ARG_ACTOR, ARG_IDS, ATAQUES_ARG


@app.cell
def aaf_dung_pure(ARG_IDS, ATAQUES_ARG):

    import itertools

    def _atacantes_de(x, atk):
        return [s for s, ts in atk.items() if x in ts]

    def _libre_de_conflicto(S, atk):
        return not any(b in atk.get(a, []) for a in S for b in S if a != b)

    def _defiende(S, x, atk):
        return all(any(d in atk.get(s, []) for s in S) for d in _atacantes_de(x, atk))

    def _extension_fundamentada(nodos, atk):
        S = set()
        cambio = True
        while cambio:
            cambio = False
            for x in nodos:
                if x not in S and _defiende(S, x, atk) and _libre_de_conflicto(S | {x}, atk):
                    S.add(x); cambio = True
        return S

    def _conjuntos_admisibles(nodos, atk):
        nodos = list(nodos)
        res = []
        for r in range(len(nodos) + 1):
            for combo in itertools.combinations(nodos, r):
                S = set(combo)
                if _libre_de_conflicto(S, atk) and all(_defiende(S, x, atk) for x in S):
                    res.append(S)
        return res

    def _extensiones_preferidas(nodos, atk):
        adm = _conjuntos_admisibles(nodos, atk)
        maxi = [s for s in adm if not any(s < t for t in adm)]
        uniq = []
        for s in maxi:
            if s not in uniq:
                uniq.append(s)
        return uniq

    _g_aaf   = _extension_fundamentada(ARG_IDS, ATAQUES_ARG)
    _out_aaf = {x for x in ARG_IDS if any(x in ATAQUES_ARG.get(s, []) for s in _g_aaf)} - _g_aaf
    _undec_aaf = set(ARG_IDS) - _g_aaf - _out_aaf
    _pref_aaf = _extensiones_preferidas(ARG_IDS, ATAQUES_ARG)

    aaf_grounded_in = _g_aaf
    aaf_grounded_out = _out_aaf
    aaf_grounded_undec = _undec_aaf
    aaf_preferred = _pref_aaf
    return (aaf_preferred,)


@app.cell
def aaf_dung_display(
    ARG_ACTOR,
    ARG_IDS,
    ATAQUES_ARG,
    BSTATE,
    PARAMO,
    UNAL,
    aaf_preferred,
    mo,
    mpatches,
    np,
    plt,
    sbm36_blocks,
    sbm36_edges,
    sbm36_nblocks,
    sbm36_ntypes,
    sbm36_palette,
    sbm36_pos,
    sbm36_type_order,
):
    _ARG_POS = {
        "A3_hidrologico":     np.array([-4.2,  1.4]),
        "A4_comunidad":       np.array([-1.5,  1.4]),
        "A5_bachue_iguaque":  np.array([ 1.5,  1.4]),
        "A6_cosmo_serpiente": np.array([ 4.2,  1.4]),
        "A1_delimitacion":    np.array([-1.5, -1.6]),
        "A2_concesion":       np.array([ 1.5, -1.6]),
    }

    _fig_aaf, _ax_aaf = plt.subplots(figsize=(11, 6))
    _fig_aaf.patch.set_facecolor("#f8f9fa")
    _ax_aaf.set_facecolor("#f8f9fa")

    for _src, _tgts in ATAQUES_ARG.items():
        for _tgt in _tgts:
            _mutual = _src in ATAQUES_ARG.get(_tgt, [])
            _rad = 0.15 if _mutual else 0.08
            _ax_aaf.annotate("", xy=tuple(_ARG_POS[_tgt]), xytext=tuple(_ARG_POS[_src]),
                arrowprops=dict(arrowstyle="-|>", color=BSTATE, lw=2.6, alpha=0.9,
                                 shrinkA=50, shrinkB=50, mutation_scale=26,
                                 connectionstyle=f"arc3,rad={_rad}"), zorder=2)

    _pref_comunidad = next(p for p in aaf_preferred if "A4_comunidad" in p)
    _pref_extractivo = next(p for p in aaf_preferred if "A4_comunidad" not in p)
    _ext_txt = ", ".join(sorted(x.split("_")[0] for x in _pref_extractivo))
    _com_txt = ", ".join(sorted(x.split("_")[0] for x in _pref_comunidad))

    for _aid in ARG_IDS:
        _x, _y = _ARG_POS[_aid]
        _fc = PARAMO if _aid in _pref_comunidad else BSTATE
        _ax_aaf.add_patch(mpatches.RegularPolygon((_x, _y), numVertices=4, radius=0.52,
                                       orientation=0, facecolor=_fc, alpha=0.85,
                                       edgecolor="white", lw=1.5, zorder=3))
        _ax_aaf.text(_x, _y, _aid.split("_")[0], ha="center", va="center",
                     fontsize=11, color="white", fontweight="bold", zorder=4)
        _lab_dy, _lab_va = (0.62, "bottom") if _y > 0 else (-0.62, "top")
        _ax_aaf.text(_x, _y + _lab_dy, ARG_ACTOR[_aid], ha="center", va=_lab_va,
                     fontsize=7.6, color="#333", zorder=4)

    _ax_aaf.text(0, 2.42, f"extensión preferida {{{_com_txt}}} — comunidad · ciencia · cosmología",
                 ha="center", va="bottom", fontsize=10, color=PARAMO, fontweight="bold", zorder=4)
    _ax_aaf.text(0, -2.52, f"extensión preferida {{{_ext_txt}}} — bloque extractivo",
                 ha="center", va="top", fontsize=10, color=BSTATE, fontweight="bold", zorder=4)

    # derivacion de admisibilidad, CALCULADA sobre la relacion real (no escrita a mano)
    def _atacantes_de(x, atk):
        return [s for s, ts in atk.items() if x in ts]
    def _libre_de_conflicto(S, atk):
        return not any(b in atk.get(a, []) for a in S for b in S if a != b)

    _short = lambda z: z.split("_")[0]
    _ext_orden = [("extractiva", _pref_extractivo),
                  ("comunidad-ciencia-cosmología", _pref_comunidad)]
    _deriv_lines = [
        "DEFINICIONES (Dung 1995)",
        "  libre-de-conflicto(S) : ningún a,b in S con a -> b",
        "  S defiende a          : para cada atacante b de a, existe c in S con c -> b",
        "  admisible(S)          : libre-de-conflicto(S) y S defiende a cada a in S",
        "",
    ]
    for _nom, _S in _ext_orden:
        _Ss = sorted(_S, key=_short)
        _deriv_lines.append("EXTENSION " + _nom.upper() + "  =  {" + ", ".join(_short(x) for x in _Ss) + "}")
        _deriv_lines.append("  [1] libre de conflicto:")
        _pares = [_short(a) + "-" + _short(b) for _i, a in enumerate(_Ss) for b in _Ss[_i + 1:]]
        _deriv_lines.append("      pares: " + ", ".join(_pares))
        _deriv_lines.append("      -> ningún miembro ataca a otro  "
                            + ("OK" if _libre_de_conflicto(set(_Ss), ATAQUES_ARG) else "CONFLICTO"))
        _deriv_lines.append("  [2] defensa (cada atacante contraatacado desde dentro de la extension):")
        for _x36 in _Ss:
            _atk = _atacantes_de(_x36, ATAQUES_ARG)
            if not _atk:
                _deriv_lines.append("      " + _short(_x36) + ": sin atacantes (defensa trivial)")
                continue
            for _d in _atk:
                _defs = [s for s in _Ss if _d in ATAQUES_ARG.get(s, [])]
                _deriv_lines.append("      " + _short(_x36) + " <- " + _short(_d)
                                    + "   contraatacado por {" + ", ".join(_short(s) for s in _defs) + "}")
        _deriv_lines.append("  => admisible, y maximal (no admite otro argumento sin conflicto)")
        _deriv_lines.append("")

    _aaf_deriv = mo.md(
        "**Computo de admisibilidad — semántica de Dung (1995), verificada sobre la relación real de ataque**\n\n"
        "<pre style=\"background:#f4f4f4;padding:12px;border-radius:4px;font-size:12.5px;line-height:1.45;overflow-x:auto\">"
        + "\n".join(_deriv_lines) + "</pre>")



    _ax_aaf.set_xlim(-5.3, 5.3); _ax_aaf.set_ylim(-3.1, 3.0)
    _ax_aaf.set_aspect("equal"); _ax_aaf.axis("off")
    _ax_aaf.set_title("AAF de Dung (1995) sobre los 6 argumentos — dos extensiones preferidas en pugna",
                       fontsize=12.5, color=UNAL, fontweight="bold")
    plt.tight_layout()

    _aaf_nota = mo.callout(mo.md(f"""
    **Desempeño y argumentación.** `desempeño` — la variable de referencia para UCB1, DIG y DEC 
    durante la clase que dí por llamar "incidencia territorial" — no es exógena: salió de una métrica 
    para la cuantificación de estructura argumentativa σ* por (Libman, Oren & Yun 2024), calculado sobre
    esta misma red de ataques.

    **Dung clásico, es decir criterios cualitativos para la evaluación de estructura argumentativa no decide esta red.**
    La extension fundamentada (escéptica) nos deja indecisos sobre los seis argumentos: ninguno está libre de ataque. La semántica
    preferida parte el grafo en dos extensiones máximas, mutuamente excluyentes —
    **{{{_ext_txt}}}** (bloque extractivo) frente a **{{{_com_txt}}}** (comunidad,
    ciencia ambiental, cosmologia muisca) — sin criterio para elegir entre ellas.

    **σ* no elige: gradúa.** Le da a cada argumento un numero continuo de
    supervivencia bajo ataque real, y ese número fue nuestro `desempeño` desde la primera
    diapositiva. El MAB nunca supo que su insumo tenía esta historia detrás.
    """), kind="success")

    _aaf_apertura = mo.accordion({"Desempeño y argumentación": _aaf_nota})


    import plotly.graph_objects as _pgo
    import matplotlib.colors as _mcolors36

    _xs36 = sbm36_pos[:, 0]
    _ys36 = sbm36_pos[:, 1]
    _z36 = sbm36_blocks.astype(float)
    _Xp36, _Yp36 = np.meshgrid(
        np.linspace(_xs36.min() - 0.4, _xs36.max() + 0.4, 6),
        np.linspace(_ys36.min() - 0.4, _ys36.max() + 0.4, 6))

    _pgo_3d = _pgo.Figure()

    for _b in range(sbm36_nblocks):
        _bc36 = sbm36_palette[_b % len(sbm36_palette)]
        _pgo_3d.add_trace(_pgo.Surface(
            x=_Xp36, y=_Yp36, z=np.full_like(_Xp36, float(_b), dtype=float),
            surfacecolor=np.zeros_like(_Xp36),
            colorscale=[[0, _bc36], [1, _bc36]], cmin=0, cmax=1,
            showscale=False, opacity=0.12, showlegend=False, hoverinfo="skip"))

    for _b in range(sbm36_nblocks):
        _bix36, _biy36, _biz36 = [], [], []
        for _u, _v in sbm36_edges:
            if int(sbm36_blocks[_u]) == _b and int(sbm36_blocks[_v]) == _b:
                _bix36 += [float(_xs36[_u]), float(_xs36[_v]), None]
                _biy36 += [float(_ys36[_u]), float(_ys36[_v]), None]
                _biz36 += [float(_z36[_u]), float(_z36[_v]), None]
        if _bix36:
            _R36, _G36, _Bv36, _ = _mcolors36.to_rgba(sbm36_palette[_b % len(sbm36_palette)])
            _pgo_3d.add_trace(_pgo.Scatter3d(
                x=_bix36, y=_biy36, z=_biz36, mode="lines",
                line=dict(color=f"rgba({int(_R36*255)},{int(_G36*255)},{int(_Bv36*255)},0.20)", width=1),
                showlegend=False, hoverinfo="none"))

    _ex_inter36, _ey_inter36, _ez_inter36 = [], [], []
    for _u, _v in sbm36_edges:
        if int(sbm36_blocks[_u]) != int(sbm36_blocks[_v]):
            _ex_inter36 += [float(_xs36[_u]), float(_xs36[_v]), None]
            _ey_inter36 += [float(_ys36[_u]), float(_ys36[_v]), None]
            _ez_inter36 += [float(_z36[_u]), float(_z36[_v]), None]
    _n_inter36 = len(_ex_inter36) // 3
    _n_intra36 = sum(1 for _u, _v in sbm36_edges if sbm36_blocks[_u] == sbm36_blocks[_v])
    if _ex_inter36:
        _pgo_3d.add_trace(_pgo.Scatter3d(x=_ex_inter36, y=_ey_inter36, z=_ez_inter36, mode="lines",
            line=dict(color="rgba(30,30,30,0.32)", width=1.8),
            name="inter-bloque", showlegend=True, hoverinfo="none"))

    _basal36 = list(range(sbm36_ntypes))
    _variant36 = list(range(sbm36_ntypes, 36))
    _pgo_3d.add_trace(_pgo.Scatter3d(
        x=[float(_xs36[_ni]) for _ni in _basal36], y=[float(_ys36[_ni]) for _ni in _basal36],
        z=[float(_z36[_ni]) for _ni in _basal36], mode="markers+text",
        marker=dict(size=11, symbol="diamond",
                    color=[sbm36_palette[int(sbm36_blocks[_ni]) % len(sbm36_palette)] for _ni in _basal36],
                    line=dict(color="white", width=0.5)),
        text=[sbm36_type_order[_ni].split("_")[0] for _ni in _basal36],
        textposition="top center", textfont=dict(size=9, color="#111"),
        name="argumentos base", showlegend=True))
    _pgo_3d.add_trace(_pgo.Scatter3d(
        x=[float(_xs36[_ni]) for _ni in _variant36], y=[float(_ys36[_ni]) for _ni in _variant36],
        z=[float(_z36[_ni]) for _ni in _variant36], mode="markers",
        marker=dict(size=6, symbol="diamond",
                    color=[sbm36_palette[int(sbm36_blocks[_ni]) % len(sbm36_palette)] for _ni in _variant36],
                    line=dict(color="white", width=0.4)),
        name="variantes", showlegend=True))

    _pgo_3d.update_layout(
        height=620,
        scene=dict(
            xaxis=dict(visible=False, showgrid=False), yaxis=dict(visible=False, showgrid=False),
            zaxis=dict(title=dict(text="mesoestructura", font=dict(size=11, color="#333")),
                       tickvals=list(range(sbm36_nblocks)), tickfont=dict(size=9, color="#222")),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.9)),
            aspectmode="manual", aspectratio=dict(x=1.0, y=1.0, z=2.6),
            bgcolor="#f8f9fa"),
        title=dict(text=f"Los 36 argumentos, {sbm36_nblocks} mesoestructuras SBM<br>"
                        f"<sup>intra: {_n_intra36}  ·  inter: {_n_inter36}</sup>",
                   font=dict(size=12, color=UNAL)),
        legend=dict(x=1.01, y=0.5, xanchor="left", yanchor="middle",
                    bgcolor="rgba(255,255,255,0.96)", bordercolor="#aaa", borderwidth=1,
                    font=dict(size=11, color="#111")),
        margin=dict(l=0, r=120, b=0, t=55),
        paper_bgcolor="#f8f9fa")
    import base64 as _b64_3d
    _png3d_bytes = _pgo_3d.to_image(format="png", width=900, height=620, scale=2)
    _png3d_b64 = _b64_3d.b64encode(_png3d_bytes).decode()
    _sbm3d_ui = mo.Html(
        '<div style="width:100%;margin:auto">'
        f'<img src="data:image/png;base64,{_png3d_b64}" style="width:100%;border-radius:4px"/>'
        '</div>')

    _aaf_thesis = mo.callout(mo.md(r"""
    ¿Y la IA en crowdsourcing? No dictamina `desempeño` como un oraculo — genera
    argumentos. Los 30 variantes que crecieron por tema en la apertura, y que el
    SBM confirma arriba, son justo eso: lo que una IA produciría si parafraseara
    cada posicion base. Frente a esa proliferación, lo justo no es asignarle a
    cada argumento nuevo una expectativa de recompensa externa y ad-hoc — como
    hizo el MAB con `desempeno` toda la clase — sino evaluarlo por su contenido
    dialógico y territorial: quién lo ataca, a quien defiende, donde sobrevive en
    la red real. Esa evaluación relacional es exactamente lo que hace σ*: la
    semántica gradual, no el MAB, es la herramienta que le corresponde a la IA en
    este territorio.
    """), kind="success")

    _aaf_cierre = mo.accordion({
        "¿Y la IA en crowdsourcing?": _aaf_thesis,
        "Detalle: computo de admisibilidad (Dung 1995) — para preguntas": _aaf_deriv,
    })

    mo.vstack([_fig_aaf, _aaf_apertura, _sbm3d_ui, _aaf_cierre])
    return


@app.cell
def conclusiones_display(mo):
    _concl_ucb1 = mo.md(r"""
    UCB1 explora y converge de manera óptima sobre `desempeño` — pero jamás
    pregunta qué es ese número ni de dónde sale. En un proceso real de
    delimitación del páramo, tratar la "incidencia territorial" de cada actor
    como un dato exógeno equivale a aceptar sin auditoría quién tiene voz
    válida: sea que ese número venga de un sorteo arbitrario o de una historia
    argumentativa (como vimos al cierre), UCB1 correría idéntico. Su
    eficiencia es comprobada; su ceguera a la procedencia del número, también.
    """)

    _concl_dig = mo.md(r"""
    La cascada de delegación de DIG parece más situada que la comparación plana
    de UCB1 — cada nodo consulta a su vecindario, no sólo a sí mismo. Pero su
    fórmula de intensidad de delegación se vuelve inestable justo cuando la
    incidencia está agrupada en valores altos,
    y solo supera a UCB1 cuando arranca en el actor de mayor incidencia (W1 o
    W2), nunca desde otra raíz. Para la delimitación del páramo esto dice algo
    serio: enrutar autoridad deliberativa a través de relaciones de confianza tiene efectos preferibles
    a los de una comparación plana — pero quien convoca el proceso (la raíz)
    puede decidir el resultado por sí mismo.
    """)

    _concl_dec = mo.md(r"""
    DEC forma coaliciones y calcula valores de Myerson — pero en esta clase
    verificamos que su función característica (ν(D)=Σ E[oᵢ]) es aditiva: 
    sin sinergia entre agentes, el valor de Myerson de cada
    actor es exactamente su propio aporte, lo cual reduce su ímpetu cooperativo.
    Redistribución genuina solo apareció cuando
    inyectamos sinergia a propósito — una prima por diversidad epistémica entre
    registros — y esa corrección redujo el desempeño de los actores. Para el páramo: llamar
    "coalición" o "cooperativo" a un mecanismo no lo hace justo automáticamente;
    la equidad tiene que diseñarse a propósito en lo que el mecanismo premia, y
    ese diseño tiene implicaciones estructurales.
    """)

    _concl_futuro = mo.md(r"""
    **Orientación para trabajo futuro:**  Lo que queda como horizonte es la siguiente
    capa: (1) el filtro BETO/τ, que atenuaría A5/A6 por su distancia al corpus de
    entrenamiento — una medida de familiaridad corporal, no de validez argumentativa
    — y (2) la confirmación topológica: un SBM sobre una
    expansión de 36 nodos (6 argumentos base + variantes) que encuentra las mismas
    mesoestructuras de silenciamiento sin leer una sola palabra de texto. Esa
    versión — Dung → σ* → BETO → SBM completa será el punto de entrada a su trabajo de investigación de final de curso.
    """)

    _conclusiones_accordion = mo.accordion({
        "UCB1 — la eficiencia que nunca pregunta de dónde viene el número": _concl_ucb1,
        "DIG — la delegación relacional que solo funciona si arranca bien": _concl_dig,
        "DEC — coalición no es lo mismo que cooperación": _concl_dec,
        "Orientación para trabajo futuro": _concl_futuro,
    })

    mo.vstack([
        mo.md("## Conclusiones — ¿qué aprendimos de cada mecanismo?, y ¿qué le dice a la delimitación del páramo?"),
        _conclusiones_accordion,
    ])
    return


if __name__ == "__main__":
    app.run()
