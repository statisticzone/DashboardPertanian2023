# 🌾 Potret Pertanian Indonesia 2023

Web story data interaktif untuk **UAS Visualisasi Data dan Informasi** (K203407, Politeknik Statistika STIS, TA 2025/2026).
Menelusuri ketergantungan daerah pada pertanian, struktur usaha tani, dan tipologi provinsi dari data BPS 2023.

- **Aplikasi (publik):** `ISI_URL_APLIKASI`
- **Repositori:** `ISI_URL_REPOSITORI`

## Isi proyek dan topik visualisasi

| Bagian | Topik soal | Data | Visualisasi | Interaksi |
|---|---|---|---|---|
| 1 | Geospasial (514 kab/kota) | `geospasial.xlsx` + `kabkota_514_dashboard.geojson` | Choropleth % pekerja pertanian; simbol proporsional (konsumsi beras atau jumlah pekerja pertanian) | Tooltip, legenda, zoom/pan, kontrol layer, metode klasifikasi, fokus provinsi |
| 2 | Hierarki (4 level) | `hierarki.xlsx` | Treemap dan sunburst: Indonesia → Pulau → Provinsi → Subsektor | Drill-down, breadcrumb, tooltip |
| 3 | Berdimensi tinggi (38 provinsi, 8 variabel) | `multivariat.xlsx` + `provinsi_38_dashboard.geojson` | PCA (biplot), parallel coordinates, heatmap terklaster, peta klaster | Brushing & linking, jumlah klaster, pilih provinsi |

## Struktur folder

```
pertanian/
├── app.py                  # halaman utama (alur cerita)
├── requirements.txt
├── README.md
├── .streamlit/config.toml  # tema
├── data/                   # 3 file .xlsx + 2 file .geojson
├── src/
│   ├── config.py           # path, palet, label variabel
│   ├── data_loader.py      # pembersihan data
│   ├── store.py            # cache Streamlit
│   ├── ui.py               # helper tampilan
│   ├── geospasial.py       # bagian 1
│   ├── hierarki.py         # bagian 2
│   └── multivariat.py      # bagian 3
└── scripts/validasi_data.py
```

## Menjalankan di komputer

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python scripts/validasi_data.py   # memeriksa kecocokan kode wilayah
streamlit run app.py
```

## Deployment (Streamlit Community Cloud)

1. Unggah folder `pertanian` ke repositori GitHub **publik** (termasuk folder `data/`).
2. Buka https://share.streamlit.io, masuk dengan GitHub, pilih **Create app**.
3. Pilih repositori dan cabang, isi *Main file path* dengan `app.py`, lalu **Deploy**.
4. Salin URL aplikasi ke bagian atas README ini dan ke makalah.

## Sumber data (lengkapi sebelum dikumpulkan)

Semua data berasal dari BPS, tahun 2023. Isi kolom URL dan tanggal akses sesuai halaman yang Anda unduh.

| Berkas | Judul tabel BPS | URL | Tanggal akses |
|---|---|---|---|
| geospasial | Penduduk Berumur 15 Tahun Keatas yang Bekerja Selama Seminggu Terakhir Menurut Kabupaten/Kota dan Lapangan Usaha | ISI | ISI |
| geospasial | Rata-rata Konsumsi Perkapita Seminggu Menurut Kelompok Padi-Padian Per Kabupaten/kota | ISI | ISI |
| hierarki | Jumlah Usaha Pertanian Perorangan Menurut Wilayah dan Subsektor (ST2023) | ISI | ISI |
| hierarki | Jumlah Usaha Pertanian Perorangan Gurem Menurut Wilayah dan Subsektor (ST2023) | https://sensus.bps.go.id/topik/tabular/st2023/237/98808/0 | 4 Oktober 2026 |
| multivariat | Usaha gurem, umur dan jenis kelamin KRT, penggunaan pupuk, badan hukum (ST2023) | ISI | ISI |
| multivariat | Luas Panen, Produksi, dan Produktivitas Padi Menurut Provinsi | ISI | ISI |
| multivariat | Nilai Tukar Petani menurut Provinsi (rata-rata Jan–Des 2023) | ISI | ISI |
| peta | Batas kab/kota dan provinsi (GeoJSON, data pendukung non-BPS) | ISI | ISI |

## Kamus data

**geospasial.xlsx** (514 baris): `kode_bps` (kab/kota), `kab-kota`, `pertanian`, `industri_pengolahan`, `jasa`, `total_pekerja` (orang), `pct_pertanian` = pertanian ÷ total_pekerja × 100, `konsumsi_beras_mingguan` (rata-rata per kapita per minggu, satuan komoditas BPS).

**hierarki.xlsx** (228 baris = 38 provinsi × 6 subsektor): `kode_prov`, `pulau`, `provinsi`, `subsektor`, `jumlah_usaha`, `jumlah_gurem`, `pct_gurem`. Persentase simpul induk dihitung Σ gurem ÷ Σ usaha, bukan rata-rata persentase.

**multivariat.xlsx** (38 baris): delapan variabel analisis, yaitu `pct_gurem`, `pct_krt_>=55`, `pct_krt_perempuan`, `pct_pakai_pupuk`, `pct_berbadan_hukum`, `produktivitas_padi(ku/ha)`, `ntp_2023`, `pct_pekerja_pertanian`. Tanda `-` dibaca sebagai data kosong.

## Keputusan rancangan

- **Warna:** palet Okabe–Ito untuk kategori; skala sekuensial satu rona (Greens, YlOrBr) dan diverging RdBu untuk z-score. Warna tidak menjadi satu-satunya penanda (ada label, legenda, dan tooltip).
- **Choropleth** memakai rasio (% pekerja pertanian), bukan angka absolut. Kelas dapat diganti antara kuantil, natural breaks, dan interval sama.
- **Simbol proporsional** diskalakan menurut *luas* lingkaran (bukan jari-jari).
- **Multivariat:** variabel distandardisasi (z-score) sebelum PCA dan k-means (random_state=42). Penomoran klaster diurutkan menurut rata-rata PC1.


