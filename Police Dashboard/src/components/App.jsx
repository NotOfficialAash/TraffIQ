// App.jsx
import { useState, useEffect } from "react";
import { collection, query, onSnapshot } from "firebase/firestore";
import { db } from "./firebase"; // Firestore instance (adjust path if needed)

import SplashScreen from "./SplashScreen.jsx";
import AccidentAlert from './AccidentAlert.jsx';
import ManualControl from './MTIC-System/ManualControl.jsx';
import STLSMenu from "./STLS-System/STLSMenu.jsx";
import SADSMenu from "./SADSDashboard.jsx";
import Navbar from "./Navbar.jsx";
import "../styles/Menu.css";

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [selectedView, setSelectedView] = useState(null);
  const [notification, setNotification] = useState(null);
  const [prevView, setPrevView] = useState(null);
  const [toast, setToast] = useState(null);

  // Show toast message
  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 4000);
  };

  // Firestore listener for new accident data
  useEffect(() => {
    const q = query(collection(db, "accident_data"));
    let firstLoad = true;  // ignore existing documents on initial load

    const unsubscribe = onSnapshot(q, snapshot => {
      snapshot.docChanges().forEach(change => {
        if (change.type === "added") {
          const data = { id: change.doc.id, ...change.doc.data() };

          if (!firstLoad) { // only notify for new additions
            console.log("New accident data:", data);
            setNotification(data);
            setSelectedView("alert"); // open AccidentAlert automatically
          }
        }
      });
      firstLoad = false; // after first snapshot, future adds trigger notifications
    });

    return () => unsubscribe();
  }, []);

  // Handle clicking notification banner
  const handleNotificationClick = () => {
    setPrevView(selectedView);
    setSelectedView("alert");
  };

  // Handle decision from AccidentAlert component
  const handleAccidentDecision = (decision) => {
    if (decision === "accept") {
      showToast("🚑 ER team has been informed!");
    } else if (decision === "reject") {
      showToast("⚠️ Fake alert identified.");
    } else if (decision === "acknowledge") {
      showToast("⚠️ Accident acknowledged");
    }

    setSelectedView(prevView);
    setPrevView(null);
    setNotification(null);
  };

  return (
    <>
      <Navbar setSelectedView={setSelectedView} />

      {/* Toast notification */}
      {toast && <div className="left-toast">{toast}</div>}

      {/* Splash screen */}
      {showSplash && <SplashScreen onFinish={() => setShowSplash(false)} />}

      {/* Accident notification banner */}
      {notification && selectedView !== "alert" && (
        <div className="notification" onClick={handleNotificationClick}>
          Accident Detected! Click to view details
        </div>
      )}

      {/* Main menu */}
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
              <div className="btn-desc">Accident History</div>
            </div>
          </div>
        </div>
      )}

      {/* Selected views */}
      {selectedView === "manual" && <ManualControl />}
      {selectedView === "stls" && <STLSMenu />}
      {selectedView === "sads" && <SADSMenu />}
      {selectedView === "alert" && notification && (
        <AccidentAlert
          accidentData={notification}
          onDecision={handleAccidentDecision}
        />
      )}
    </>
  );
}

export default App;
