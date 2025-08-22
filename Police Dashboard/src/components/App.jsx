import { useState, useEffect } from "react";
import SplashScreen from "./SplashScreen.jsx";
import AccidentAlert from './AccidentAlert.jsx';
import ManualControl from './MTIC-System/ManualControl.jsx';
import STLSMenu from "./STLS-System/STLSMenu.jsx";
import SADSMenu from "./SADS-System/SADSMenu.jsx";
import Navbar from "./Navbar.jsx";
import "../styles/Menu.css";

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [selectedView, setSelectedView] = useState(null);
  const [notification, setNotification] = useState(null);
  const [prevView, setPrevView] = useState(null);

  const [toast, setToast] = useState(null);
  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 4000);
  };

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8765");
    ws.onopen = () => console.log("Connected to WebSocket server");

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'notification') {
          setNotification(data);
        }
      } catch (e) {
        console.error("Invalid message:", event.data);
      }
    };

    ws.onerror = (error) => console.error("WebSocket error:", error);
    return () => ws.close();
  }, []);

  const handleNotificationClick = () => {
    setPrevView(selectedView);
    setSelectedView("alert");
    setNotification(null);
  };

  const handleAccidentDecision = (decision) => {
    if (decision === "accept") {
      showToast("🚑 ER team has been informed!");
    } else {
      showToast("⚠️ Fake alert identified.");
    }
    setSelectedView(prevView);
    setPrevView(null);
  };

  return (
    <>
      <Navbar setSelectedView={setSelectedView} />

      {toast && <div className="left-toast">{toast}</div>}

      {showSplash && <SplashScreen onFinish={() => setShowSplash(false)} />}

      {notification && (
        <div className="notification" onClick={handleNotificationClick}>
          Accident Detected! Click to view details
        </div>
      )}

      {!showSplash && !selectedView && (
        <div className="parent-body">
          <h1 className="title">
            <span className="title-blue">Welcome, </span>
            <span className="title-white">User</span>
          </h1>
          <div className="button-container">
            <div>
              <button className="buttons" onClick={() => setSelectedView("manual")}>🕹️</button>
              <div className="btn-desc">Manual Intersection Control</div>
            </div>
            <div>
              <button className="buttons" onClick={() => setSelectedView("stls")}>🚦</button>
              <div className="btn-desc">STLS Board</div>
            </div>
            <div>
              <button className="buttons" onClick={() => setSelectedView("sads")}>🚨</button>
              <div className="btn-desc">SADS Board</div>
            </div>
          </div>
        </div>
      )}

      {selectedView === "manual" && <ManualControl />}
      {selectedView === "stls" && <STLSMenu />}
      {selectedView === "sads" && <SADSMenu />}

      {selectedView === "alert" && <AccidentAlert onDecision={handleAccidentDecision} />}
    </>
  );
}

export default App;