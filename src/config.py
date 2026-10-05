"""Konfigurasi: lokasi file, palet warna ramah buta warna, dan label variabel."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

FILE_GEO = DATA_DIR / "geospasial.xlsx"
FILE_HIER = DATA_DIR / "hierarki.xlsx"
FILE_MULTI = DATA_DIR / "multivariat.xlsx"
FILE_GJ_KAB = DATA_DIR / "kabkota_514_dashboard.geojson"
FILE_GJ_PROV = DATA_DIR / "provinsi_38_dashboard.geojson"

# Palet kategorikal Okabe-Ito (aman untuk buta warna)
OKABE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00", "#56B4E9"]
ABU = "#BDBDBD"
WARNA_SIMBOL = "#0072B2"

# Skala sekuensial (satu rona, dibedakan oleh kecerahan)
SKALA_PEKERJA = "Greens"   # peta choropleth % pekerja pertanian
SKALA_GUREM = "YlOrBr"     # treemap/sunburst % usaha gurem

BASEMAP = "carto-positron"

# ----- Variabel multivariat (8 variabel, nama kolom setelah dibersihkan) -----
VARS = [
    "pct_gurem", "pct_krt_55plus", "pct_krt_perempuan", "pct_pakai_pupuk",
    "pct_berbadan_hukum", "produktivitas_padi", "ntp_2023", "pct_pekerja_pertanian",
]
VAR_LABEL = {
    "pct_gurem": "Usaha gurem (%)",
    "pct_krt_55plus": "KRT usia ≥55 th (%)",
    "pct_krt_perempuan": "KRT perempuan (%)",
    "pct_pakai_pupuk": "Usaha pakai pupuk (%)",
    "pct_berbadan_hukum": "Berbadan hukum (%)",
    "produktivitas_padi": "Produktivitas padi (ku/ha)",
    "ntp_2023": "NTP 2023 (indeks)",
    "pct_pekerja_pertanian": "Pekerja pertanian (%)",
}
VAR_SHORT = {
    "pct_gurem": "Gurem",
    "pct_krt_55plus": "KRT ≥55",
    "pct_krt_perempuan": "KRT perempuan",
    "pct_pakai_pupuk": "Pakai pupuk",
    "pct_berbadan_hukum": "Berbadan hukum",
    "produktivitas_padi": "Produkt. padi",
    "ntp_2023": "NTP",
    "pct_pekerja_pertanian": "Pekerja tani",
}
