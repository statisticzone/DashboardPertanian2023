"""Validasi data sebelum dijalankan/dideploy.  Jalankan:  python scripts/validasi_data.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config as C
from src import data_loader as dl


def cek(nama, kondisi, info=""):
    print(("[OK]   " if kondisi else "[GAGAL] ") + nama + (f"  {info}" if info else ""))
    return kondisi


ok = True
geo, hier, multi = dl.load_geospasial(), dl.load_hierarki(), dl.load_multivariat()
gj_kab, gj_prov = dl.load_geojson(C.FILE_GJ_KAB), dl.load_geojson(C.FILE_GJ_PROV)

# --- Geospasial ---
id_kab = {str(f["properties"]["kode_bps"]).zfill(4) for f in gj_kab["features"]}
ok &= cek("Geospasial: 514 kab/kota", len(geo) == 514, f"(n={len(geo)})")
ok &= cek("Geospasial: kode kab/kota cocok dengan GeoJSON", set(geo["kode_bps"]) == id_kab,
          f"(selisih={len(set(geo['kode_bps']) ^ id_kab)})")
ok &= cek("Geospasial: tidak ada nilai kosong", not geo[["pct_pertanian", "konsumsi_beras_mingguan"]].isna().any().any())
ok &= cek("Geospasial: pct_pertanian = pertanian/total_pekerja",
          ((geo["pertanian"] / geo["total_pekerja"] * 100 - geo["pct_pertanian"]).abs() < 1e-6).all())

# --- Hierarki ---
ok &= cek("Hierarki: 38 provinsi x 6 subsektor = 228 baris", len(hier) == 228 and hier["provinsi"].nunique() == 38)
ok &= cek("Hierarki: gurem <= usaha", (hier["jumlah_gurem"] <= hier["jumlah_usaha"]).all())
ok &= cek("Hierarki: tidak ada usaha = 0", (hier["jumlah_usaha"] > 0).all())

# --- Multivariat ---
id_prov = {str(f["properties"]["kode_prov"]).zfill(2) for f in gj_prov["features"]}
ok &= cek("Multivariat: 38 provinsi", len(multi) == 38)
ok &= cek("Multivariat: kode provinsi cocok dengan GeoJSON provinsi", set(multi["kode_prov"]) == id_prov,
          f"(selisih={sorted(set(multi['kode_prov']) ^ id_prov)})")
ok &= cek("Multivariat: kode provinsi sama dengan hierarki", set(multi["kode_prov"]) == set(hier["kode_prov"]))
lengkap = multi.dropna(subset=C.VARS)
ok &= cek("Multivariat: minimal 34 provinsi lengkap & 8 variabel", len(lengkap) >= 34 and len(C.VARS) >= 8,
          f"(lengkap={len(lengkap)})")
kosong = multi.loc[~multi["kode_prov"].isin(lengkap["kode_prov"]), "provinsi_nama"].tolist()
print("[INFO] Provinsi dengan data tidak lengkap (tidak ikut PCA):", kosong)

print("\nSEMUA PEMERIKSAAN LULUS" if ok else "\nADA PEMERIKSAAN YANG GAGAL, periksa daftar di atas")
