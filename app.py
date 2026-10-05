"""Potret Pertanian Indonesia 2023 — web story data (Streamlit)."""
import streamlit as st

from src import geospasial, hierarki, multivariat, store
from src.ui import fmt_dec, fmt_int

st.set_page_config(page_title="Potret Pertanian Indonesia 2023", page_icon="🌾", layout="wide")

st.title("🌾 Potret Pertanian Indonesia 2023")
st.markdown(
    "##### Menelusuri struktur, karakteristik, dan persebaran pertanian Indonesia melalui data BPS"
)

with st.sidebar:
    st.header("Dashboard")
    st.write("Bagaimana pertanian membentuk kehidupan dan karakteristik berbagai wilayah di Indonesia?")
    st.write("By Difya Ayu Meisya Nurjanah")
    st.write("**Alur cerita**")
    st.markdown("1. Ketergantungan pada pertanian (peta)\n2. Struktur usaha tani (hierarki)\n3. Tipologi provinsi (multivariat)\n4. Penutup")
    st.write("**Menjelajahi Pertanian Indonesia**")
    st.caption("Setiap visualisasi dirancang untuk menjawab pertanyaan yang berbeda. Arahkan kursor pada grafik atau peta untuk melihat informasi lebih rinci.")
    st.caption("Warna dan ukuran digunakan untuk membantu membandingkan pola antarwilayah.")

# ---------- Pembuka ----------
geo = store.geospasial()
h = store.hierarki()
tot_u, tot_g = h["jumlah_usaha"].sum(), h["jumlah_gurem"].sum()
c1, c2, c3 = st.columns(3)
c1.metric("Kabupaten/Kota", fmt_int(len(geo)))
c2.metric("Median pekerja di sektor pertanian", f"{fmt_dec(geo['pct_pertanian'].median())}%")
c3.metric("Usaha pertanian gurem", f"{fmt_dec(tot_g / tot_u * 100)}%")
st.write(
    "Pertanian menyerap banyak tenaga kerja dan menyediakan pangan, tetapi sebagian besar usahanya berskala kecil. "
    "Dashboard ini mencoba menjawab: **seberapa bergantung daerah pada pertanian, bagaimana struktur usahanya, "
    "dan provinsi mana yang memiliki profil pertanian serupa?**"
)
st.caption("Usaha Pertanian Gurem : Banyaknya usaha pertanian perorangan yang menggunakan lahan pertanian kurang dari 0,5 hektar dan melakukan manajemen kegiatan usaha budidaya tanaman sayuran, tanaman buah-buahan, tanaman hias, dan tanaman obat, termasuk pembibitan tanaman hortikultura. Mengacu ke Usaha Pertanian Perorangan (UTP).")

st.divider()
st.markdown("## Bagian 1 · Seberapa bergantung daerah pada pertanian?")
geospasial.render()

st.divider()
st.markdown("## Bagian 2 · Seperti apa struktur usaha pertaniannya?")
hierarki.render()

st.divider()
st.markdown("## Bagian 3 · Provinsi mana yang mirip?")
multivariat.render()

st.divider()
st.markdown("## Penutup")
st.write(
    "- Ketergantungan pada pertanian sangat bervariasi antardaerah, dan pola konsumsi beras tidak selalu sejalan dengan itu.\n"
    "- Usaha pertanian tersebar tidak merata antarpulau, dan proporsi usaha gurem berbeda antarsubsektor maupun antarprovinsi.\n"
    "- Delapan variabel pertanian mengelompokkan provinsi menjadi beberapa tipe, dengan beberapa provinsi sebagai pencilan."
)
st.caption("Sumber: Sensus Pertanian 2023 dan Tabel Dinamis Badan Pusat Statistik dan Badan Pusat Statistik (BPS).")
