import { useState, useEffect } from "react";
import { collection, query, onSnapshot } from "firebase/firestore";
import { db } from "./firebase";

import SplashScreen from "./SplashScreen.jsx";
import AccidentAlert from './AccidentAlert.jsx';
import ManualControl from './ManualControl.jsx';
import STLSMenu from "./STLSDashboard.jsx";
import SADSMenu from "./SADSDashboard.jsx";
import Navbar from "./Navbar.jsx";
import "../styles/Menu.css";

import controlPanelImg from "../assets/Control Panel.png";
import trafficHistoryImg from "../assets/Traffic History.png";
import accidentHistoryImg from "../assets/Accident History.png";
import welcomeUserImg from "../assets/Welcome Banner.png";

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
    let firstLoad = true; // Ignore existing documents on initial load

    const unsubscribe = onSnapshot(q, (snapshot) => {
      snapshot.docChanges().forEach((change) => {
        if (change.type === "added") {
          const data = { id: change.doc.id, ...change.doc.data() };

          if (!firstLoad) {
            console.log("New accident data:", data);
            setNotification(data); // Set notification state
          }
        }
      });
      firstLoad = false; // After first snapshot, future adds trigger notifications
    });

    return () => unsubscribe();
  }, []);

  // Handle clicking notification banner
  const handleNotificationClick = () => {
    setPrevView(selectedView); // Save the current view
    setSelectedView("alert"); // Switch to the alert view
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

    setSelectedView(prevView); // Return to the previous view
    setPrevView(null);
    setNotification(null); // Clear the notification
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
          <img className="welcome-img" src={welcomeUserImg} alt="" />
          <div className="button-container">
            <div>
              <button className="buttons" onClick={() => setSelectedView("manual")}>
                <img src={controlPanelImg} alt="" />
              </button>
            </div>
            <div>
              <button className="buttons" onClick={() => setSelectedView("stls")}>
                <img src={trafficHistoryImg} alt="" />
              </button>
            </div>
            <div>
              <button className="buttons" onClick={() => setSelectedView("sads")}>
                <img src={accidentHistoryImg} alt="" />
              </button>
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