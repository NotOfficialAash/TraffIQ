import { useEffect, useState } from "react";
import "../styles/SplashScreen.css"; // we'll define fade animation here

function SplashScreen({ onFinish }) {
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    const timer1 = setTimeout(() => setFadeOut(true), 2500); // start fade out
    const timer2 = setTimeout(() => onFinish(), 3000); // remove splash completely
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [onFinish]);

  return (
    <div className={`splash-container ${fadeOut ? "fade-out" : ""}`}>
      <img src="/logo.svg" alt="Splash Logo" className="splash-logo" />
    </div>
  );
}

export default SplashScreen;
