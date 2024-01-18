import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import axios from 'axios';

import { useParams } from 'react-router-dom';

const MapWithGeoJSON = () => {
  const { geojsonPath } = useParams();
  const [geojsonData, setGeojsonData] = useState(null);

  useEffect(() => {
    const fetchGeoJSON = async () => {
      try {
        const response = await axios.get(geojsonPath);
        setGeojsonData(response.data);
      } catch (error) {
        console.error('Error fetching GeoJSON data:', error);
      }
    };

    fetchGeoJSON();
  }, []);

  return (
    <MapContainer center={[0, 0]} zoom={2} style={{ height: '400px', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {geojsonData && <GeoJSON data={geojsonData} />}
    </MapContainer>
  );
};

export default MapWithGeoJSON;
