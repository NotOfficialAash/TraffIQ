import { useEffect, useState } from "react";
import { collection, onSnapshot } from "firebase/firestore";
import { db } from "./firebase";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, Legend } from "recharts";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "../styles/SLTSDashboard.css";

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

function TrafficDashboard() {
    const [traffic, setTraffic] = useState([]);
    const [hoveredEntry, setHoveredEntry] = useState(null);
    const [selectedEntry, setSelectedEntry] = useState(null);
    const [activeTab, setActiveTab] = useState("line");

    useEffect(() => {
        const unsub = onSnapshot(
            collection(db, "traffic_data"),
            (snapshot) => {
                const data = snapshot.docs.map((doc) => ({
                    id: doc.id,
                    ...doc.data(),
                }));
                setTraffic(data);
            },
            (error) => {
                console.error("Error fetching traffic data:", error);
            }
        );
        return () => unsub();
    }, []);

    // Ensure unique locations for pins
    const uniqueLocations = Object.values(
        traffic.reduce((acc, cur) => {
            const key = `${cur.location?._lat}-${cur.location?._long}`;
            acc[key] = cur; // overwrite with latest entry
            return acc;
        }, {})
    );

    // Chart data (time vs density)
    const chartData = traffic.map((t) => {
        let formattedTime = "Unknown";
        if (t.time?.toDate) {
            formattedTime = t.time.toDate().toLocaleDateString();
        }
        return { time: formattedTime, density: t.density || 0 };
    });

    return (
        <div className="dashboard">
            <h2>Traffic History</h2>
            <div className="content-container">
                <div className="left-column">
                    <div className="list-container">
                        <ul>
                            {traffic.map((entry) => (
                                <li
                                    key={entry.id}
                                    className={selectedEntry?.id === entry.id ? "active" : ""}
                                    onClick={() => setSelectedEntry(entry)}
                                    onMouseEnter={() => setHoveredEntry(entry)}
                                    onMouseLeave={() => setHoveredEntry(null)}
                                >
                                    <strong>
                                        {entry.time?.toDate ? entry.time.toDate().toLocaleString() : "Unknown time"}
                                    </strong>
                                    <br />
                                    <span className="density">
                                        Density: {entry.density ?? "N/A"}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="charts-container">
                        <div className="tabs">
                            <button
                                onClick={() => setActiveTab("line")}
                                className={activeTab === "line" ? "active" : ""}
                            >
                                Line
                            </button>
                            <button
                                onClick={() => setActiveTab("bar")}
                                className={activeTab === "bar" ? "active" : ""}
                            >
                                Bar
                            </button>
                        </div>

                        <div className="chart-container">
                            {activeTab === "line" && (
                                <LineChart width={500} height={300} data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="time" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="density" stroke="#8884d8" />
                                </LineChart>
                            )}

                            {activeTab === "bar" && (
                                <BarChart width={500} height={300} data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="time" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="density" fill="#82ca9d" />
                                </BarChart>
                            )}
                        </div>
                    </div>
                </div>

                <div className="right-column">
                    <div className="map-container">
                        <MapContainer center={[20.5937, 78.9629]} zoom={5} style={{ height: "100%", width: "100%" }}>
                            <TileLayer
                                attribution='&copy; OpenStreetMap contributors'
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            />
                            {uniqueLocations.map((entry) => {
                                const lat = entry.location?._lat;
                                const lng = entry.location?._long;
                                if (!lat || !lng) return null;
                                const isHovered = hoveredEntry?.id === entry.id;
                                const isSelected = selectedEntry?.id === entry.id;
                                return (
                                    <Marker key={entry.id} position={[lat, lng]} opacity={isHovered || isSelected ? 1 : 0.6}>
                                        <Popup>
                                            <strong>
                                                {entry.time?.toDate ? entry.time.toDate().toLocaleString() : "Unknown"}
                                            </strong>
                                            <br />
                                            Density: {entry.density ?? "N/A"}
                                        </Popup>
                                    </Marker>
                                );
                            })}
                            {selectedEntry && (
                                <RecenterMap lat={selectedEntry.location?._lat} lng={selectedEntry.location?._long} />
                            )}
                        </MapContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default TrafficDashboard;
