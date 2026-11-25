import { Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Gallery from "./pages/Gallery";
import Documents from "./pages/Documents";
import Search from "./pages/Search";
import Videos from "./pages/Videos";

import Settings from "./pages/Settings";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />

      <Route path="/register" element={<Register />} />

      <Route path="/dashboard" element={<Dashboard />} />

      <Route path="/upload" element={<Upload />} />

      <Route path="/gallery" element={<Gallery />} />

      <Route path="/documents" element={<Documents />} />

      <Route path="/search" element={<Search />} />
      <Route path="/videos" element={<Videos />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  );
}

export default App;
