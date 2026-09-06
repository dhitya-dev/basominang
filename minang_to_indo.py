import re
import mysql.connector

# 🔁 Kamus akhiran
konversi_akhiran = {'lah': 'lah', 'nyo': 'nya', 'kan': 'kan', 'an': 'an', 'i': 'i'}
konversi_awalan = {'man': 'men', 'pang': 'peng', 'basi': 'bersi', 'ka': 'ke', 'sa': 'se' }
# 🔁 Daftar imbuhan yang digunakan untuk pemisahan awalan dan akhiran
daftar_awalan = ['mampa', 'bapa', 'tapa', 'sapa', 'baku', 'pang', 'basi', 'pan', 'man', 'bo', 'ba', 'ma', 'pa', 'ta', 'no', 'di', 'ka', 'sa']
daftar_akhiran = ['lah', 'nyo', 'kan', 'an', 'i']


# Tokenisasi teks
def pecah_teks(teks):
    return re.findall(r"\w+(?:-\w+)*|[.,!?;]", teks)

# 📌 Fungsi utama
def terjemahkan_teks(teks, kamus):
    token = pecah_teks(teks)
    token_terjemahan = [terjemahkan_kata(kata, kamus) for kata in token]
    return ''.join(
        f' {t}' if i > 0 and re.match(r"\w+", t) else t
        for i, t in enumerate(token_terjemahan)
    )

# 📌 Pisahkan akhiran
def pisah_akhiran(kata, daftar_akhiran, kamus):
    if kata in kamus:
        return kata, ''
    for akhiran in sorted(daftar_akhiran, key=len, reverse=True): 
        if kata.endswith(akhiran):
            calon = kata[:-len(akhiran)]
            return calon, akhiran  
    return kata, ''


# 📌 Pisahkan awalan
def pisah_awalan(kata, daftar_awalan):
    for awalan in sorted(daftar_awalan, key=len, reverse=True):
        if kata.startswith(awalan):
            sisa = kata[len(awalan):]
            id_kata, kategori, _ = ambil_kategori_dan_terjemahan_kata(sisa)
            if id_kata:
                return awalan, sisa
    return '', kata

# 📌 Ambil data dari DB
def ambil_kategori_dan_terjemahan_kata(kata):
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="terjemahan"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, kategori, kata_indo FROM minangkabau WHERE LOWER(kata_minang) = %s", (kata.lower(),))
        hasil = cursor.fetchone()
        conn.close()
        if hasil:
            return hasil
        return None, None, None
    except mysql.connector.Error:
        return None, None, None

# 📌 Ganti awalan dan akhiran
def ganti_awalan_akhiran(awalan, kata_dasar, akhiran):

    id_kata, kategori, kata_dasar_terjemahan = ambil_kategori_dan_terjemahan_kata(kata_dasar)
    if kata_dasar_terjemahan:
        kata_dasar_terjemahan = kata_dasar_terjemahan.lower()

    awalan_baru = konversi_awalan.get(awalan, awalan)
    if awalan == 'sapa' and kategori == "Kata Bilangan":
        awalan_baru = 'seper'
    elif awalan == 'tapa' and kategori in ["Kata Bilangan", "Kata Sifat", "Kata Sifat Kebiasaan"]:
        awalan_baru = 'Dijadikan '
    elif awalan == 'bapa' and kategori in ["Kata Bilangan", "Kata Sifat", "Kata Sifat Kebiasaan"]:
        awalan_baru = 'dijadikan '
    elif awalan == 'ta' and kategori in ["Kata Kerja", "Kata Sifat", "Kata Sifat Kebiasaan", "Kata Benda", "Kata Benda Status", "Kata Benda Alat", "Kata Benda Makhluk Hidup"]:
        awalan_baru = 'ter'
    elif awalan == 'no' and kategori == "Kata Kerja":
        awalan_baru = 'di'
    elif awalan == 'mampa':
        if kategori == "Kata Bilangan":
            awalan_baru = 'membagi '
        elif kategori in ["Kata Benda", "Kata Benda Status", "Kata Benda Alat", "Kata Benda Makhluk Hidup", "Kata Sifat", "Kata Sifat Kebiasaan"]:
            awalan_baru = 'memper'
    elif awalan == 'baku' and kategori == "Kata Kerja":
        awalan_baru = 'ber'
    # AWALAN Pa
    elif awalan == 'pa':
        if kategori == "Kata Sifat Kebiasaan":
            awalan_baru = 'pe'
        elif kategori in ["Kata Sifat", "Kata Sifat Kebiasaan"]:
            awalan_baru = 'memper'
        elif kategori == "Kata Benda Status":
            awalan_baru = 'menjadikan '
        elif kategori == "Kata Benda Makhluk Hidup":
            awalan_baru = 'memanggilkan '
        elif kategori == "Kata Bilangan":
            awalan_baru = 'bagi '
    # Awalan Pan
    elif awalan == 'pan':
        if kategori == "Kata Kerja":
            awalan_baru = 'pen'
        elif kategori == "Kata Benda Alat":
            awalan_baru = 'peng'
        elif kategori == "Kata Sifat Kebiasaan":
            awalan_baru = 'pe'
    elif awalan == 'ma' and kategori in ["Kata Kerja", "Kata Benda", "Kata Benda Status", "Kata Benda Alat", "Kata Benda Makhluk Hidup", "Kata Sifat", "Kata Sifat Kebiasaan"]:
        awalan_baru = 'me'
    elif awalan == 'bo' and kategori == "Kata Kerja Pasif":
        awalan_baru = 'di'
    elif awalan == 'ba' and kategori in ["Kata Kerja", "Kata Benda", "Kata Benda Status", "Kata Benda Alat", "Kata Benda Makhluk Hidup", "Kata Sifat", "Kata Sifat Kebiasaan", "Kata Bilangan"]:
        awalan_baru = 'ber'

    akhiran_baru = konversi_akhiran.get(akhiran, '')
    return awalan_baru, kata_dasar_terjemahan or kata_dasar, akhiran_baru, id_kata

# 📌 Pertahankan kapitalisasi awal
def kembalikan_kapitalisasi(asli, terjemahan):
    if asli[0].isupper():
        return terjemahan[0].upper() + terjemahan[1:]
    elif asli.isupper():
        return terjemahan.upper()
    return terjemahan

# 📌 Fungsi inti
def terjemahkan_kata(kata, kamus):
    print(f"\n Kata Asli: {kata}")
    kata_kecil = kata.lower()

    if kata_kecil in kamus:
        hasil = kembalikan_kapitalisasi(kata, kamus[kata_kecil])
        print(f" Ditemukan langsung di kamus: {hasil}")
        return hasil

    kata_dasar, akhiran = pisah_akhiran(kata_kecil, daftar_akhiran, kamus)
    print(f" Pisah akhiran → Kata Dasar: {kata_dasar} | Akhiran: {akhiran}")

    if kata_dasar in kamus:
        akhiran_baru = konversi_akhiran.get(akhiran, '')
        hasil = kembalikan_kapitalisasi(kata, kamus[kata_dasar] + akhiran_baru)
        print(f" Ditemukan kata dasar di kamus: {hasil}")
        return hasil
    

    awalan, kata_dasar = pisah_awalan(kata_dasar, daftar_awalan)
    print(f" Pisah awalan → Awalan: {awalan} | Sisa: {kata_dasar}")
    awalan_baru, kata_dasar_terjemahan, akhiran_baru, _ = ganti_awalan_akhiran(awalan, kata_dasar, akhiran)
    print(f" Konversi → Awalan Baru: {awalan_baru} | Dasar Terjemahan: {kata_dasar_terjemahan} | Akhiran Baru: {akhiran_baru}")

    kata_terjemahan_akhir = awalan_baru + kata_dasar_terjemahan + akhiran_baru
    hasil = kembalikan_kapitalisasi(kata, kata_terjemahan_akhir)
    print(f" Hasil Akhir Terjemahan: {hasil}")
    return hasil