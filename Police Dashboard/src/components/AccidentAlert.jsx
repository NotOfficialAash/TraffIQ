import { useEffect, useRef, useState } from "react";
import { doc, updateDoc } from "firebase/firestore";
import { db } from "./firebase"; // adjust path if needed
import "../styles/AccidentAlert.css";

function AccidentAlert({ accidentData, onDecision }) {
  const videoRef = useRef(null);
  const wsRef = useRef(null);
  const [streaming, setStreaming] = useState(false);

  // WebSocket connection for live video feed
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8765");
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected ✅");
      // 👉 Request video when component mounts
      ws.send(JSON.stringify({ type: "start_video" }));
      setStreaming(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "video_frame" && videoRef.current) {
        videoRef.current.src = `data:image/jpeg;base64,${data.frame}`;
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected ❌");
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        // Stop video before unmounting
        ws.send(JSON.stringify({ type: "stop_video" }));
      }
      ws.close();
    };
  }, []);

  // Safe time formatting
  const formatTime = (t) => {
    if (!t) return "Unknown";
    if (t.toDate && typeof t.toDate === "function")
      return t.toDate().toLocaleString();
    if (t instanceof Date) return t.toLocaleString();
    const date = new Date(t);
    return isNaN(date.getTime()) ? "Unknown" : date.toLocaleString();
  };

  const handleDecision = async (decision) => {
    try {
      if (decision === "accept") {
        await updateDoc(doc(db, "accident_data", accidentData.id), {
          er_informed: true,
        });
      } else if (decision === "reject") {
        await updateDoc(doc(db, "accident_data", accidentData.id), {
          real: false,
        });
      }
    } catch (err) {
      console.error("Error updating Firestore:", err);
    }

    // 👉 Tell server to stop sending frames (but keep connection alive)
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "stop_video" }));
      setStreaming(false);
    }

    // ✅ Trigger parent callback (toast, etc.)
    onDecision?.(decision);
  };

  if (!accidentData) {
    return <div style={{ color: "white" }}>Loading accident details...</div>;
  }

  // Convert GeoPoint to string
  const formatValue = (key, value) => {
    if (key === "time") return formatTime(value);
    if (key === "location" && value?._lat != null && value?._long != null) {
      return `Lat: ${value._lat}, Lng: ${value._long}`;
    }
    if (typeof value === "boolean") return value ? "Yes" : "No";
    if (typeof value === "number") return value.toFixed(2);
    return value?.toString() || "Unknown";
  };

  // Make labels pretty
  const labelMap = {
    ai_conf: "AI Confidence",
    er_dispatched: "ER Dispatched",
    er_informed: "ER Informed",
    location: "Location",
    real: "Real",
    severity: "Severity",
    time: "Time",
  };

  return (
    <div className="accident-alert">
      <h2>ACCIDENT DETECTED</h2>
      <div className="content-container">
        {/* Video feed */}
        <div className="video-container">
          {streaming ? (
            <img ref={videoRef} alt="Live feed" className="video-feed" />
          ) : (
            <div className="video-placeholder">🚫 Stream stopped</div>
          )}
        </div>

        {/* Accident details */}
        <div className="details-container">
          <div className="accident-details">
            <h3>Accident Details</h3>
            {Object.entries(accidentData).map(([key, value]) => {
              if (key === "id") return null; // skip internal id
              return (
                <div className="detail-item" key={key}>
                  <span className="detail-label">
                    {labelMap[key] || key}:
                  </span>
                  <span className="detail-value">
                    {formatValue(key, value)}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Buttons based on AI confidence */}
          <div className="decision">
            {accidentData.ai_conf != null && accidentData.ai_conf < 25 ? (
              <>
                <button
                  className="decision-accept"
                  onClick={() => handleDecision("accept")}
                >
                  Dispatch ER Services
                </button>
                <button
                  className="decision-reject"
                  onClick={() => handleDecision("reject")}
                >
                  Flag Fake Detection
                </button>
              </>
            ) : (
              <button
                className="decision-ack"
                onClick={() => handleDecision("acknowledge")}
              >
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
