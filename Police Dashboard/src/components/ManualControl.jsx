import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/ManualControl.css';

// Sample intersection data - replace with your actual data
const intersections = [
  {
    id: 1,
    name: "Main Street & 1st Avenue",
    position: [12.9716, 77.5946], // Bangalore coordinates
    signals: [
      { id: 1, direction: "North", color: "red" },
      { id: 2, direction: "South", color: "red" },
      { id: 3, direction: "East", color: "red" }
    ]
  },
  // Add more intersections as needed
];

function ManualControl() {
  const [selectedIntersection, setSelectedIntersection] = useState(null);
  const [signals, setSignals] = useState([]);
  const [ws, setWs] = useState(null);

  // Setup WebSocket connection
  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8765');
    
    websocket.onopen = () => {
      console.log('Connected to signal control server');
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setWs(websocket);

    return () => {
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.close();
      }
    };
  }, []);

    const handleIntersectionSelect = (intersection) => {
    console.log("Selected intersection:", intersection);
    setSelectedIntersection(intersection);
    setSignals(intersection.signals);
  };
  
  // Modify handleSignalChange to send data to Python
  const handleSignalChange = (signalId, newColor) => {
    if (!selectedIntersection) return;

    const signalData = {
      type: 'signal_change',
      data: {
        intersectionId: selectedIntersection.id,
        intersectionName: selectedIntersection.name,
        coordinates: selectedIntersection.position,
        signalId: signalId,
        newState: newColor
      }
    };

    // Send to Python backend
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(signalData));
    }

    // Update local state
    setSignals(signals.map(signal => 
      signal.id === signalId ? { ...signal, color: newColor } : signal
    ));
  };

  return (
    <div className="manual-control">
      <h1 className="control-title">
        <span className="title-blue">Manual </span>
        <span className="title-white">Control</span>
      </h1>

      <div className="control-layout">
        {/* Map View */}
        <div className="map-container">
          <MapContainer center={[12.9716, 77.5946]} zoom={13} style={{ height: '39vw', width: '47vw' }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap contributors' />
            {intersections.map(intersection => (
              <Marker key={intersection.id} position={intersection.position} eventHandlers={{click: () => handleIntersectionSelect(intersection),}}>
                <Popup>{intersection.name}</Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* Signal Controls */}
        {selectedIntersection && (
          <div className="signal-controls">
            <h2>{selectedIntersection.name}</h2>
            <div className="signals-grid">
              {signals.map(signal => (
                <div key={signal.id} className="signal-control">
                  <h3>{signal.direction}</h3>
                  <div className="signal-buttons">
                    <button className={`signal-btn ${signal.color === 'red' ? 'active' : ''}`} onClick={() => handleSignalChange(signal.id, 'red')}>
                      Red
                    </button>
                    <button className={`signal-btn ${signal.color === 'yellow' ? 'active' : ''}`} onClick={() => handleSignalChange(signal.id, 'yellow')}>
                      Yellow
                    </button>
                    <button className={`signal-btn ${signal.color === 'green' ? 'active' : ''}`} onClick={() => handleSignalChange(signal.id, 'green')}>
                      Green
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ManualControl;