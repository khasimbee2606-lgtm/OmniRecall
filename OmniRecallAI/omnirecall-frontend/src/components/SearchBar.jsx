import "./../assets/styles/searchBar.css";
import { Search } from "lucide-react";

function SearchBar({ value, onChange, placeholder }) {
  return (
    <div className="search-bar">
      <Search size={20} className="search-icon" />

      <input
        type="text"
        placeholder={placeholder || "Search..."}
        value={value}
        onChange={onChange}
      />
    </div>
  );
}

export default SearchBar;
