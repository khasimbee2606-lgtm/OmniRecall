import { Mic } from "lucide-react";
import "../assets/styles/voiceSearch.css";

function VoiceSearch({ onResult }) {
  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech Recognition is not supported.");
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";
    recognition.start();

    recognition.onresult = (e) => {
      onResult(e.results[0][0].transcript);
    };
  };

  return (
    <button className="voice-btn" onClick={startListening}>
      <Mic size={20} />
    </button>
  );
}

export default VoiceSearch;
