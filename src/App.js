import "mapbox-gl/dist/mapbox-gl.css";
import React, { useState, useEffect, useCallback } from "react";
import { HashRouter as Router, Route, Routes } from 'react-router-dom';
// HashRouter BrowserRouter
import axios from "axios";

import Splash from "./components/Splash";
import Trip from "./components/Trip";
import Path from "./components/Path";
import Home from "./components/Home";
import Nav from "./components/Nav";

import "./css/app.css";

const fetchData = (FilE_NAME) => {
  const res = axios.get(
    `https://raw.githubusercontent.com/1023sherry/drt/main/src/data/${FilE_NAME}.json`
  );
  const data = res.then((r) => r.data);
  return data;
};

const App = () => {
  // const [icon, setIcon] = useState([]);
  // const [line, setLine] = useState([]);
  const [people, setPeople] = useState([]);
  const [trips, setTrips] = useState([]);




  const [isloaded, setIsLoaded] = useState(false);

  const getData = useCallback(async () => {

    const TRIPS =  await Promise.all([
      fetchData("trip"),
    ])
    
    const PEOPLE = await fetchData("people");
      

    // const ICON = await Promise.all([
    //   fetchData("bus_icon"),
    //   fetchData("trail_icon"),
    // ]);

    // const LINE = await Promise.all([
    //   fetchData("bus_line"),
    //   fetchData("trail_line"),
    // ]);


    // setIcon((prev) => ICON.flat());
    // setLine((prev) => LINE.flat());
    setTrips((prev) => TRIPS.flat())
    setPeople((prev) => PEOPLE);
 



    setIsLoaded(true);
  }, []);

  useEffect(() => {
    getData();
  }, [getData]);

  return (
    <Router>
      <div className="App"> 
        <Nav />  
        {!isloaded && <Splash />}
        {isloaded && (
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/trip" element={<Trip 
                                                trips={trips}
                                                people={people} 
                                                // icon={icon}
                                                // line={line}
                                                
                                                />} />
            <Route path="/path" element={<Path trips={trips} />} />
          </Routes>
        )}
      </div>
    </Router>
  );
}

export default App;
