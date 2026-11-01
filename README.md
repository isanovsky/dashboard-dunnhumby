# Dashboard Dunnhumby: Association Rule dan Sequential Pattern

Dashboard Streamlit untuk menampilkan hasil notebook `MiniProject_Dunnhumby_AR_SPM.ipynb`.
Dashboard hanya membaca file CSV di folder `hasil/`, tidak menghitung ulang data mentah.

## Struktur folder

```
dashboard_dunnhumby/
  app.py              # kode dashboard
  requirements.txt    # library yang dibutuhkan
  hasil/              # CSV hasil notebook (bagian 8)
    rq1_aturan_final.csv
    rq2_pola_panjang2.csv
    rq2_sensitivitas_N.csv
    rq3_segmen_aturan.csv
    rq3_segmen_pola.csv
    rq3_ukuran_keranjang_segmen.csv
    eda_*.csv         # ringkasan EDA (dari notebook versi terbaru)
```

Folder `hasil/` sudah berisi CSV dari run Colab terakhir, kecuali file `eda_*.csv`.
Untuk mengisi halaman EDA: jalankan notebook versi terbaru, unduh semua file `eda_*.csv`
dari folder `hasil/` di Colab, lalu salin ke folder `hasil/` di sini.

## Menjalankan di komputer sendiri

```
pip install -r requirements.txt
streamlit run app.py
```

Browser akan terbuka di `http://localhost:8501`.

## Deploy gratis ke Streamlit Community Cloud

1. Buat repository GitHub, unggah seluruh isi folder ini (termasuk `hasil/`).
2. Masuk ke https://share.streamlit.io dengan akun GitHub.
3. Pilih *Create app*, pilih repository, branch, dan file utama `app.py`, lalu *Deploy*.

Batas ukuran file dan ketentuan layanan bisa berubah; cek dokumentasi Streamlit terbaru.

## Halaman

| Halaman | Isi |
|---|---|
| Ringkasan | Angka kunci dan kesimpulan per RQ |
| EDA | Rumah tangga aktif per minggu, ukuran keranjang, porsi pembelian ulang, commodity terpopuler, jarak antar-kunjungan |
| RQ1 | Filter aturan (lift, confidence, support, jumlah item, cari commodity), grafik top-N, scatter support vs confidence, unduh hasil filter |
| RQ2 | Diagnostik artefak frekuensi, pola searah (dengan filter commodity non-populer), sensitivitas N |
| RQ3 | Lift aturan per segmen, ukuran keranjang per segmen, perbandingan pola (dengan peringatan keabsahan) |
