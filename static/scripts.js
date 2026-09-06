function clearText(id) {
  document.getElementById(id).value = "";
}

function copyText(id) {
  const textArea = document.getElementById(id);
  textArea.select();
  document.execCommand("copy");
}

function translateText() {
  let inputText = document.getElementById("text1").value;

  fetch("/translate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: inputText }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("text2").value = data.translated_text;
    })
    .catch((error) => console.error("Error:", error));
}
