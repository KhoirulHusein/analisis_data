# Proyek Analisis Data E-Commerce

Proyek ini berisi analisis komprehensif dari E-Commerce Public Dataset, mencakup pola pembelian pelanggan, kategori produk populer, performa penjual, dan segmentasi pelanggan menggunakan analisis RFM.

## Struktur Folder

```
submission/
├── data/                             # dataset asli
├── analysis.ipynb                    # notebook lengkap & sudah run
├── app.py                            # streamlit dashboard
├── requirements.txt                  # daftar library yang digunakan
└── README.md                         # dokumentasi proyek
```

## Deskripsi Proyek

Proyek ini menganalisis dataset e-commerce publik untuk mendapatkan insight bisnis yang berharga. Analisis mencakup:

1. **Pola Pembelian Pelanggan**: Analisis pola pembelian berdasarkan waktu (jam, hari, bulan) dan lokasi geografis.
2. **Kategori Produk Populer**: Identifikasi kategori produk terlaris dan yang menghasilkan pendapatan tertinggi.
3. **Performa Penjual**: Analisis performa penjual berdasarkan lokasi, volume penjualan, dan rating pelanggan.
4. **Segmentasi Pelanggan**: Segmentasi pelanggan menggunakan analisis RFM (Recency, Frequency, Monetary).

## Cara Menjalankan Dashboard Lokal

1. Pastikan semua library yang diperlukan sudah terinstal:
   ```
   pip install -r requirements.txt
   ```

2. Jalankan aplikasi Streamlit:
   ```
   streamlit run app.py
   ```

3. Dashboard akan terbuka di browser Anda secara otomatis, biasanya di alamat `http://localhost:8501`.

## Fitur Dashboard

Dashboard interaktif menyediakan beberapa halaman:

- **Beranda**: Ringkasan metrik utama dan visualisasi kunci.
- **Pola Pembelian**: Analisis pola pembelian berdasarkan waktu dan lokasi.
- **Analisis Kategori Produk**: Kategori produk terlaris dan dengan pendapatan tertinggi.
- **Performa Penjual**: Analisis performa penjual berdasarkan berbagai metrik.
- **Segmentasi Pelanggan (RFM)**: Segmentasi pelanggan berdasarkan analisis RFM.
- **Insight & Kesimpulan**: Ringkasan insight dan rekomendasi bisnis.

## Teknologi yang Digunakan

- Python
- Pandas & NumPy untuk manipulasi data
- Matplotlib, Seaborn, dan Plotly untuk visualisasi
- Streamlit untuk dashboard interaktif

## Catatan

Pastikan struktur folder sesuai dengan yang dijelaskan di atas, terutama folder `data/` yang berisi dataset asli, agar aplikasi dapat berjalan dengan benar.
