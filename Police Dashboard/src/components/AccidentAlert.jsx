import { useEffect, useRef } from 'react';
import '../styles/AccidentAlert.css';

function AccidentAlert() {
  const videoRef = useRef(null);
  
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Only update video frame for video_frame type messages
      if (data.type === 'video_frame' && videoRef.current) {
        videoRef.current.src = `data:image/jpeg;base64,${data.frame}`;
      }
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  return (
    <div className="accident-alert">
      <h2>Live Accident Detection Feed</h2>
      <img ref={videoRef} alt="Live feed" className="video-feed" />
    </div>
  );
}

export default AccidentAlert;