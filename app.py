import os
import torch
import scipy.io.wavfile
import numpy as np
from flask import Flask, render_template, request, jsonify
# Library TTS INDO
from transformers import VitsModel, AutoTokenizer
#Library TTS Minang
from TTS.utils.synthesizer import Synthesizer
import mysql.connector
from indo_to_minang import terjemahkan_teks as indo_to_minang_translate
from minang_to_indo import terjemahkan_teks as minang_to_indo_translate

app = Flask(__name__)

# 🔗 Koneksi ke database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="terjemahan"
)
cursor = conn.cursor()

# 🔍 Ambil data kamus
cursor.execute("SELECT kata_indo, kata_minang FROM indonesia")
data_indo_minang = cursor.fetchall()

cursor.execute("SELECT kata_minang, kata_indo FROM minangkabau")
data_minang_indo = cursor.fetchall()

# 🔤 Bentuk dictionary lower-case
dictionary_indonesia_to_minang = {ind.lower(): minang.lower() for ind, minang in data_indo_minang}
dictionary_minang_to_indonesia = {minang.lower(): ind.lower() for minang, ind in data_minang_indo}

# 🔄 Fungsi terjemahan dinamis
def translate_dynamic(text, lang):
    if lang == "indo_minang":
        return indo_to_minang_translate(text, dictionary_indonesia_to_minang)
    else:
        return minang_to_indo_translate(text, dictionary_minang_to_indonesia)

# 📁 Path model TTS
MODEL_TTS_INDO_PATH = "C:/Users/MuhammadArifAditya/Documents/TAHUN_2026/BasoMinang/TTS_Indo"
MINANG_TTS_MODEL_PATH = "C:/Users/MuhammadArifAditya/Documents/TAHUN_2026/BasoMinang/TTS_Minang/best_model.pth"
MINANG_TTS_CONFIG_PATH = "C:/Users/MuhammadArifAditya/Documents/TAHUN_2026/BasoMinang/TTS_Minang/config_Agam.json"
AUDIO_PATH = "static/output.wav"

# 🌐 Variabel global (lazy load)
model_indo = None
tokenizer_indo = None
synthesizer_minang = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    input_text = data.get("text", "")
    lang_mode = data.get("lang", "indo_minang")
    translated_text = translate_dynamic(input_text, lang_mode)
    return jsonify({"translated_text": translated_text})

@app.route("/speak", methods=["POST"])
def speak():
    global model_indo, tokenizer_indo, synthesizer_minang

    data = request.get_json()
    text = data.get("text", "")
    lang = data.get("lang", "indo")

    if not text:
        return jsonify({"error": "Teks tidak boleh kosong"}), 400

    if not os.path.exists("static"):
        os.makedirs("static")

    try:
        if lang == "indo":
            # model Indo
            if model_indo is None or tokenizer_indo is None:
                model_indo = VitsModel.from_pretrained(MODEL_TTS_INDO_PATH)
                tokenizer_indo = AutoTokenizer.from_pretrained(MODEL_TTS_INDO_PATH)

            inputs = tokenizer_indo(text, return_tensors="pt")
            with torch.no_grad():
                output = model_indo(**inputs).waveform
            sampling_rate = getattr(model_indo.config, "sampling_rate", 22050)
            output_audio = (output.numpy().squeeze() * 32767).astype(np.int16)
            scipy.io.wavfile.write(AUDIO_PATH, rate=sampling_rate, data=output_audio)

        else:
            # model Minang
            if synthesizer_minang is None:
                synthesizer_minang = Synthesizer(
                    tts_checkpoint=MINANG_TTS_MODEL_PATH,
                    tts_config_path=MINANG_TTS_CONFIG_PATH,
                    use_cuda=False
                )
            wav = synthesizer_minang.tts(text)
            synthesizer_minang.save_wav(wav, AUDIO_PATH)

        return jsonify({"audio_url": "/" + AUDIO_PATH})

    except Exception as e:
        print(f"Terjadi kesalahan saat sintesis suara: {e}")
        return jsonify({"error": "Terjadi kesalahan saat menghasilkan audio"}), 500

if __name__ == "__main__":
    app.run(debug=True)
