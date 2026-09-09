import re


SUFFIX_CONVERSIONS = {
    "lah": "lah",
    "nyo": "nya",
    "kan": "kan",
    "an": "an",
    "i": "i",
}
PREFIX_CONVERSIONS = {
    "man": "men",
    "pang": "peng",
    "basi": "bersi",
    "ka": "ke",
    "sa": "se",
}
PREFIXES = [
    "mampa",
    "bapa",
    "tapa",
    "sapa",
    "baku",
    "pang",
    "basi",
    "pan",
    "man",
    "bo",
    "ba",
    "ma",
    "pa",
    "ta",
    "no",
    "di",
    "ka",
    "sa",
]
SUFFIXES = ["lah", "nyo", "kan", "an", "i"]
NOUN_CATEGORIES = {
    "Kata Benda",
    "Kata Benda Status",
    "Kata Benda Alat",
    "Kata Benda Makhluk Hidup",
}
ADJECTIVE_CATEGORIES = {"Kata Sifat", "Kata Sifat Kebiasaan"}


def pecah_teks(teks):
    return re.findall(r"\w+(?:-\w+)*|[^\w\s]", teks, flags=re.UNICODE)


def terjemahkan_teks(teks, kamus, kategori=None):
    categories = kategori or {}
    translated_tokens = [
        terjemahkan_kata(token, kamus, categories) for token in pecah_teks(teks)
    ]
    return re.sub(r"\s+([.,!?;])", r"\1", " ".join(translated_tokens))


def pisah_akhiran(kata, daftar_akhiran, kamus):
    if kata in kamus:
        return kata, ""

    for suffix in sorted(daftar_akhiran, key=len, reverse=True):
        if kata.endswith(suffix) and len(kata) > len(suffix):
            return kata[: -len(suffix)], suffix

    return kata, ""


def pisah_awalan(kata, daftar_awalan, kamus):
    for prefix in sorted(daftar_awalan, key=len, reverse=True):
        remainder = kata[len(prefix) :]
        if kata.startswith(prefix) and remainder in kamus:
            return prefix, remainder
    return "", kata


def convert_prefix(prefix, category):
    converted = PREFIX_CONVERSIONS.get(prefix, prefix)

    if prefix == "sapa" and category == "Kata Bilangan":
        return "seper"
    if prefix == "tapa" and category in {"Kata Bilangan", *ADJECTIVE_CATEGORIES}:
        return "dijadikan "
    if prefix == "bapa" and category in {"Kata Bilangan", *ADJECTIVE_CATEGORIES}:
        return "dijadikan "
    if prefix == "ta" and category in {
        "Kata Kerja",
        *ADJECTIVE_CATEGORIES,
        *NOUN_CATEGORIES,
    }:
        return "ter"
    if prefix == "no" and category == "Kata Kerja":
        return "di"
    if prefix == "mampa":
        if category == "Kata Bilangan":
            return "membagi "
        if category in {*NOUN_CATEGORIES, *ADJECTIVE_CATEGORIES}:
            return "memper"
    if prefix == "baku" and category == "Kata Kerja":
        return "ber"
    if prefix == "pa":
        if category == "Kata Sifat Kebiasaan":
            return "pe"
        if category == "Kata Sifat":
            return "memper"
        if category == "Kata Benda Status":
            return "menjadikan "
        if category == "Kata Benda Makhluk Hidup":
            return "memanggilkan "
        if category == "Kata Bilangan":
            return "bagi "
    if prefix == "pan":
        if category == "Kata Kerja":
            return "pen"
        if category == "Kata Benda Alat":
            return "peng"
        if category == "Kata Sifat Kebiasaan":
            return "pe"
    if prefix == "ma" and category in {
        "Kata Kerja",
        *NOUN_CATEGORIES,
        *ADJECTIVE_CATEGORIES,
    }:
        return "me"
    if prefix == "bo" and category == "Kata Kerja Pasif":
        return "di"
    if prefix == "ba" and category in {
        "Kata Kerja",
        "Kata Bilangan",
        *NOUN_CATEGORIES,
        *ADJECTIVE_CATEGORIES,
    }:
        return "ber"

    return converted


def kembalikan_kapitalisasi(asli, terjemahan):
    if asli.isupper():
        return terjemahan.upper()
    if asli[:1].isupper():
        return terjemahan[:1].upper() + terjemahan[1:]
    return terjemahan


def terjemahkan_kata(kata, kamus, kategori=None):
    categories = kategori or {}
    normalized_word = kata.lower()

    if normalized_word in kamus:
        return kembalikan_kapitalisasi(kata, kamus[normalized_word])

    root_word, suffix = pisah_akhiran(normalized_word, SUFFIXES, kamus)
    if root_word in kamus:
        result = kamus[root_word] + SUFFIX_CONVERSIONS.get(suffix, "")
        return kembalikan_kapitalisasi(kata, result)

    prefix, root_word = pisah_awalan(root_word, PREFIXES, kamus)
    if root_word not in kamus:
        return kata

    category = categories.get(root_word)
    converted_prefix = convert_prefix(prefix, category)
    converted_suffix = SUFFIX_CONVERSIONS.get(suffix, "")
    result = converted_prefix + kamus[root_word] + converted_suffix
    return kembalikan_kapitalisasi(kata, result)
