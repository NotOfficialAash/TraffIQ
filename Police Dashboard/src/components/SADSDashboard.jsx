import { useEffect, useState } from "react";
import { collection, onSnapshot } from "firebase/firestore";
import { db } from "./firebase";
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, Legend } from "recharts";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "../styles/SADSDashboard.css";

// Utility to recenter map
function RecenterMap({ lat, lng }) {
    const map = useMap();
    useEffect(() => {
        if (lat && lng) {
            map.setView([lat, lng], 15, { animate: true });
        }
    }, [lat, lng, map]);
    return null;
}

function AccidentDashboard() {
    const [accidents, setAccidents] = useState([]);
    const [hoveredAccident, setHoveredAccident] = useState(null);
    const [selectedAccident, setSelectedAccident] = useState(null);
    const [activeTab, setActiveTab] = useState("pie");
    
    useEffect(() => {
        const unsub = onSnapshot(
            collection(db, "accident_data"), // Ensure this matches your Firestore collection name
            (snapshot) => {
                const data = snapshot.docs.map((doc) => ({
                    id: doc.id,
                    ...doc.data(),
                }
            )
        );
        setAccidents(data.filter((d) => d.real)); // Filter only real accidents
        },
        
        (error) => {
            console.error("Error fetching data:", error);
        }
    );
    
    return () => unsub();
    }, []);

    // Pie chart data
    const severityCounts = accidents.reduce(
        (acc, cur) => {
            acc[cur.severity] = (acc[cur.severity] || 0) + 1;
            return acc;
        },
        { minor: 0, major: 0 }
    );
    
    const pieData = [
        { name: "Minor", value: severityCounts.minor },
        { name: "Major", value: severityCounts.major },
    ];
    const COLORS = ["#22c55e", "#ef4444"];

    // Time-series data
    const timeData = accidents.map((a) => {
        let formatted = "Unknown";
        if (a.time?.toDate) {
            formatted = a.time.toDate().toLocaleDateString();
        }
        return { time: formatted, count: 1 };
    });
    
    // Aggregate by day
    const aggregated = timeData.reduce((acc, cur) => {
        const existing = acc.find((x) => x.time === cur.time);
        if (existing) existing.count += 1;
        else acc.push({ ...cur });
        return acc;
    }, []);
    
    
    return (
    <div className="dashboard">
        <h2>Accident History</h2>
        <div className="content-container">
            <div className="left-column">
                <div className="list-container">
                    <ul>
                        {accidents.map((acc) => (
                        <li
                            key={acc.id}
                            className={selectedAccident?.id === acc.id ? "active" : ""}
                            onClick={() => setSelectedAccident(acc)}
                            onMouseEnter={() => setHoveredAccident(acc)}
                            onMouseLeave={() => setHoveredAccident(null)}
                        >
                        <strong>{acc.severity.toUpperCase()}</strong>  
                        <br />
                        {acc.time?.toDate ? acc.time.toDate().toLocaleString() : "Unknown time"}
                        <br />
                        <span className="location-coordinates">
                            Lat: {acc.location?._lat?.toFixed(3)}, Lng:{" "}
                            {acc.location?._long?.toFixed(3)}
                        </span>
                        </li>
                        ))}
                    </ul>
                </div>

                <div className="charts-container">
                    <div className="tabs">
                        <button onClick={() => setActiveTab("pie")} className={activeTab === "pie" ? "active" : ""}>
                            PIE
                        </button>
                        <button onClick={() => setActiveTab("line")} className={activeTab === "line" ? "active" : ""}>
                            LINE
                        </button>
                        <button onClick={() => setActiveTab("bar")} className={activeTab === "bar" ? "active" : ""}>
                            BAR
                        </button>
                    </div>

                    <div className="chart-container">
                        {activeTab === "pie" && (
                            <PieChart width={400} height={300}>
                                <Pie data={pieData} cx="50%" cy="50%" labelLine={false} outerRadius={100} fill="#8884d8" dataKey="value" label>
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                            <Legend />
                            </PieChart>
                        )}

                        {activeTab === "line" && (
                            <LineChart width={500} height={300} data={aggregated}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="time" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Line type="monotone" dataKey="count" stroke="#8884d8" />
                            </LineChart>
                        )}

                        {activeTab === "bar" && (
                            <BarChart width={500} height={300} data={aggregated}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="time" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="count" fill="#82ca9d" />
                            </BarChart>
                        )}
                    </div>
                </div>
            </div>

            <div className="right-column">
                <div className="map-container">
                    <MapContainer center={[20.5937, 78.9629]} zoom={5} style={{ height: "100%", width: "100%" }}>
                        <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                        {accidents.map((acc) => {
                            const lat = acc.location?._lat;
                            const lng = acc.location?._long;
                            if (!lat || !lng) return null;
                            const isHovered = hoveredAccident?.id === acc.id;
                            const isSelected = selectedAccident?.id === acc.id;
                            return (
                                <Marker key={acc.id} position={[lat, lng]} opacity={isHovered || isSelected ? 1 : 0.6}>
                                    <Popup>
                                        <strong>{acc.severity.toUpperCase()}</strong>
                                        <br />
                                        {acc.time?.toDate ? acc.time.toDate().toLocaleString() : "Unknown"}
                                    </Popup>
                                </Marker>
                            );
                        })}
                        {selectedAccident && <RecenterMap lat={selectedAccident.location?._lat} lng={selectedAccident.location?._long} />}
                    </MapContainer>
                </div>   
            </div>
        </div>
    </div>
  );
}

export default AccidentDashboard;
