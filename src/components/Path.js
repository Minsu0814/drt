
import React, { useState, useEffect, useCallback } from "react";

import DeckGL from '@deck.gl/react';
import {Map} from 'react-map-gl';

import {AmbientLight, PointLight, LightingEffect} from '@deck.gl/core';
import { PathLayer } from "@deck.gl/layers";


import legend from "../image/legend.png";
import "../css/trip.css";


const ambientLight = new AmbientLight({
  color: [255, 255, 255],
  intensity: 1.0
});

const pointLight = new PointLight({
  color: [255, 255, 255],
  intensity: 2.0,
  position: [-74.05, 40.7, 8000]
});

const lightingEffect = new LightingEffect({ambientLight, pointLight});

const material = {
  ambient: 0.1,
  diffuse: 0.6,
  shininess: 32,
  specularColor: [60, 64, 70]
};

const material2 = {
  ambient: 0.3,
  diffuse: 0.6,
  shininess: 32,
  specularCol: [60, 64, 70]
};

const DEFAULT_THEME = {
  buildingColor: [228, 228, 228],
  buildingColor2: [255, 255, 255],
  trailColor0: [253, 128, 93],
  trailColor1: [23, 184, 190],
  material,
  material2,
  effects: [lightingEffect]
};

const INITIAL_VIEW_STATE = { 
  longitude: 126.98, // 126.98 , -74
  latitude: 37.57, // 37.57 , 40.72
  zoom: 11,
  pitch: 20,
  minZoom: 5,
  maxZoom: 16,
  bearing: 0
};


const minTime = 540;
const maxTime = 800;
const animationSpeed = 1;
const mapStyle = "mapbox://styles/spear5306/ckzcz5m8w002814o2coz02sjc";
const MAPBOX_TOKEN = `pk.eyJ1Ijoic2hlcnJ5MTAyNCIsImEiOiJjbG00dmtic3YwbGNoM2Zxb3V5NmhxZDZ6In0.ZBrAsHLwNihh7xqTify5hQ`;

const returnAnimationTime = (time) => {
    if (time > maxTime) {
      return minTime;
    } else {
      return time + 0.01 * animationSpeed;
    }
  };
  

const Trip = (props) => {
  const [time, setTime] = useState(minTime);
  const [animation] = useState({});


  const trips = props.trips;


  const animate = useCallback(() => {
    setTime(returnAnimationTime);
    animation.id = window.requestAnimationFrame(animate);
  }, [animation]);

  useEffect(() => {
    animation.id = window.requestAnimationFrame(animate);
    return () => window.cancelAnimationFrame(animation.id);
  }, [animation, animate]);

  const layers = [
 
    new PathLayer({
      id: 'paths',
      data: trips,
      getPath: d => d.route,
      getColor: d => 
        {
          const vendorColorMap = {
            "WALK" : [36, 143, 223], 
            "SUBWAY" : [254, 198, 39],   
            "BUS" : [44, 170, 159], 
            "KICKBOARD" : [255, 255, 255],
          };
          return vendorColorMap[d.mode] || [255, 255, 50];
        },
      opacity: 1,
      widthMinPixels: 5,
      rounded: true,
      currentTime: time,
      shadowEnabled: false
    }),
    
   
  ];
  
  return (
    <div className="trip-container" style={{ position: "relative" }}>
      <DeckGL
        effects={DEFAULT_THEME.effects}
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={layers}
      >
        <Map mapStyle={mapStyle} mapboxAccessToken={MAPBOX_TOKEN} preventStyleDiffing={true}/>
      </DeckGL>
      <img className="legend" src={legend} alt="legend" ></img>
    </div>
  );
}

export default Trip;
