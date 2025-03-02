document.addEventListener("DOMContentLoaded", function() {
    const transcriptEl = document.getElementById("transcript");
    const translatedTextEl = document.getElementById("translatedText");
    const errorMessageEl = document.getElementById("errorMessage");
    const historyList = document.getElementById("historyList");

    const startRecordingButton = document.getElementById("startRecording");
    const stopRecordingButton = document.getElementById("stopRecording");
    const translateButton = document.getElementById("translateButton");
    const speakButton = document.getElementById("speakButton");

    let recognition;

    // Speech-to-Text
    startRecordingButton.addEventListener("click", function() {
        if (!('webkitSpeechRecognition' in window)) {
            alert("Your browser does not support speech recognition.");
            return;
        }

        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = document.getElementById("inputLanguage").value;

        recognition.onresult = function(event) {
            transcriptEl.value = event.results[0][0].transcript;
        };

        recognition.onerror = function(event) {
            errorMessageEl.textContent = "Speech recognition error: " + event.error;
        };

        recognition.start();
        startRecordingButton.disabled = true;
        stopRecordingButton.disabled = false;
    });

    stopRecordingButton.addEventListener("click", function() {
        if (recognition) {
            recognition.stop();
        }
        startRecordingButton.disabled = false;
        stopRecordingButton.disabled = true;
    });

    // Translation
    translateButton.addEventListener("click", function() {
        const text = transcriptEl.value;
        const targetLanguage = document.getElementById("targetLanguage").value;

        if (!text.trim()) {
            errorMessageEl.textContent = "Please enter text to translate.";
            return;
        }

        fetch("/api/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, target_language: targetLanguage })
        })
        .then(response => response.json())
        .then(data => {
            if (data.translated_text) {
                translatedTextEl.textContent = data.translated_text;
                errorMessageEl.textContent = "";

                // Add to history
                const listItem = document.createElement("li");
                listItem.textContent = `Input: ${text} → Output: ${data.translated_text}`;
                historyList.appendChild(listItem);
            } else {
                errorMessageEl.textContent = "Translation failed: " + data.error;
            }
        })
        .catch(error => {
            errorMessageEl.textContent = "Error: " + error;
        });
    });

    // Speak Translated Text
    speakButton.addEventListener("click", function() {
        const utterance = new SpeechSynthesisUtterance(translatedTextEl.textContent);
        utterance.lang = document.getElementById("targetLanguage").value;
        speechSynthesis.speak(utterance);
    });

    // Help Modal
    const helpModal = document.getElementById("helpModal");
    document.getElementById("helpButton").addEventListener("click", function() {
        helpModal.style.display = "block";
    });
    document.querySelector(".close").addEventListener("click", function() {
        helpModal.style.display = "none";
    });
});
