import { useState, useEffect, useRef } from 'react';
import './SpeechBubble.css';

const TYPING_SPEED = 30; // ms per character

export default function SpeechBubble({ text }) {
  const [displayed, setDisplayed] = useState('');
  const [isTyping, setIsTyping] = useState(true);
  const timeoutRef = useRef(null);
  const indexRef = useRef(0);

  useEffect(() => {
    indexRef.current = 0;

    if (!text) return;

    const typeNext = () => {
      if (indexRef.current < text.length) {
        indexRef.current++;
        setDisplayed(text.slice(0, indexRef.current));
        timeoutRef.current = setTimeout(typeNext, TYPING_SPEED);
      } else {
        setIsTyping(false);
      }
    };

    // Reset and start typing after a small delay
    timeoutRef.current = setTimeout(() => {
      setDisplayed('');
      setIsTyping(true);
      typeNext();
    }, 300);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [text]);

  if (!text) return null;

  return (
    <div className="speech-bubble-container">
      <div className="speech-bubble">
        {displayed}
        <span className={`cursor ${!isTyping ? 'hidden' : ''}`} />
      </div>
    </div>
  );
}
