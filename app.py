import os

from flask import Flask, jsonify, render_template, request, url_for

from config import Config
from database import DatabaseUnavailableError, DictionaryRepository
from speech import SpeechService
from translation_service import TranslationService


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    repository = DictionaryRepository(app.config)
    translator = TranslationService(repository)
    speech = SpeechService(app.config)

    app.extensions["dictionary_repository"] = repository
    app.extensions["translation_service"] = translator
    app.extensions["speech_service"] = speech

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/translate")
    def translate():
        payload = request.get_json(silent=True) or {}
        raw_text = payload.get("text", "")
        direction = payload.get("lang", "indo_minang")

        if not isinstance(raw_text, str):
            return jsonify({"error": "Teks harus berupa string."}), 400
        text = raw_text.strip()
        if not text:
            return jsonify({"error": "Teks tidak boleh kosong."}), 400
        if len(text) > app.config["MAX_TEXT_LENGTH"]:
            return jsonify({"error": "Teks melebihi batas karakter."}), 400
        if direction not in {"indo_minang", "minang_indo"}:
            return jsonify({"error": "Arah terjemahan tidak valid."}), 400

        try:
            translated_text = translator.translate(text, direction)
        except DatabaseUnavailableError as error:
            app.logger.error("Database unavailable: %s", error)
            return jsonify({"error": "Kamus belum dapat diakses."}), 503

        return jsonify({"translated_text": translated_text})

    @app.post("/speak")
    def speak():
        payload = request.get_json(silent=True) or {}
        raw_text = payload.get("text", "")
        language = payload.get("lang", "indo")

        if not isinstance(raw_text, str):
            return jsonify({"error": "Teks harus berupa string."}), 400
        text = raw_text.strip()
        if not text:
            return jsonify({"error": "Teks tidak boleh kosong."}), 400
        if len(text) > app.config["MAX_TEXT_LENGTH"]:
            return jsonify({"error": "Teks melebihi batas karakter."}), 400
        if language not in {"indo", "minang"}:
            return jsonify({"error": "Bahasa suara tidak valid."}), 400

        try:
            filename = speech.synthesize(text, language)
        except (FileNotFoundError, RuntimeError) as error:
            app.logger.error("Speech synthesis failed: %s", error)
            return jsonify({"error": "Model suara belum siap digunakan."}), 503
        except Exception:
            app.logger.exception("Unexpected speech synthesis error")
            return jsonify({"error": "Gagal menghasilkan audio."}), 500

        return jsonify({"audio_url": url_for("static", filename=filename)})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
