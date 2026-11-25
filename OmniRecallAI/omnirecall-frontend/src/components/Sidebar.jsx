import { Link } from "react-router-dom";
import "../assets/styles/sidebar.css";

function Sidebar() {
  return (
    <div className="sidebar">
      <div className="sidebar-logo">OmniRecall AI</div>

      <div className="sidebar-menu">
        <Link to="/dashboard">🏠 Dashboard</Link>

        <Link to="/search">🔍 Search</Link>

        <Link to="/upload">⬆ Upload</Link>

        <Link to="/gallery">🖼 Gallery</Link>

        <Link to="/documents">📄 Documents</Link>

        <Link to="/videos">🎥 Videos</Link>

        <Link to="/settings">⚙ Settings</Link>
      </div>
    </div>
  );
}

export default Sidebar;
