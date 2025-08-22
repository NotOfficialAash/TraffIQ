import { useEffect, useRef, useState } from 'react';
import '../styles/AccidentAlert.css';

function AccidentAlert({ onDecision }) {
  const videoRef = useRef(null);
  const wsRef = useRef(null);
  const [accidentDetails, setAccidentDetails] = useState({
    location: "Loading...",
    timestamp: "Loading...",
    severity: "Loading..."
  });

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'video_frame' && videoRef.current) {
        videoRef.current.src = `data:image/jpeg;base64,${data.frame}`;
      }
      if (data.type === 'accident_details') {
        setAccidentDetails(data.details);
      }
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    };
  }, []);

  const handleDecision = (decision) => {
    const payload = decision === 'accept' ? 'Accident confirmed' : 'Fake Alert';
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'decision',
        value: payload
      }));
    }
    // Tell App to show the left toast and navigate back
    onDecision?.(decision);
  };

  return (
    <div className="accident-alert">
      <h2>ACCIDENT DETECTED</h2>
      <div className="content-container">
        <div className="video-container">
          <img ref={videoRef} alt="Live feed" className="video-feed" />
        </div>
        <div className="details-container">
          <div className="accident-details">
            <h3>Accident Details</h3>
            <div className="detail-item">
              <span className="detail-label">Location:</span>
              <span className="detail-value">{accidentDetails.location}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Time:</span>
              <span className="detail-value">{accidentDetails.timestamp}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Severity:</span>
              <span className="detail-value">{accidentDetails.severity}</span>
            </div>
          </div>
          <div className="decision">
            <button className="decision-accept" onClick={() => handleDecision('accept')}>
              ✓ Accept
            </button>
            <button className="decision-reject" onClick={() => handleDecision('reject')}>
              ✕ Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AccidentAlert;
