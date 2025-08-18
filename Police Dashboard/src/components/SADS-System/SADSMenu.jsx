import { useState, useEffect } from "react";
import "../../styles/SADSSystem.css";

function ManualControl() {
    const [selectedView, setSelectedView] = useState(null);

    return (
        <>
            <div className="parent-body">
                <h1 className="title">
                    <span className="title-blue">Manual </span>
                    <span className="title-white">Control</span>
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
                </div>
            </div>
            {/* {selectedView == "manual" && <ManualControl />}
            {selectedView == "slts" && <SLTSSystem />}
            {selectedView == "sads" && <SADSSystem />}
            {selectedView == "alert" && <AccidentAlert />} */}
        </>
    );
}

export default ManualControl;