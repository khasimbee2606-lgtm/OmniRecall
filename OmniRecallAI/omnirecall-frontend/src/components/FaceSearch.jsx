function FaceSearch() {
  return (
    <div className="card">
      <h2>Face Recognition Search</h2>

      <input
        type="text"
        placeholder="Search person name..."
        style={{ width: "100%", marginTop: "15px" }}
      />

      <button style={{ marginTop: "15px" }}>Search Face</button>
    </div>
  );
}

export default FaceSearch;
