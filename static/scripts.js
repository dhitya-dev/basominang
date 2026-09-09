const elements = {
  input: document.getElementById("text1"),
  output: document.getElementById("text2"),
  inputLanguage: document.getElementById("lang1"),
  outputLanguage: document.getElementById("lang2"),
  inputLabel: document.getElementById("label1"),
  outputLabel: document.getElementById("label2"),
  characterCount: document.getElementById("characterCount"),
  translateButton: document.getElementById("translateButton"),
  audioPlayer: document.getElementById("audioPlayer"),
  audioSource: document.getElementById("audioSource"),
};

function showMessage(message) {
  window.alert(message);
}

function clearText(id) {
  document.getElementById(id).value = "";
  updateCharacterCount();
}

function updateCharacterCount() {
  elements.characterCount.textContent = `${elements.input.value.length} / 1000`;
}

async function copyText(id) {
  const textArea = document.getElementById(id);
  if (!textArea.value) return;

  try {
    await navigator.clipboard.writeText(textArea.value);
  } catch {
    textArea.select();
    document.execCommand("copy");
  }
}

async function readJson(response) {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Permintaan tidak dapat diproses.");
  }
  return data;
}

async function translateText() {
  const text = elements.input.value.trim();
  if (!text) {
    showMessage("Masukkan teks terlebih dahulu.");
    return;
  }

  const direction =
    elements.input.dataset.lang === "indo" ? "indo_minang" : "minang_indo";
  const originalContent = elements.translateButton.innerHTML;
  elements.translateButton.disabled = true;
  elements.translateButton.innerHTML =
    '<span class="material-symbols-rounded animate-spin text-[18px]">progress_activity</span><span>Menerjemahkan...</span>';

  try {
    const response = await fetch("/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, lang: direction }),
    });
    const data = await readJson(response);
    elements.output.value = data.translated_text;
  } catch (error) {
    showMessage(error.message);
  } finally {
    elements.translateButton.disabled = false;
    elements.translateButton.innerHTML = originalContent;
  }
}

function swapLanguages() {
  const inputLanguage = elements.inputLanguage.textContent.trim();
  const outputLanguage = elements.outputLanguage.textContent.trim();
  const inputText = elements.input.value;

  elements.inputLanguage.textContent = outputLanguage;
  elements.outputLanguage.textContent = inputLanguage;
  elements.inputLabel.textContent = outputLanguage;
  elements.outputLabel.textContent = inputLanguage;
  elements.input.value = elements.output.value;
  elements.output.value = inputText;

  const inputCode = elements.input.dataset.lang;
  elements.input.dataset.lang = elements.output.dataset.lang;
  elements.output.dataset.lang = inputCode;
  updateCharacterCount();
}

async function playAudio(textareaId) {
  const textArea = document.getElementById(textareaId);
  const text = textArea.value.trim();
  if (!text) {
    showMessage("Tidak ada teks untuk diucapkan.");
    return;
  }

  try {
    const response = await fetch("/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, lang: textArea.dataset.lang }),
    });
    const data = await readJson(response);
    elements.audioSource.src = `${data.audio_url}?v=${Date.now()}`;
    elements.audioPlayer.load();
    await elements.audioPlayer.play();
  } catch (error) {
    showMessage(error.message);
  }
}

elements.input.addEventListener("input", updateCharacterCount);
elements.input.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    translateText();
  }
});

window.clearText = clearText;
window.copyText = copyText;
window.translateText = translateText;
window.swapLanguages = swapLanguages;
window.playAudio = playAudio;
