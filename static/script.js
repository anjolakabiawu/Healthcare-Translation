document.addEventListener("DOMContentLoaded", function() {
    const transcriptEl = document.getElementById("transcript");
    const translatedTextEl = document.getElementById("translatedText");
    const errorMessageEl = document.getElementById("errorMessage");
    const historyList = document.getElementById("chatWindow");

    const startRecordingButton = document.getElementById("startRecording");
    const stopRecordingButton = document.getElementById("stopRecording");
    const translateButton = document.getElementById("translateButton");
    const speakButton = document.getElementById("speakButton");

    let mediaRecorder;
    let audioChunks = [];

    // Speech-to-Text
    startRecordingButton.addEventListener("click", async function() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Your browser does not support audio recording.");
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true});
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, {type: 'audio/wav'});
                audioChunks = [];

                errorMessageEl.textContent = "Transcribing... PLease wait.";
                startRecordingButton.classList.remove("is_recording");

                fetch("api/transcribe", {
                    method: "POST",
                    body: audioBlob,
                })
                .then(response => response.json())
                .then(data => {
                    if (data.text) {
                        transcriptEl.value = data.text;
                        errorMessageEl.textContent = "";
                        translateButton.style.backgroundColor = "#ffc107";
                        translateButton.textContent = "Confirm & Translate";
                    } else {
                        errorMessageEl.textContent = "Transcription failed: " + (data.error || "Unknown error");
                    }
                })
                .catch(error => {
                    errorMessageEl.textContent = "Error during transcription: " + error;
                });
            };

            mediaRecorder.start();
            startRecordingButton.disabled = true;
            stopRecordingButton.disabled = false;
            startRecordingButton.classList.add("is-recording");
            errorMessageEl.textContent = "Recording...";
        } catch (err) {
            errorMessageEl.textContent = "Error starting recording: " + err.message;
        }
    });

    stopRecordingButton.addEventListener("click", function() {
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }
        startRecordingButton.disabled = false;
            stopRecordingButton.disabled = true;
            startRecordingButton.classList.remove("is-recording");
            errorMessageEl.textContent = "";
    });

    // Translation
    translateButton.addEventListener("click", function() {
        const text = transcriptEl.value;
        const targetLanguage = document.getElementById("targetLanguage").value;

        if (!text.trim()) {
            errorMessageEl.textContent = "Please enter text to translate.";
            return;
        }

        errorMessageEl.textContent = "Translating...";

        fetch("/api/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, target_language: targetLanguage })
        })
        .then(response => response.json())
        .then(data => {
            errorMessageEl.textContent = "";
            if (data.translated_text) {
                translatedTextEl.textContent = data.translated_text;
                
                // Create user bubble
                const userBubble = document.createElement("div");
                userBubble.className = "chat-bubble user-bubble";
                userBubble.textContent = text;
                chatWindow.appendChild(userBubble);

                // Create translated bubble
                const translatedBubble = document.createElement("div");
                translatedBubble.className = "chat-bubble translated-bubble";
                translatedBubble.textContent = data.translated_text;
                chatWindow.appendChild(translatedBubble);

                // Auto-scroll to the bottom of the chat window
                chatWindow.scrollTop = chatWindow.scrollHeight;
            } else {
                errorMessageEl.textContent = "Translation failed: " + data.error;
            }
        })
        .catch(error => {
            errorMessageEl.textContent = "Error: " + error;
        });
        translateButton.textContent = "Translate";
        translateButton.style.backgroundColor = "#007BFF"; // Reset button color
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
