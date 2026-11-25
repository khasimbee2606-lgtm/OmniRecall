import "../assets/styles/filterBar.css";

const filters = ["All", "People", "Places", "Documents", "Travel", "Events"];

function FilterBar({ filter, setFilter }) {
  return (
    <div className="filter-bar">
      {filters.map((item) => (
        <button
          key={item}
          className={filter === item ? "active" : ""}
          onClick={() => setFilter(item)}
        >
          {item}
        </button>
      ))}
    </div>
  );
}

export default FilterBar;
