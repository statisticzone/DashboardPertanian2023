"""Bagian 3 — Visualisasi data berdimensi tinggi (multivariat), provinsi 2023.

Teknik: PCA (reduksi dimensi + biplot), parallel coordinates, heatmap terklaster,
plus peta klaster provinsi. Brushing & linking: pilih titik/kotak/lasso pada PCA
(atau pilih provinsi manual) → provinsi yang sama disorot di semua tampilan lain.
Seluruh variabel distandardisasi (z-score) sebelum PCA dan klaster.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from . import config as C
from . import store
from .ui import fmt_dec, show, sumber, tabel

V = C.VARS


@st.cache_data(show_spinner=False)
def hitung(k: int):
    m = store.multivariat()
    d = m.dropna(subset=V).reset_index(drop=True)          # 34 provinsi dengan data lengkap
    Z = StandardScaler().fit_transform(d[V].to_numpy(float))
    pca = PCA().fit(Z)
    S = pca.transform(Z)
    lab = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(Z)
    urut = pd.Series(S[:, 0]).groupby(lab).mean().sort_values(ascending=False).index.tolist()
    remap = {old: i + 1 for i, old in enumerate(urut)}     # penomoran klaster stabil (urut PC1)
    d["klaster"] = [remap[x] for x in lab]
    d["pc1"], d["pc2"] = S[:, 0], S[:, 1]
    z = pd.DataFrame(Z, columns=V)
    return d, z, pca.explained_variance_ratio_, pca.components_, float(silhouette_score(Z, lab))


def _idx_terpilih(ev) -> set:
    out = set()
    try:
        for p in ev.selection.points:
            if p.get("curve_number", 0) == 0:
                out.add(int(p["point_index"]))
    except Exception:
        pass
    return out


def fig_pca(d, evr, comps, k):
    f = go.Figure()
    out = np.abs(StandardScaler().fit_transform(d[V])).max(axis=1) >= 2.5
    f.add_trace(go.Scatter(
        x=d["pc1"], y=d["pc2"], mode="markers+text",
        text=[n if o else "" for n, o in zip(d["provinsi_nama"], out)], textposition="top center",
        textfont=dict(size=10),
        marker=dict(size=12, color=[C.OKABE[c - 1] for c in d["klaster"]], line=dict(width=1, color="#333")),
        selected=dict(marker=dict(opacity=1, size=15)), unselected=dict(marker=dict(opacity=0.3)),
        customdata=np.c_[d["provinsi_nama"], d["klaster"]],
        hovertemplate="<b>%{customdata[0]}</b><br>Klaster %{customdata[1]}<extra></extra>",
        showlegend=False,
    ))
    sk = 0.85 * np.abs(d[["pc1", "pc2"]].to_numpy()).max() / np.abs(comps[:2]).max()
    for j, v in enumerate(V):  # panah beban variabel (biplot)
        x, y = comps[0, j] * sk, comps[1, j] * sk
        f.add_trace(go.Scatter(x=[0, x], y=[0, y], mode="lines+text", text=["", C.VAR_SHORT[v]],
                               textposition="top center", textfont=dict(size=10, color="#555"),
                               line=dict(color="#888", width=1.2), hoverinfo="skip", showlegend=False))
    for c in range(1, k + 1):  # entri legenda klaster
        f.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=f"Klaster {c}",
                               marker=dict(size=11, color=C.OKABE[c - 1])))
    f.update_layout(
        dragmode="select", height=520, margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title=f"PC1 ({fmt_dec(evr[0] * 100)}% varians)", yaxis_title=f"PC2 ({fmt_dec(evr[1] * 100)}% varians)",
        legend=dict(orientation="h", y=-0.2),
    )
    f.add_hline(y=0, line_color="#ddd"); f.add_vline(x=0, line_color="#ddd")
    return f


def fig_parcoords(d, sel, k):
    if sel:
        c = np.where(d.index.isin(sel), d["klaster"], 0)
    else:
        c = d["klaster"].to_numpy()
    o = np.argsort(c, kind="stable")                        # garis abu-abu digambar lebih dulu
    dd, cc = d.iloc[o], c[o]
    skala = [[i / k, C.ABU if i == 0 else C.OKABE[i - 1]] for i in range(k + 1)]
    f = go.Figure(go.Parcoords(
        line=dict(color=cc, colorscale=skala, cmin=0, cmax=k),
        dimensions=[dict(label=C.VAR_SHORT[v].replace(" ", "<br>"), values=dd[v]) for v in V],
    ))
    f.update_layout(height=420, margin=dict(l=50, r=40, t=70, b=20))
    return f


def fig_heatmap(d, z, sel):
    urut_baris = dendrogram(linkage(z.to_numpy(), "ward"), no_plot=True)["leaves"]
    urut_kol = dendrogram(linkage(z.to_numpy().T, "average", metric="correlation"), no_plot=True)["leaves"]
    zz = z.iloc[urut_baris, urut_kol]
    nama = d["provinsi_nama"].iloc[urut_baris].tolist()
    f = go.Figure(go.Heatmap(
        z=zz.to_numpy(), x=[C.VAR_SHORT[V[i]] for i in urut_kol], y=nama,
        colorscale="RdBu_r", zmid=0, zmin=-3, zmax=3, colorbar=dict(title="z-score", thickness=12),
        hovertemplate="<b>%{y}</b><br>%{x}: z = %{z:.2f}<extra></extra>",
    ))
    pos = {i: p for p, i in enumerate(urut_baris)}
    for i in sel:
        f.add_shape(type="rect", x0=-0.5, x1=len(V) - 0.5, y0=pos[i] - 0.5, y1=pos[i] + 0.5,
                    line=dict(color="black", width=2.5))
    f.update_layout(height=max(520, 20 * len(d) + 120), margin=dict(l=0, r=0, t=10, b=0),
                    yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
                    xaxis=dict(tickangle=-35, side="top"))
    return f


def fig_peta_klaster(d, m_all, sel_codes, k):
    gj = store.geojson_prov()
    peta = m_all[["kode_prov", "provinsi_nama"]].merge(d[["kode_prov", "klaster"]], on="kode_prov", how="left")
    peta["grup"] = peta["klaster"].map(lambda x: "Data tidak lengkap" if pd.isna(x) else f"Klaster {int(x)}")
    cmap = {f"Klaster {i}": C.OKABE[i - 1] for i in range(1, k + 1)}
    cmap["Data tidak lengkap"] = C.ABU
    f = px.choropleth_map(
        peta, geojson=gj, locations="kode_prov", featureidkey="properties.kode_prov",
        color="grup", color_discrete_map=cmap, hover_name="provinsi_nama",
        hover_data={"kode_prov": False, "grup": True}, labels={"grup": "Kelompok"},
        category_orders={"grup": [f"Klaster {i}" for i in range(1, k + 1)] + ["Data tidak lengkap"]},
        opacity=0.85,
    )
    f.update_traces(marker_line_width=0.5, marker_line_color="white")
    if sel_codes:
        f.add_trace(go.Choroplethmap(
            geojson=gj, locations=sel_codes, z=[1] * len(sel_codes), featureidkey="properties.kode_prov",
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
            marker=dict(line=dict(width=3, color="black")), hoverinfo="skip", showlegend=False))
    f.update_layout(map=dict(style=C.BASEMAP, center=dict(lat=-2.5, lon=118), zoom=3.1),
                    margin=dict(l=0, r=0, t=0, b=0), height=420,
                    legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.88)", title_text=""))
    return f


def render():
    m_all = store.multivariat()
    st.markdown("### 🧭 Tipologi pertanian provinsi")
    st.write(
        "Delapan variabel pertanian dipadukan untuk melihat **provinsi mana yang mirip satu sama lain**. "
        "Karena satuan tiap variabel berbeda (persen, ku/ha, indeks), semuanya distandardisasi (*z-score*) lebih dulu. "
        "Pilih titik atau area pada grafik PCA di bawah, maka provinsi yang sama disorot di grafik garis paralel, "
        "heatmap, dan peta."
    )
    k = st.slider("Jumlah klaster (k-means)", 2, 6, 4)
    d, z, evr, comps, sil = hitung(k)
    excl = m_all.loc[~m_all["kode_prov"].isin(d["kode_prov"]), "provinsi_nama"].tolist()
    st.caption(
        f"{len(d)} provinsi dengan data lengkap dianalisis. Tidak diikutkan karena sebagian variabel belum tersedia: "
        f"{', '.join(excl) if excl else '-'}. Silhouette = {fmt_dec(sil, 2)}; PC1+PC2 menjelaskan "
        f"{fmt_dec((evr[0] + evr[1]) * 100)}% varians."
    )

    # ---------- 1) PCA (sumber seleksi untuk brushing & linking) ----------
    st.markdown("#### 1. PCA: peta kemiripan provinsi")
    manual = st.multiselect("Atau pilih provinsi secara manual (untuk ponsel)", d["provinsi_nama"].tolist(), key="mv_manual")
    ev = show(fig_pca(d, evr, comps, k), key="mv_pca", on_select="rerun", selection_mode=("points", "box", "lasso"))
    sel = _idx_terpilih(ev) | set(d.index[d["provinsi_nama"].isin(manual)])
    sel_codes = d.loc[sorted(sel), "kode_prov"].tolist()
    st.caption("Titik berdekatan = profil pertanian mirip. Panah menunjukkan arah variabel; titik yang searah panah "
               "bernilai tinggi pada variabel itu. Warna = klaster. " +
               (f"**{len(sel)} provinsi dipilih.**" if sel else "Belum ada provinsi dipilih."))
    sumber("Tabel: Sensus Pertanian 2023 (gurem, umur & jenis kelamin KRT, penggunaan pupuk, badan hukum); "
           "Luas panen, produksi, dan produktivitas padi menurut provinsi; Nilai Tukar Petani menurut provinsi; "
           "Penduduk 15+ yang bekerja menurut lapangan usaha (2023)")

    # ---------- 2) Parallel coordinates ----------
    st.markdown("#### 2. Garis paralel: profil lengkap tiap provinsi")
    show(fig_parcoords(d, sel, k), key="mv_par")
    st.caption("Satu garis = satu provinsi. Seret pada sebuah sumbu untuk menyaring garis. Garis abu-abu = provinsi tidak dipilih.")

    # ---------- 3) Heatmap terklaster ----------
    st.markdown("#### 3. Heatmap terklaster")
    show(fig_heatmap(d, z, sel), key="mv_heat")
    st.caption("Biru = di bawah rata-rata, merah = di atas rata-rata (z-score). Baris dan kolom diurutkan menurut "
               "kemiripan (klaster hierarkis). Bingkai hitam = provinsi dipilih.")

    # ---------- 4) Peta klaster ----------
    st.markdown("#### 4. Di mana letak tiap klaster?")
    show(fig_peta_klaster(d, m_all, sel_codes, k), key="mv_map")
    sumber("Batas provinsi: berkas GeoJSON pendukung (non-BPS); data: tabel di atas")

    if sel:
        st.markdown("#### Provinsi terpilih")
        tab = d.loc[sorted(sel), ["provinsi_nama", "klaster"] + V].rename(columns={"provinsi_nama": "Provinsi", "klaster": "Klaster", **C.VAR_LABEL})
        tabel(tab, hide_index=True)

    # ---------- Interpretasi ----------
    st.markdown("#### Membaca klaster dan pencilan")
    prof = z.groupby(d["klaster"]).mean()
    for c in prof.index:
        anggota = d.loc[d["klaster"] == c, "provinsi_nama"].tolist()
        tinggi = prof.loc[c].nlargest(2); rendah = prof.loc[c].nsmallest(2)
        t = ", ".join(f"{C.VAR_LABEL[v]} ({x:+.1f} SD)".replace(".", ",") for v, x in tinggi.items())
        r = ", ".join(f"{C.VAR_LABEL[v]} ({x:+.1f} SD)".replace(".", ",") for v, x in rendah.items())
        with st.expander(f"Klaster {c} — {len(anggota)} provinsi"):
            st.write(f"**Relatif tinggi:** {t}.  \n**Relatif rendah:** {r}.")
            st.write("**Anggota:** " + ", ".join(anggota) + ".")
    zabs = z.abs()
    pen = pd.DataFrame({"Provinsi": d["provinsi_nama"], "Variabel paling ekstrem": zabs.idxmax(axis=1).map(C.VAR_LABEL),
                        "|z| maks": zabs.max(axis=1)}).nlargest(5, "|z| maks")
    st.write("**Lima provinsi dengan nilai paling ekstrem pada salah satu variabel (kandidat pencilan):**")
    tabel(pen, hide_index=True, column_config={"|z| maks": st.column_config.NumberColumn(format="%.2f")})
    st.caption("Klaster dan pencilan ini bersifat deskriptif. Nama klaster sebaiknya dirumuskan dari ciri di atas "
               "dan dibahas bersama konteks daerahnya.")
