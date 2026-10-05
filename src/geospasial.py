"""Bagian 1 — Visualisasi geospasial (514 kab/kota, 2023).

Peta 1: choropleth % pekerja pertanian (rasio, bukan angka absolut).
Peta 2: proportional symbol (konsumsi beras per kapita, atau jumlah pekerja pertanian).
Kontrol: metode klasifikasi, kontrol layer, fokus provinsi, tooltip, legenda, zoom/pan.
"""
import mapclassify
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.colors import sample_colorscale

from . import config as C
from . import store
from .ui import fmt_dec, show, sumber, tabel, zoom_dari_bounds

METODE = ["Kuantil", "Natural breaks (Jenks)", "Interval sama"]
LYR_CHORO = "Choropleth: % pekerja pertanian"
LYR_SIMBOL = "Proportional symbol"
UKURAN = {
    "Konsumsi beras per kapita (per minggu)": ("konsumsi_beras_mingguan", "Konsumsi beras per kapita per minggu (satuan komoditas BPS)"),
    "Jumlah pekerja pertanian (orang)": ("pertanian", "Jumlah pekerja pertanian (orang)"),
}


def class_edges(values, metode: str, k: int = 5) -> np.ndarray:
    v = np.asarray(values, float)
    if metode == "Kuantil":
        e = np.quantile(v, np.linspace(0, 1, k + 1))
    elif metode.startswith("Natural"):
        e = np.r_[v.min(), mapclassify.NaturalBreaks(v, k=k).bins]
    else:
        e = np.linspace(v.min(), v.max(), k + 1)
    return np.unique(e)


def _korelasi_teks(rho: float) -> str:
    a = abs(rho)
    kuat = "sangat lemah" if a < 0.2 else "lemah" if a < 0.4 else "sedang" if a < 0.6 else "kuat"
    arah = "positif" if rho > 0 else "negatif"
    return f"{kuat} dan {arah}"


def render():
    geo = store.geospasial()
    gj = store.geojson_kab()

    st.markdown("### 🗺️ Seberapa dominan pertanian dalam struktur pekerjaan daerah?")
    st.write(
        "Peta choropleth memperlihatkan **persentase pekerja di sektor pertanian** pada tiap kabupaten/kota. "
        "Peta proportional symbol menambahkan sisi **pangan**: proportional symbol menunjukkan konsumsi beras per kapita. "
    )

    # ---------- Kontrol ----------
    c1, c2, c3 = st.columns(3)
    metode = c1.radio("Metode klasifikasi warna", METODE, help="Cara membagi nilai menjadi 5 kelas warna.")
    layers = c2.multiselect("Lapisan peta (layer)", [LYR_CHORO, LYR_SIMBOL], default=[LYR_CHORO, LYR_SIMBOL])
    ukuran_nama = c3.selectbox("Ukuran simbol", list(UKURAN))
    fokus = st.selectbox("Fokus provinsi (zoom otomatis)", ["Seluruh Indonesia"] + sorted(geo["provinsi"].dropna().unique()))

    if fokus == "Seluruh Indonesia":
        center, zoom = dict(lat=-2.5, lon=118.0), 3.3
    else:
        s = geo[geo["provinsi"] == fokus]
        center, zoom = zoom_dari_bounds(s.minx.min(), s.miny.min(), s.maxx.max(), s.maxy.max())

    # ---------- Kelas choropleth ----------
    edges = class_edges(geo["pct_pertanian"], metode, 5)
    labels = [f"{fmt_dec(edges[i])} – {fmt_dec(edges[i + 1])}%" for i in range(len(edges) - 1)]
    geo = geo.copy()
    geo["kelas"] = pd.cut(geo["pct_pertanian"], bins=edges, labels=labels, include_lowest=True).astype(str)
    warna = sample_colorscale(C.SKALA_PEKERJA, list(np.linspace(0.15, 1.0, len(labels))))
    cmap = dict(zip(labels, warna))

    # ---------- Peta ----------
    if LYR_CHORO in layers:
        fig = px.choropleth_map(
            geo, geojson=gj, locations="kode_bps", featureidkey="properties.kode_bps",
            color="kelas", color_discrete_map=cmap, category_orders={"kelas": labels},
            hover_name="nama",
            hover_data={"provinsi": True, "pct_pertanian": ":.1f", "pertanian": ":,.0f",
                        "total_pekerja": ":,.0f", "kode_bps": False, "kelas": False},
            labels={"provinsi": "Provinsi", "pct_pertanian": "% pekerja pertanian",
                    "pertanian": "Pekerja pertanian", "total_pekerja": "Total pekerja"},
            opacity=0.85,
        )
        fig.update_traces(marker_line_width=0.3, marker_line_color="#ffffff")
    else:
        fig = go.Figure()

    if LYR_SIMBOL in layers:
        col, judul_ukuran = UKURAN[ukuran_nama]
        v = geo[col].astype(float)
        fmt_hover = ',.3f' if col.startswith('konsumsi') else ',.0f'
        sizeref = 2.0 * v.max() / (26 ** 2)  # diameter simbol terbesar ≈ 26 px; LUAS sebanding nilai
        fig.add_trace(go.Scattermap(
            lat=geo["lat"], lon=geo["lon"], mode="markers", name="Simbol: " + ukuran_nama.split(" (")[0],
            marker=dict(size=v, sizemode="area", sizeref=sizeref, sizemin=2,
                        color=C.WARNA_SIMBOL, opacity=0.6),
            customdata=np.c_[geo["nama"], geo["provinsi"], v],
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>" + judul_ukuran + ": %{customdata[2]:" + fmt_hover + "}<extra></extra>",
        ))

    fig.update_layout(
        map=dict(style=C.BASEMAP, center=center, zoom=zoom),
        margin=dict(l=0, r=0, t=0, b=0), height=540,
        legend=dict(title_text="% pekerja pertanian", x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.88)",
                    font=dict(size=11)),
    )
    show(fig, key="peta_geo")
    sumber("Tabel: Penduduk 15+ yang bekerja menurut kab/kota dan lapangan usaha (2023); "
           "Rata-rata konsumsi perkapita seminggu kelompok padi-padian per kab/kota (2023)")
    st.caption(
        "Warna gelap = persentase pekerja pertanian tinggi. Luas lingkaran sebanding dengan nilai variabel. "
        "Satuan konsumsi beras mengikuti tabel BPS (satuan komoditas). Gunakan scroll/cubit untuk zoom dan seret untuk menggeser."
    )

    # ---------- Insight ----------
    st.markdown("#### Apa yang terlihat?")
    n = len(geo)
    med = geo["pct_pertanian"].median()
    n50 = int((geo["pct_pertanian"] >= 50).sum())
    top = geo.nlargest(5, "pct_pertanian")[["nama", "provinsi", "pct_pertanian", "pertanian", "total_pekerja"]]
    bot = geo.nsmallest(5, "pct_pertanian")[["nama", "provinsi", "pct_pertanian", "pertanian", "total_pekerja"]]
    st.write(
        f"Dari **{n}** kabupaten/kota, median persentase pekerja pertanian adalah **{fmt_dec(med)}%**, "
        f"dan **{n50}** daerah memiliki lebih dari separuh pekerjanya di sektor pertanian. "
        f"Daerah tertinggi adalah **{top.iloc[0]['nama']}** ({fmt_dec(top.iloc[0]['pct_pertanian'])}%), "
        f"sedangkan terendah **{bot.iloc[0]['nama']}** ({fmt_dec(bot.iloc[0]['pct_pertanian'], 2)}%)."
    )
    cfg = {
        "nama": "Kab/Kota", "provinsi": "Provinsi",
        "pct_pertanian": st.column_config.NumberColumn("% pekerja pertanian", format="%.1f"),
        "pertanian": st.column_config.NumberColumn("Pekerja pertanian", format="%d"),
        "total_pekerja": st.column_config.NumberColumn("Total pekerja", format="%d"),
    }
    t1, t2 = st.columns(2)
    t1.caption("Lima daerah dengan persentase tertinggi")
    tabel(top, t1, hide_index=True, column_config=cfg)
    t2.caption("Lima daerah dengan persentase terendah")
    tabel(bot, t2, hide_index=True, column_config=cfg)

    # ---------- Hubungan pertanian vs beras ----------
    st.markdown("#### Pekerja pertanian dan konsumsi beras")
    rho = geo["pct_pertanian"].corr(geo["konsumsi_beras_mingguan"], method="spearman")
    sc = px.scatter(geo, x="pct_pertanian", y="konsumsi_beras_mingguan", hover_name="nama",
                    hover_data={"provinsi": True, "pct_pertanian": ":.1f", "konsumsi_beras_mingguan": ":.3f"},
                    labels={"pct_pertanian": "% pekerja pertanian",
                            "konsumsi_beras_mingguan": "Konsumsi beras per kapita per minggu"},
                    opacity=0.55, color_discrete_sequence=[C.WARNA_SIMBOL])
    b, a = np.polyfit(geo["pct_pertanian"], geo["konsumsi_beras_mingguan"], 1)
    xs = np.array([geo["pct_pertanian"].min(), geo["pct_pertanian"].max()])
    sc.add_trace(go.Scatter(x=xs, y=a + b * xs, mode="lines", name="Garis tren",
                            line=dict(color="#D55E00", width=3)))
    sc.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    show(sc, key="sc_beras")
    st.write(
        f"Korelasi peringkat Spearman antara kedua variabel adalah **ρ = {fmt_dec(rho, 2)}**, "
        f"yaitu hubungan **{_korelasi_teks(rho)}**. Ini deskripsi pola antardaerah, **bukan bukti sebab-akibat**: "
        "pola konsumsi pangan pokok juga dipengaruhi kebiasaan setempat (misalnya umbi, jagung, atau sagu di sebagian wilayah timur)."
    )
    sumber("(2023)")
