# BasoMinang

<p align="center">
  <img src="static/logo.png" alt="Logo BasoMinang" width="360">
</p>

BasoMinang adalah penerjemah dua arah Bahasa Indonesia dan Bahasa Minangkabau. platform ini menggabungkan terjemahan menggunakan aturan morfologi sederhana, dan text-to-speech untuk membantu pembelajaran sekaligus mendukung pelestarian bahasa daerah.

## Fitur

- Terjemahan Indonesia ke Minangkabau dan sebaliknya
- Pemrosesan awalan, akhiran, kapitalisasi, dan tanda baca
- Text-to-speech Bahasa Indonesia dan Minangkabau
- Penukaran arah bahasa, salin teks, dan penghitung karakter

## Arsitektur

basominang/
├── static/
│ ├── Background.png
│ ├── logo.png
│ └── scripts.js
├── templates/index.html
├── app.py
├── config.py
├── database.py
├── indo_to_minang.py
├── minang_to_indo.py
├── speech.py
├── translation_service.py
├── terjemahan.sql
└── requirements\*.txt

## Menjalankan proyek

### Prasyarat

Pastikan perangkat Anda sudah memiliki:

- Python 3.11
- MySQL 8

### 1. Siapkan virtual environment

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan virtual environment di Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Instal dependensi

Instal dependensi utama aplikasi:

```bash
pip install -r requirements.txt
```

### 3. Siapkan konfigurasi

Salin file konfigurasi contoh:

```powershell
Copy-Item .env.example .env
```

Kemudian buka file `.env` dan sesuaikan konfigurasi koneksi MySQL.

### 4. Siapkan database

Buat database:

```bash
mysql -u root -p -e "CREATE DATABASE terjemahan CHARACTER SET utf8mb4"
```

Kemudian impor data dari `terjemahan.sql`:

```bash
mysql -u root -p terjemahan < terjemahan.sql
```

### 5. Jalankan aplikasi

```bash
python app.py
```

Setelah aplikasi berjalan, buka:

http://127.0.0.1:5000

di browser.

## Mengaktifkan text-to-speech

Dependensi text-to-speech (TTS) dipisahkan dari dependensi utama karena ukuran instalasinya cukup besar.

Instal dependensi TTS:

```bash
pip install -r requirements-tts.txt
```

Bobot model tidak disimpan di repository agar ukuran repository dan proses clone tetap ringan.

Letakkan model yang Anda miliki dan berhak gunakan pada struktur direktori berikut:

```text
TTS_Indo/
├── config.json
├── model.safetensors
├── tokenizer_config.json
└── vocab.json

TTS_Minang/
├── best_model.pth
└── config_Agam.json
```
