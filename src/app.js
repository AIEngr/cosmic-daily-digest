import React, { useEffect, useState } from 'react';
import './index.css'; // Import the global styles

function App() {
  const [digestData, setDigestData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ⚠️ IMPORTANT: REPLACE THIS PLACEHOLDER URL WITH YOUR ACTUAL N8N WEBHOOK URL
  const WEBHOOK_URL = WEBHOOK_URL;

  // Helper to format ISO 8601 time
  const formatTime = (isoTime) => {
    if (!isoTime) return 'N/A';
    const date = new Date(isoTime);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
  };

  // Helper to format Date
  const formatDate = (isoTime) => {
    if (!isoTime) return 'N/A';
    const date = new Date(isoTime);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  useEffect(() => {
    const fetchDigestData = async () => {
      try {
        const response = await fetch(WEBHOOK_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setDigestData(data);
      } catch (err) {
        console.error("Fetch error:", err);
        setError("Could not load cosmic data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchDigestData();
  }, []); // Empty dependency array means this runs once on mount

  if (loading) {
    return (
      <div className="container">
        <h1 className="loading">Loading cosmic data... 🚀</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <h1 className="error">{error}</h1>
      </div>
    );
  }

  // Destructure data for easier access
  const { apod, weather } = digestData;

  // Determine media type for APOD
  let apodMedia;
  if (apod.media_type === 'video') {
    apodMedia = (
      <iframe
        className="apod-media"
        src={apod.url}
        frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        title={apod.title}
      ></iframe>
    );
  } else {
    apodMedia = <img className="apod-media" src={apod.url} alt={apod.title} />;
  }

  return (
    <div className="container">
      <h1>🌌 Cosmic Daily Digest 🗓️</h1>

      <h2 className="section-title">✨ NASA Astronomy Picture of the Day (APOD)</h2>
      <div className="apod-grid">
        <div className="apod-media">
          {apodMedia}
        </div>
        <div className="apod-info">
          <h3>{apod.title || 'APOD Title Missing'}</h3>
          <p><strong>Date:</strong> {formatDate(apod.date)}</p>
          <p>{apod.explanation || 'No explanation available.'}</p>
        </div>
      </div>
      
      <h2 className="section-title">☁️ Local Weather Summary</h2>
      <div className="weather-grid">
        <div className="weather-card">
          <span>{weather.temperature}°C</span>
          <p>Temperature</p>
        </div>
        <div className="weather-card">
          <span>{weather.windspeed} km/h</span>
          <p>Wind Speed</p>
        </div>
        <div className="weather-card">
          <span>{formatTime(weather.time)}</span>
          <p>Local Time</p>
        </div>
      </div>
    </div>
  );
}


export default App;
