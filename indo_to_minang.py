import re

def terjemahkan_teks(teks, kamus):
    token = pecah_teks(teks)
    token_terjemahan = [terjemahkan_kata(kata, kamus) for kata in token]
    return ''.join(
        f' {t}' if i > 0 and re.match(r"\w+", t) else t
        for i, t in enumerate(token_terjemahan)
    )

def pecah_teks(teks):
    token = re.findall(r"\w+(?:-\w+)*|[.,!?;]", teks)
    return token

# Pastikan imbuhan lebih panjang diproses lebih dulu
daftar_awalan = ['memper', 'seper', 'meng', 'men', 'peng', 'pen', 'bersi', 'ber','be', 'ter', 'me', 'di', 'ke', 'pe', 'se']
daftar_akhiran = ['lah', 'kan', 'an', 'i', 'kah', 'nya'] 

def pisah_awalan(kata, daftar_awalan, kamus):
    for awalan in sorted(daftar_awalan, key=len, reverse=True):
        if kata.startswith(awalan):
            sisa = kata[len(awalan):]
            if sisa in kamus:
                return awalan, sisa
    # fallback= kalau tidak valid tetap ambil awalan pertama yang cocok
    for awalan in sorted(daftar_awalan, key=len, reverse=True):
        if kata.startswith(awalan):
            sisa = kata[len(awalan):]
            return awalan, sisa
    return '', kata

def pisah_akhiran(kata, daftar_akhiran):
    for akhiran in sorted(daftar_akhiran, key=len, reverse=True):
        if kata.endswith(akhiran):
            calon_dasar = kata[:-len(akhiran)]
            return calon_dasar, akhiran
    return kata, ''



def ganti_awalan_akhiran(awalan, akhiran):
    konversi_awalan = {
        'memper': 'mampa', 'seper': 'sapa', 'meng': 'ma', 'men': 'man', 'peng': 'pang', 'pen': 'pan',
        'bersi': 'basi', 'ber': 'ba','be': 'ba', 'ter': 'ta', 'me': 'ma', 'di': 'di', 'ke': 'ka', 'pe': 'pa', 'se': 'sa'
    }
    konversi_akhiran = {'lah': 'lah', 'an': 'an', 'i': 'i', 'kan': 'kan', 'kah': '', 'nya': 'nyo'}  

    return konversi_awalan.get(awalan, awalan), konversi_akhiran.get(akhiran, akhiran)  

# Anak-anak tetap jadi Anak-anak bukan anak-anak, dan bisa mempertahankan kapital kata SAYA jadi
def kembalikan_kapitalisasi(asli, terjemahan):
    if asli.isupper():
        return terjemahan.upper()
    elif asli[0].isupper():
        return terjemahan[0].upper() + terjemahan[1:]
    return terjemahan

def terjemahkan_kata(kata, kamus):
    kata_kecil = kata.lower()
    print(f"\n[🔍] Kata Asli: {kata} | Lowercase: {kata_kecil}")

    # 1. Cek langsung ke kamus
    if kata_kecil in kamus:
        print(f" Langsung ditemukan di kamus: {kata_kecil} → {kamus[kata_kecil]}")
        return kembalikan_kapitalisasi(kata, kamus[kata_kecil])

    # 2. Pisah awalan dulu
    awalan, sisa = pisah_awalan(kata_kecil, daftar_awalan, kamus)
    # awalan, sisa = pisah_awalan(kata_kecil, daftar_awalan)
    print(f"  ✂️ Pisah awalan → Awalan: {awalan} | Sisa: {sisa}")

    # 3. Cek sisa di kamus
    if sisa in kamus:
        kata_terjemahan = kamus[sisa]
        awalan_baru = ganti_awalan_akhiran(awalan, '')[0]
        hasil = awalan_baru + kata_terjemahan
        print(f"  Ditemukan setelah pisah awalan: {sisa} → {kata_terjemahan}")
        print(f"  Hasil akhir: {hasil}")
        return kembalikan_kapitalisasi(kata, hasil)

    # 4. Pisah akhiran dari sisa
    kata_dasar, akhiran = pisah_akhiran(sisa, daftar_akhiran)
    print(f"  Pisah akhiran dari sisa → Kata Dasar: {kata_dasar} | Akhiran: {akhiran}")

    if kata_dasar in kamus:
        kata_terjemahan = kamus[kata_dasar]
        awalan_baru, akhiran_baru = ganti_awalan_akhiran(awalan, akhiran)
        hasil = awalan_baru + kata_terjemahan + akhiran_baru
        print(f"  Ditemukan setelah pisah awalan & akhiran: {kata_dasar} → {kata_terjemahan}")
        print(f"  Hasil akhir: {hasil}")
        return kembalikan_kapitalisasi(kata, hasil)

    # 5. Fallback: pisah akhiran langsung dari kata utuh
    kata_dasar2, akhiran2 = pisah_akhiran(kata_kecil, daftar_akhiran)
    print(f"  Fallback: Pisah akhiran dari kata asli → Dasar: {kata_dasar2} | Akhiran: {akhiran2}")
    if kata_dasar2 in kamus:
        kata_terjemahan = kamus[kata_dasar2]
        awalan_baru, akhiran_baru = ganti_awalan_akhiran('', akhiran2)
        hasil = awalan_baru + kata_terjemahan + akhiran_baru
        print(f"  Fallback berhasil → {kata_dasar2} → {kata_terjemahan}")
        print(f"  Hasil akhir (fallback): {hasil}")
        return kembalikan_kapitalisasi(kata, hasil)

    # 6. Gagal → kembalikan kata asli
    print(f" Tidak ditemukan di kamus. Kembalikan kata asli: {kata}")
    return kata
