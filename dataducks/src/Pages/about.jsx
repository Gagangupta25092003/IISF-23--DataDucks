import React, { useEffect, useState } from "react";
import { StickyNavbar } from "../components/navbar";
import BackgroundPhoto from "../resources/Images/background.png";

export function About() {
  const [isMounted, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 500); // Delay in milliseconds

    return () => clearTimeout(timer);
  }, []);

  return (
    <div>
      <StickyNavbar />
      <div>
        <div className="text-white z-5 absolute backdrop-filter backdrop-blur-md h-5/6">
          <div className="w-screen p-32 text-blue-100 text-md flex flex-col items-center font-bold">
            <div
              className={`text-7xl font-bold text-blue-100 ${
                isMounted
                  ? "transition-transform ease-in-out transform translate-x-0"
                  : "opacity-0 translate-x-96"
              }`}>
              DataDucks</div>
              <div className="text-4xl font-bold">Intelligent Data Catalouging System</div>
            
            <div className="text-xl">
              Optimized Geospatial Data Management for Bhuvan Platform. <br />
              <br />
            </div>
            <p className="text-lg mx-16">
              Revolutionize geospatial data management with our cutting-edge solution at [Your Hackathon Solution]! Unleash the power of Bhuvan platform through our innovative approach, featuring enhanced data quality, optimized storage with de-duplication, seamless data integration, comprehensive cataloging, and accelerated access for meaningful analysis. We've crafted a solution that transforms Bhuvan into a dynamic and efficient system, setting new standards in geospatial technology. Join us in reshaping the future of data management - where precision meets adaptability and insights unfold effortlessly. Discover the possibilities with DataDucks!
              
            </p>
          </div>
        </div>
        <img src={BackgroundPhoto} className="w-screen  z-1" />
      </div>
    </div>
  );
}
