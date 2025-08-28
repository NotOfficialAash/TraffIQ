import { useEffect, useRef } from 'react';
import '../styles/AccidentAlert.css';

function AccidentAlert({ accidentData, onDecision }) {
  const videoRef = useRef(null);
  const wsRef = useRef(null);

  // WebSocket connection for live video feed
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'video_frame' && videoRef.current) {
        videoRef.current.src = `data:image/jpeg;base64,${data.frame}`;
      }
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    };
  }, []);

  const handleDecision = (decision) => {
    let payload = '';
    if (decision === 'accept') payload = 'Accident confirmed';
    else if (decision === 'reject') payload = 'Fake Alert';
    else if (decision === 'acknowledge') payload = 'Accident acknowledged';

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'decision',
          value: payload,
        })
      );
    }

    onDecision?.(decision);
  };

  if (!accidentData) return <div style={{ color: 'white' }}>Loading accident details...</div>;

  // Safe time formatting
  const formatTime = (t) => {
    if (!t) return 'Unknown';
    if (t.toDate && typeof t.toDate === 'function') return t.toDate().toLocaleString();
    if (t instanceof Date) return t.toLocaleString();
    const date = new Date(t);
    return isNaN(date.getTime()) ? 'Unknown' : date.toLocaleString();
  };

  // Convert GeoPoint to string
  const locationStr =
    accidentData.location?._lat != null && accidentData.location?._long != null
      ? `Lat: ${accidentData.location._lat}, Lng: ${accidentData.location._long}`
      : accidentData.location || 'Unknown';

  const severityStr = accidentData.severity ? accidentData.severity.toString().trim().toLowerCase() : '';

  return (
    <div className="accident-alert">
      <h2>ACCIDENT DETECTED</h2>
      <div className="content-container">
        {/* Video feed */}
        <div className="video-container">
          <img ref={videoRef} alt="Live feed" className="video-feed" />
        </div>

        {/* Accident details */}
        <div className="details-container">
          <div className="accident-details">
            <h3>Accident Details</h3>
            <div className="detail-item">
              <span className="detail-label">Location:</span>
              <span className="detail-value">{locationStr}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Time:</span>
              <span className="detail-value">{formatTime(accidentData.time)}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Severity:</span>
              <span className="detail-value">{accidentData.severity || 'Unknown'}</span>
            </div>
          </div>

          {/* Buttons based on severity */}
          <div className="decision">
            {severityStr === 'minor' || (accidentData.ai_conf != null && accidentData.ai_conf < 25) ? (
              <>
                <button className="decision-accept" onClick={() => handleDecision('accept')}>
                  Dispatch ER Services
                </button>
                <button className="decision-reject" onClick={() => handleDecision('reject')}>
                  Flag Fake Detection
                </button>
              </>
            ) : (
              <button className="decision-ack" onClick={() => handleDecision('acknowledge')}>
                ⚠️ Acknowledge
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AccidentAlert;
