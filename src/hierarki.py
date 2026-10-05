"""Bagian 2 — Visualisasi data berhierarki: Indonesia → Pulau → Provinsi → Subsektor.

Dua representasi (treemap dan sunburst) dari data yang sama.
Ukuran = jumlah usaha pertanian perorangan; warna = % usaha gurem.
% gurem untuk simpul induk dihitung ulang: Σ gurem ÷ Σ usaha (BUKAN rata-rata persentase).
Drill-down: klik simpul; breadcrumb (pathbar) di atas treemap dapat diklik untuk kembali.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from . import config as C
from . import store
from .ui import fmt_dec, fmt_int, show, sumber, tabel

JENIS = {0: "pulau", 1: "provinsi", 2: "subsektor"}


def build_nodes(h: pd.DataFrame) -> pd.DataFrame:
    rows = []

    def add(id_, label, parent, level, g):
        u, gu = g["jumlah_usaha"].sum(), g["jumlah_gurem"].sum()
        rows.append(dict(id=id_, label=label, parent=parent, level=level, usaha=u, gurem=gu,
                         pct=gu / u * 100 if u else np.nan))

    add("Indonesia", "Indonesia", "", 0, h)
    for pulau, gp in h.groupby("pulau"):
        pid = f"Indonesia/{pulau}"
        add(pid, pulau, "Indonesia", 1, gp)
        for prov, gv in gp.groupby("provinsi_nama"):
            vid = f"{pid}/{prov}"
            add(vid, prov, pid, 2, gv)
            for sub, gs in gv.groupby("subsektor"):
                add(f"{vid}/{sub}", sub, vid, 3, gs)
    return pd.DataFrame(rows)


def _kolom_umum(nodes: pd.DataFrame, level_id: str, maxdepth: int):
    return dict(
        ids=nodes["id"], labels=nodes["label"], parents=nodes["parent"], values=nodes["usaha"],
        branchvalues="total", maxdepth=maxdepth,
        level="" if level_id == "Indonesia" else level_id,
        text=[f"{fmt_dec(p)}% gurem" for p in nodes["pct"]],
        textinfo="label+text",
        customdata=np.c_[nodes["usaha"], nodes["gurem"], nodes["pct"]],
        hovertemplate=("<b>%{label}</b><br>Jumlah usaha: %{customdata[0]:,.0f}"
                       "<br>Usaha gurem: %{customdata[1]:,.0f}"
                       "<br>Persentase gurem: %{customdata[2]:.1f}%<extra></extra>"),
        marker=dict(colors=nodes["pct"], colorscale=C.SKALA_GUREM,
                    cmin=float(nodes["pct"].min()), cmax=float(nodes["pct"].max()),
                    colorbar=dict(title=dict(text="% gurem"), ticksuffix="%", thickness=14),
                    line=dict(width=1, color="white")),
    )


def fig_treemap(nodes, level_id):
    f = go.Figure(go.Treemap(**_kolom_umum(nodes, level_id, 2),
                             pathbar=dict(visible=True, side="top", thickness=28)))
    f.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=560)
    return f


def fig_sunburst(nodes, level_id):
    f = go.Figure(go.Sunburst(**_kolom_umum(nodes, level_id, 3), insidetextorientation="radial"))
    f.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=560)
    return f


def insight_text(nodes, level_id) -> str:
    cur = nodes[nodes["id"] == level_id].iloc[0]
    ch = nodes[nodes["parent"] == level_id]
    if ch.empty:
        return ""
    big = ch.loc[ch["usaha"].idxmax()]
    hi, lo = ch.loc[ch["pct"].idxmax()], ch.loc[ch["pct"].idxmin()]
    return (
        f"Di **{cur['label']}**, {JENIS[int(cur['level'])]} **{big['label']}** memiliki jumlah usaha terbesar "
        f"({fmt_int(big['usaha'])} usaha, {fmt_dec(big['usaha'] / cur['usaha'] * 100)}% dari total). "
        f"Persentase usaha gurem tertinggi ada di **{hi['label']}** ({fmt_dec(hi['pct'])}%) "
        f"dan terendah di **{lo['label']}** ({fmt_dec(lo['pct'])}%). "
        "Ini gambaran deskriptif dari data, bukan penilaian mana yang lebih baik."
    )


def render():
    h = store.hierarki()
    nodes = build_nodes(h)
    root = nodes.iloc[0]

    st.markdown("### 🌳 Pertanian Indonesia tidak seragam")
    st.write(
        "Pertanian tersebar di berbagai pulau, provinsi, dan subsektor, dan tiap tingkat punya karakter berbeda. "
        "Telusuri dari wilayah terbesar sampai ke subsektor: **Indonesia → Pulau → Provinsi → Subsektor**. "
        "*Ukuran kotak* menunjukkan jumlah usaha, *warna* menunjukkan persentase usaha gurem."
    )
    k1, k2, k3 = st.columns(3)
    k1.metric("Usaha pertanian (6 subsektor)", fmt_int(root["usaha"]))
    k2.metric("Usaha gurem", fmt_int(root["gurem"]))
    k3.metric("Persentase gurem", f"{fmt_dec(root['pct'])}%")
    st.caption("Satu usaha dapat menjalankan lebih dari satu subsektor sehingga terhitung lebih dari sekali; "
               "angka ini sebaiknya dibaca sebagai perbandingan relatif antarwilayah.")

    # ---------- Navigator (alternatif klik, berguna di ponsel) ----------
    c1, c2 = st.columns(2)
    pulau = c1.selectbox("Mulai dari", ["Seluruh Indonesia"] + sorted(h["pulau"].unique()))
    level_id = "Indonesia"
    if pulau != "Seluruh Indonesia":
        level_id = f"Indonesia/{pulau}"
        provs = sorted(h.loc[h["pulau"] == pulau, "provinsi_nama"].unique())
        prov = c2.selectbox("Lanjut ke provinsi", ["(semua provinsi)"] + provs)
        if prov != "(semua provinsi)":
            level_id = f"{level_id}/{prov}"
    else:
        c2.empty()

    tab1, tab2 = st.tabs(["Treemap", "Sunburst"])
    with tab1:
        st.caption("Klik kotak untuk membuka tingkat berikutnya (drill-down). "
                   "Klik jalur di bagian atas (breadcrumb) untuk kembali.")
        show(fig_treemap(nodes, level_id), key=f"tm_{level_id}")
        sumber("Tabel: Jumlah usaha pertanian perorangan menurut wilayah dan subsektor, dan jumlah usaha pertanian "
               "perorangan gurem menurut wilayah dan subsektor (Sensus Pertanian 2023)")
    with tab2:
        st.caption("Cincin dalam = tingkat atas, cincin luar = tingkat di bawahnya. Klik sektor untuk memperbesar, "
                   "klik bagian tengah untuk kembali satu tingkat.")
        show(fig_sunburst(nodes, level_id), key=f"sb_{level_id}")
        sumber("Tabel yang sama dengan treemap (Sensus Pertanian 2023)")

    st.markdown("#### Apa yang terlihat?")
    st.write(insight_text(nodes, level_id))
    ch = nodes[nodes["parent"] == level_id][["label", "usaha", "gurem", "pct"]].sort_values("usaha", ascending=False)
    tabel(
        ch, hide_index=True,
        column_config={
            "label": "Wilayah / subsektor",
            "usaha": st.column_config.NumberColumn("Jumlah usaha", format="%d"),
            "gurem": st.column_config.NumberColumn("Usaha gurem", format="%d"),
            "pct": st.column_config.NumberColumn("% gurem", format="%.1f"),
        },
    )
