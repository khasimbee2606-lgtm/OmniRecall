function ImagePreview({ image }) {
  return (
    <div className="card">
      <img
        src={image}
        alt="preview"
        style={{
          width: "100%",
          borderRadius: "10px",
          objectFit: "cover",
        }}
      />
    </div>
  );
}

export default ImagePreview;
