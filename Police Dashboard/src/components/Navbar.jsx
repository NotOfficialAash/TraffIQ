import "../styles/Navbar.css";

function Navbar({ setSelectedView }) {
  return (
    <nav className="navbar">
      <h2 className="nav-title">🚦 Traffic Control</h2>
      <div className="nav-links">
        <button onClick={() => setSelectedView(null)}>🏠 Home</button>
        <button onClick={() => setSelectedView("manual")}>🕹️ Manual</button>
        <button onClick={() => setSelectedView("stls")}>🚦 STLS</button>
        <button onClick={() => setSelectedView("sads")}>🚨 SADS</button>
        <button onClick={() => setSelectedView("alert")}>⚠️ Alerts</button>
      </div>
    </nav>
  );
}

export default Navbar;
