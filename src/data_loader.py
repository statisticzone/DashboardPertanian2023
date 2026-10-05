"""Pemuat dan pembersih data (fungsi murni, tanpa Streamlit agar mudah divalidasi)."""
import json

import numpy as np
import pandas as pd
from shapely.geometry import shape

from . import config as C


def nice_name(s: str) -> str:
    """'DI YOGYAKARTA' -> 'DI Yogyakarta', 'ACEH' -> 'Aceh'."""
    s = str(s).strip().title()
    for a, b in (("Dki ", "DKI "), ("Di ", "DI ")):
        if s.startswith(a):
            s = b + s[len(a):]
    return s


def load_geojson(path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_kabkota_geometry(path=C.FILE_GJ_KAB) -> pd.DataFrame:
    """Titik representatif (selalu di dalam poligon) dan bounding box tiap kab/kota."""
    rows = []
    for f in load_geojson(path)["features"]:
        p = f["properties"]
        g = shape(f["geometry"])
        pt = g.representative_point()
        minx, miny, maxx, maxy = g.bounds
        rows.append(dict(
            kode_bps=str(p["kode_bps"]).zfill(4), nama=p.get("nama"),
            provinsi=p.get("provinsi"), kode_prov=str(p["kode_prov"]).zfill(2),
            luas_km2=p.get("luas_km2"), lon=pt.x, lat=pt.y,
            minx=minx, miny=miny, maxx=maxx, maxy=maxy,
        ))
    return pd.DataFrame(rows)


def load_geospasial() -> pd.DataFrame:
    df = pd.read_excel(C.FILE_GEO).rename(columns={"kab-kota": "kabkota"})
    df["kode_bps"] = df["kode_bps"].astype(int).astype(str).str.zfill(4)
    geo = load_kabkota_geometry()
    return df.merge(geo, on="kode_bps", how="left", validate="1:1")


def load_hierarki() -> pd.DataFrame:
    h = pd.read_excel(C.FILE_HIER)
    h["kode_prov"] = h["kode_prov"].astype(int).astype(str).str.zfill(2)
    h["provinsi_nama"] = h["provinsi"].map(nice_name)
    h["pct_gurem"] = np.where(h["jumlah_usaha"] > 0,
                              h["jumlah_gurem"] / h["jumlah_usaha"] * 100, np.nan)
    return h


def load_multivariat() -> pd.DataFrame:
    m = pd.read_excel(C.FILE_MULTI)
    m = m.rename(columns={
        "kode_kab": "kode_prov", "total>=55": "total_krt_55plus",
        "pct_krt_>=55": "pct_krt_55plus", "produktivitas_padi(ku/ha)": "produktivitas_padi",
    })
    m = m.loc[:, ~m.columns.astype(str).str.startswith("Unnamed")]
    m["kode_prov"] = m["kode_prov"].astype(int).astype(str).str.zfill(2)
    m["provinsi_nama"] = m["provinsi"].map(nice_name)
    for c in C.VARS:  # tanda "-" (data tidak tersedia) -> NaN
        m[c] = pd.to_numeric(m[c], errors="coerce")
    return m
