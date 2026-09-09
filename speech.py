from pathlib import Path
from threading import Lock


class SpeechService:
    def __init__(self, config):
        self.indonesia_model_path = Path(config["MODEL_TTS_INDO_PATH"])
        self.minang_model_path = Path(config["MINANG_TTS_MODEL_PATH"])
        self.minang_config_path = Path(config["MINANG_TTS_CONFIG_PATH"])
        self.output_path = Path(config["AUDIO_OUTPUT_PATH"])
        self.indonesia_model = None
        self.indonesia_tokenizer = None
        self.minang_synthesizer = None
        self.lock = Lock()

    def synthesize(self, text, language):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with self.lock:
            if language == "indo":
                self._synthesize_indonesia(text)
            else:
                self._synthesize_minang(text)

        return self.output_path.relative_to(self.output_path.parents[1]).as_posix()

    def _synthesize_indonesia(self, text):
        if not self.indonesia_model_path.exists():
            raise FileNotFoundError(self.indonesia_model_path)

        import numpy as np
        import scipy.io.wavfile
        import torch
        from transformers import AutoTokenizer, VitsModel

        if self.indonesia_model is None or self.indonesia_tokenizer is None:
            self.indonesia_model = VitsModel.from_pretrained(
                self.indonesia_model_path
            )
            self.indonesia_tokenizer = AutoTokenizer.from_pretrained(
                self.indonesia_model_path
            )

        inputs = self.indonesia_tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            waveform = self.indonesia_model(**inputs).waveform

        sampling_rate = getattr(
            self.indonesia_model.config,
            "sampling_rate",
            22050,
        )
        audio = (waveform.numpy().squeeze() * 32767).astype(np.int16)
        scipy.io.wavfile.write(
            self.output_path,
            rate=sampling_rate,
            data=audio,
        )

    def _synthesize_minang(self, text):
        if not self.minang_model_path.exists():
            raise FileNotFoundError(self.minang_model_path)
        if not self.minang_config_path.exists():
            raise FileNotFoundError(self.minang_config_path)

        from TTS.utils.synthesizer import Synthesizer

        if self.minang_synthesizer is None:
            self.minang_synthesizer = Synthesizer(
                tts_checkpoint=str(self.minang_model_path),
                tts_config_path=str(self.minang_config_path),
                use_cuda=False,
            )

        waveform = self.minang_synthesizer.tts(text)
        self.minang_synthesizer.save_wav(waveform, str(self.output_path))
