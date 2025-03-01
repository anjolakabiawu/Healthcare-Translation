import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Button, Modal } from 'react-bootstrap';
import logo from './logo.svg';
import './App.css';

const speakText = (text, language) => {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = getLanguageCode(language);
  window.speechSynthesis.speak(utterance);
};

console.log("Backend URL:", process.env.REACT_APP_BACKEND_URL);

const getLanguageCode = (language) => {
  const languageCodes = {
    // Source and Target Languages
    Arabic: "AR",
    Bulgarian: "BG",
    Czech: "CS",
    Danish: "DA",
    German: "DE",
    Greek: "EL",
    English: "EN-US", // Use "EN-US" or "EN-GB"
    Spanish: "ES",
    Estonian: "ET",
    Finnish: "FI",
    French: "FR",
    Hungarian: "HU",
    Indonesian: "ID",
    Italian: "IT",
    Japanese: "JA",
    Korean: "KO",
    Lithuanian: "LT",
    Latvian: "LV",
    NorwegianBokmål: "NB",
    Dutch: "NL",
    Polish: "PL",
    Portuguese: "PT-PT", // Use "PT-PT" or "PT-BR"
    Romanian: "RO",
    Russian: "RU",
    Slovak: "SK",
    Slovenian: "SL",
    Swedish: "SV",
    Turkish: "TR",
    Ukrainian: "UK",
    Chinese: "ZH-HANS", // Use "ZH-HANS" or "ZH-HANT"
  };
  return languageCodes[language] || 'EN-US'; // Default to English
};

const SpeechToText = ({ setTranscript, inputLanguage, setError }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);

  const startRecording = () => {
    setIsRecording(true);
    setError('');

    // Check if the browser supports the Web Speech API
    if (!('webkitSpeechRecognition' in window)) {
      setError('Your browser does not support speech recognition.');
      setIsRecording(false);
      return;
    }

    // Create a new SpeechRecognition instance
    const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false; // Stop after one sentence
    recognition.interimResults = false; // Only return final results
    recognition.lang = inputLanguage; // Set the language

    // Event handler for when speech is recognized
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log("Recognized speech:", transcript);
      setTranscript(transcript);
      setIsRecording(false);
    };

    // Event handler for errors
    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setError('Speech recognition failed. Please try again.');
      setIsRecording(false);
    };

    // Start speech recognition
    recognition.start();
    setRecognition(recognition);
  };

  const stopRecording = () => {
    if (recognition) {
      recognition.stop();
      setIsRecording(false);
    }
  };

  return (
    <div>
      <button onClick={startRecording} disabled={isRecording}>
        {isRecording ? 'Recording...' : 'Start Speaking'}
      </button>
      <button onClick={stopRecording} disabled={!isRecording}>
        Stop Recording
      </button>
    </div>
  );
};

function App() {
  const [transcript, setTranscript] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('English'); // Default output language
  const [inputLanguage, setInputLanguage] = useState('en-US'); // Default input language
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState([]); // Translation history
  const [showGuide, setShowGuide] = useState(false);

  const languageCodes = {
    English: "EN-US",
    Arabic: "AR",
    Bulgarian: "BG",
    Czech: "CS",
    Danish: "DA",
    German: "DE",
    Greek: "EL",
    Spanish: "ES",
    Estonian: "ET",
    Finnish: "FI",
    French: "FR",
    Hungarian: "HU",
    Indonesian: "ID",
    Italian: "IT",
    Japanese: "JA",
    Korean: "KO",
    Lithuanian: "LT",
    Latvian: "LV",
    NorwegianBokmål: "NB",
    Dutch: "NL",
    Polish: "PL",
    Portuguese: "PT-PT", // Use "PT-PT" or "PT-BR"
    Romanian: "RO",
    Russian: "RU",
    Slovak: "SK",
    Slovenian: "SL",
    Swedish: "SV",
    Turkish: "TR",
    Ukrainian: "UK",
    Chinese: "ZH-HANS", // Use "ZH-HANS" or "ZH-HANT"
  };

  const handleTranslate = async () => {
    setIsLoading(true);
    setError('');
    try {
      const targetLanguageCode = languageCodes[targetLanguage];
      if (!transcript.trim()) {
        setError('No text provided for translation.');
        setIsLoading(false);
        return;
      }

      console.log("Sending translation request...")
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}translate`, {
        text: transcript,
        target_language: targetLanguageCode, // Use the mapped code
      });

      console.log("Backend response:", response.data);
      const translatedText = response.data.translated_text;
      setTranslatedText(response.data.translated_text);
      setHistory([...history, { input: transcript, output: translatedText }]);
    } catch (error) {
      console.error("Error details:", error.response);
      setError('Translation failed. Please try again.');
      console.error('Error translating text:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className='App-logo' alt='logo' />
        <h1>Healthcare Translation App</h1>

        {/* Help Button */}
        <Button variant='info' onClick={() => setShowGuide(true)} style={{position: 'absolute',
          top: '10px', right: '10px'
        }}>
          Help
        </Button>

        {/* Input Language Selection */}
        <div>
          <label>Input Language: </label>
          <select
            value={inputLanguage}
            onChange={(e) => setInputLanguage(e.target.value)}
          >
              <option value="en-US">English (US)</option>
              <option value="es-ES">Spanish</option>
              <option value="fr-FR">French</option>
              <option value="de-DE">German</option>
              <option value="zh-HANS">Chinese (Simplified)</option>
              <option value="ar-SA">Arabic</option>
              <option value="ja-JP">Japanese</option>
              <option value="ru-RU">Russian</option>
              <option value="pt-PT">Portuguese (Portugal)</option>
              <option value="it-IT">Italian</option>
              <option value="ko-KR">Korean</option>
              <option value="tr-TR">Turkish</option>
              <option value="nl-NL">Dutch</option>
              <option value="sv-SE">Swedish</option>
              <option value="pl-PL">Polish</option>
            </select>
        </div>

        {/* Speech-to-Text Component */}
        < SpeechToText setTranscript={setTranscript} inputLanguage={inputLanguage} setError={setError} />

        {/* Transcript Display */}
        <textarea
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder='Enter text to translate...'
        />

        {/* Output Language Selection */}
        <div>
          <label>Output Language: </label>
          <select
            value={targetLanguage}
            onChange={(e) => setTargetLanguage(e.target.value)}
          >
            <option value="English">English (US)</option>
            <option value="Spanish">Spanish</option>
            <option value="French">French</option>
            <option value="German">German</option>
            <option value="Chinese">Chinese (Simplified)</option>
            <option value="Arabic">Arabic</option>
            <option value="Japanese">Japanese</option>
            <option value="Russian">Russian</option>
            <option value="Portuguese">Portuguese (Portugal)</option>
            <option value="Italian">Italian</option>
            <option value="Korean">Korean</option>
            <option value="Turkish">Turkish</option>
            <option value="Dutch">Dutch</option>
            <option value="Swedish">Swedish</option>
            <option value="Polish">Polish</option>
          </select>
        </div>

        {/* Translate Button */}
        {isLoading ? (
          <div>Loading...</div> // Adds a spinner
        ) : (
          <button onClick={handleTranslate}>Translate</button>
        )}
        
        {/* Error Message */}
        {error && <p style={{ color: 'red'}}>{error}</p>}

        {/* Translated Text Display */}
        <p>{translatedText}</p>

        {/* Speak Button */}
        <button onClick={() => speakText(translatedText, targetLanguage)}>Speak</button>

        {/* Translation History */}
        <div style={{ marginTop: '20px'}}>
          <h3>Translation History</h3>
          <ul>
            {history.map((item, index) => (
              <li key={index}>
                <strong>Input:</strong> {item.input} <br />
                <strong>Output:</strong> {item.output}
              </li>
            ))}
          </ul>
        </div>
      </header>

      {/* User Guide Modal */}
      <Modal show={showGuide} onHide={() => setShowGuide(false)} 
      size="lg"
      enforceFocus={false}
      restoreFocus={false}>
        <Modal.Header closeButton>
          <Modal.Title>User Guide</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ maxHeight: '70vh', overflowY: 'auto'}}>
          <h2>Healthcare Translation Web App - User Guide</h2>
          <p>This guide will walk you through how to use the Healthcare Translation Web App.</p>

          <h3>Features</h3>
          <ul>
            <li><strong>Voice-to-Text</strong>: Convert spoken input into text.</li>
            <li><strong>Real-Time Translation</strong>: Translate text into multiple languages.</li>
            <li><strong>Audio Playback</strong>: Listen to the translated text.</li>
            <li><strong>Translation History</strong>: View past translations.</li>
          </ul>

          <h3>How to Use the App</h3>
          <ol>
            <li><strong>Select Input Language</strong>: Choose the language of the spoken input from the <strong>Input Language</strong> dropdown.</li>
            <li><strong>Start Speaking</strong>: Click the <strong>Start Speaking</strong> button to begin recording your voice. The app will convert your speech into text and display it in the <strong>Transcript</strong> box.</li>
            <li><strong>Select Output Language</strong>: Choose the language you want to translate the text into from the <strong>Output Language</strong> dropdown.</li>
            <li><strong>Translate</strong>: Click the <strong>Translate</strong> button to translate the text. The translated text will appear below the <strong>Transcript</strong> box.</li>
            <li><strong>Listen to Translation</strong>: Click the <strong>Speak</strong> button to hear the translated text.</li>
            <li><strong>View Translation History</strong>: Past translations are displayed in the <strong>Translation History</strong> section at the bottom of the page.</li>
          </ol>

          <h3>Supported Languages</h3>
          <ul>
            <li><strong>Input Languages</strong>: English, Spanish, French, German, Chinese, Hindi.</li>
            <li><strong>Output Languages</strong>: English, Spanish, French, German, Chinese, Hindi.</li>
          </ul>

          <h3>Troubleshooting</h3>
          <ul>
            <li><strong>No Audio Detected</strong>: Ensure your microphone is working and you’ve selected the correct input language.</li>
            <li><strong>Translation Failed</strong>: Check your internet connection and try again.</li>
          </ul>

          <h3>Privacy and Security</h3>
          <p>Your data is processed securely and not stored. The app uses HTTPS for secure communication.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowGuide(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default App;
