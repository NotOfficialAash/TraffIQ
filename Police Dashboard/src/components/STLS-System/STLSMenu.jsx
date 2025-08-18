import { useState } from "react";
import "../../styles/Menu.css";

function STLSMenu() {
    const [selectedView, setSelectedView] = useState(null);

    return (
        <>
            <div className="parent-body">
                <h1 className="title">
                    <span className="title-blue">Smart Traffic Light </span>
                    <span className="title-white">System</span>
                </h1>
                <div className="button-container">
                    <div>
                        <button className="buttons" onClick={() => setSelectedView("")}></button>
                        <div className="btn-desc">Emergency Override</div>
                    </div>
                    <div>
                        <button className="buttons" onClick={() => setSelectedView("")}></button>
                        <div className="btn-desc">Signal Control</div>
                    </div>
                    <div>
                        <button className="buttons" onClick={() => setSelectedView("")}></button>
                        <div className="btn-desc">Timing Adjustment</div>
                    </div>
                </div>
            </div>
            {/* {selectedView == "manual" && <ManualControl />}
            {selectedView == "slts" && <SLTSSystem />}
            {selectedView == "sads" && <SADSSystem />}
            {selectedView == "alert" && <AccidentAlert />} */}
        </>
    );
}

export default STLSMenu;