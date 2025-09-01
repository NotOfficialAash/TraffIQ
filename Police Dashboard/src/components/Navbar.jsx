import "../styles/Navbar.css";

import titleImage from "../assets/TraffIQNavBarLogo.png";

function Navbar({ setSelectedView }) {
  return (
    <nav className="navbar">
      <a href="#" onClick={() => setSelectedView(null)}>
        <img className="nav-title" src={titleImage} alt="Home" />
      </a>
      <div className="nav-links">
        <button classname="nav-buttons" onClick={() => setSelectedView(null)}>HOME</button>
        <button classname="nav-buttons" onClick={() => setSelectedView("manual")}>CONTROL PANEL</button>
        <button classname="nav-buttons" onClick={() => setSelectedView("stls")}> TRAFFIC HISTORY</button>
        <button classname="nav-buttons" onClick={() => setSelectedView("sads")}>ACCIDENT HISTORY</button>
        <button onClick={() => setSelectedView("alert")}>⚠️ Alerts</button> 
      </div>
    </nav>
  );
}

export default Navbar;
