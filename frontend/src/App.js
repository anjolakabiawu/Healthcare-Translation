import React, { useState } from 'react';
import axios from 'axios';
import { Button, Modal } from 'react-bootstrap';
import logo from './logo.svg';
import './App.css';

const speakText = (text, language) => {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = getLanguageCode(language);
  window.speechSynthesis.speak(utterance);
};

const getLanguageCode = (language) => {
  const languageCodes = {
    English: 'en-US',
    Spanish: 'es-ES',
    French: 'fr-FR',
    German: 'de-DE',
    Chinese: 'zh-CN',
    Hindi: 'hi-IN',
  };
  return languageCodes[language] || 'es-US'; // Default to English
};

const SpeechToText = ({ setTranscript, inputLanguage }) => {
  const [isListening, setIsListening] = useState(false);

  const startListening = () => {
    setIsListening(true);
    try {
      // Use the Web Speech API for speech-to-text
      const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      recognition.lang = inputLanguage;
      recognition.interimResults = false;

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setTranscript(transcript);
      };

      recognition.start();
    } catch (error) {
      console.error('Error transcribing speech:', error);
    } finally {
      setIsListening(false);
    }
  };

  return (
    <div>
      <button onClick={startListening} disabled={isListening}>
        {isListening ? 'Listening...' : 'Start Speaking'}
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

  const handleTranslate = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.post('/translate', {
        text: transcript,
        target_language: targetLanguage, // Use selected language
      });
      const translatedText = response.data.translated_text;
      setTranslatedText(response.data.translated_text);
      setHistory([...history, { input: transcript, output: translatedText }]);
    } catch (error) {
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
              <option value={"en-US"}>English</option>
              <option value={"es-ES"}>Spanish</option>
              <option value={"fr-FR"}>French</option>
              <option value={"de-DE"}>German</option>
              <option value={"zh-CN"}>Chinese</option>
              <option value={"hi-IN"}>Hindi</option>
            </select>
        </div>

        {/* Speech-to-Text Component */}
        < SpeechToText setTranscript={setTranscript} inputLanguage={inputLanguage} />

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
            <option value={"English"}>English</option>
            <option value={"Spanish"}>Spanish</option>
            <option value={"French"}>French</option>
            <option value={"German"}>German</option>
            <option value={"Chinese"}>Chinese</option>
            <option value={"Hindi"}>Hindi</option>
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
