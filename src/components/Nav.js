import React from "react";
import { Link, useLocation } from 'react-router-dom';
import "../css/nav.css";

const Nav = () => {
  const location = useLocation(); // 현재 경로 감지

  return (
    <nav 
    className={
      location.pathname === "/" ? "nav-home" :
      location.pathname === "/trip" ? "nav-trip" :
      location.pathname === "/path" ? "nav-path" : ""
    }
    >
      <ul>
        <li>
          <Link to="/">Home</Link>
        </li>
        <li>
          <Link to="/trip">Trip Layer</Link>
        </li>
        <li>
          <Link to="/path">Path Layer</Link>
        </li>
      </ul>
    </nav>
  );
};

export default Nav;
