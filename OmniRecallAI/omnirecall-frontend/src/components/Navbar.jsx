import { Link } from "react-router-dom";
import "../assets/styles/navbar.css";

function Navbar() {
  return (
    <div className="navbar">
      <h2>OmniRecall AI</h2>

      <div className="nav-links">
        <Link to="/dashboard">Dashboard</Link>

        <Link to="/gallery">Gallery</Link>

        <Link to="/search">Search</Link>
      </div>
    </div>
  );
}

export default Navbar;
