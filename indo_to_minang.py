import re


PREFIXES = [
    "memper",
    "seper",
    "meng",
    "bersi",
    "peng",
    "men",
    "pen",
    "ber",
    "ter",
    "be",
    "me",
    "di",
    "ke",
    "pe",
    "se",
]
SUFFIXES = ["lah", "kan", "kah", "nya", "an", "i"]
PREFIX_CONVERSIONS = {
    "memper": "mampa",
    "seper": "sapa",
    "meng": "ma",
    "men": "man",
    "peng": "pang",
    "pen": "pan",
    "bersi": "basi",
    "ber": "ba",
    "be": "ba",
    "ter": "ta",
    "me": "ma",
    "di": "di",
    "ke": "ka",
    "pe": "pa",
    "se": "sa",
}
SUFFIX_CONVERSIONS = {
    "lah": "lah",
    "an": "an",
    "i": "i",
    "kan": "kan",
    "kah": "",
    "nya": "nyo",
}


def terjemahkan_teks(teks, kamus):
    translated_tokens = [terjemahkan_kata(token, kamus) for token in pecah_teks(teks)]
    return re.sub(r"\s+([.,!?;])", r"\1", " ".join(translated_tokens))


def pecah_teks(teks):
    return re.findall(r"\w+(?:-\w+)*|[^\w\s]", teks, flags=re.UNICODE)


def pisah_awalan(kata, daftar_awalan, kamus):
    sorted_prefixes = sorted(daftar_awalan, key=len, reverse=True)

    for prefix in sorted_prefixes:
        if kata.startswith(prefix) and kata[len(prefix) :] in kamus:
            return prefix, kata[len(prefix) :]

    for prefix in sorted_prefixes:
        if kata.startswith(prefix):
            return prefix, kata[len(prefix) :]

    return "", kata


def pisah_akhiran(kata, daftar_akhiran):
    for suffix in sorted(daftar_akhiran, key=len, reverse=True):
        if kata.endswith(suffix) and len(kata) > len(suffix):
            return kata[: -len(suffix)], suffix
    return kata, ""


def ganti_awalan_akhiran(awalan, akhiran):
    return (
        PREFIX_CONVERSIONS.get(awalan, awalan),
        SUFFIX_CONVERSIONS.get(akhiran, akhiran),
    )


def kembalikan_kapitalisasi(asli, terjemahan):
    if asli.isupper():
        return terjemahan.upper()
    if asli[:1].isupper():
        return terjemahan[:1].upper() + terjemahan[1:]
    return terjemahan


def terjemahkan_kata(kata, kamus):
    normalized_word = kata.lower()

    if normalized_word in kamus:
        return kembalikan_kapitalisasi(kata, kamus[normalized_word])

    prefix, remainder = pisah_awalan(normalized_word, PREFIXES, kamus)

    if remainder in kamus:
        converted_prefix, _ = ganti_awalan_akhiran(prefix, "")
        result = converted_prefix + kamus[remainder]
        return kembalikan_kapitalisasi(kata, result)

    root_word, suffix = pisah_akhiran(remainder, SUFFIXES)
    if root_word in kamus:
        converted_prefix, converted_suffix = ganti_awalan_akhiran(prefix, suffix)
        result = converted_prefix + kamus[root_word] + converted_suffix
        return kembalikan_kapitalisasi(kata, result)

    root_word, suffix = pisah_akhiran(normalized_word, SUFFIXES)
    if root_word in kamus:
        _, converted_suffix = ganti_awalan_akhiran("", suffix)
        result = kamus[root_word] + converted_suffix
        return kembalikan_kapitalisasi(kata, result)

    return kata
