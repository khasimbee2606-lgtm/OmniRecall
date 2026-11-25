function MemoryCard({ title, image, description }) {
  return (
    <div className="card">
      <img
        src={image}
        alt={title}
        style={{ width: "100%", borderRadius: "10px" }}
      />

      <h3 style={{ marginTop: "10px" }}>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

export default MemoryCard;
