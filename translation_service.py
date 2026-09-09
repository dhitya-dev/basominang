from indo_to_minang import terjemahkan_teks as translate_indonesia_to_minang
from minang_to_indo import terjemahkan_teks as translate_minang_to_indonesia


class TranslationService:
    def __init__(self, repository):
        self.repository = repository

    def translate(self, text, direction):
        indonesia_to_minang, minang_to_indonesia, minang_categories = (
            self.repository.get_all()
        )

        if direction == "indo_minang":
            return translate_indonesia_to_minang(text, indonesia_to_minang)

        return translate_minang_to_indonesia(
            text,
            minang_to_indonesia,
            minang_categories,
        )
