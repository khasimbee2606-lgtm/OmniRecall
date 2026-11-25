import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

import "../assets/styles/settings.css";

function Settings() {
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "dark");

  useEffect(() => {
    document.body.className = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <>
      <Sidebar />

      <div className="settings-page">
        <Navbar />

        <div className="settings-container">
          <h1>⚙ Settings</h1>

          {/* Theme */}

          <div className="setting-card">
            <h3>🎨 Theme</h3>

            <select value={theme} onChange={(e) => setTheme(e.target.value)}>
              <option value="dark">🌙 Dark</option>

              <option value="light">☀ Light</option>
            </select>
          </div>

          {/* Notifications */}

          <div className="setting-card">
            <h3>🔔 Notifications</h3>

            <label>
              <input type="checkbox" />
              Enable Notifications
            </label>
          </div>

          {/* Privacy */}

          <div className="setting-card">
            <h3>🔒 Privacy</h3>

            <button>Manage Permissions</button>
          </div>
        </div>
      </div>
    </>
  );
}

export default Settings;
