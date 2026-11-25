import { X, Trash2 } from "lucide-react";
import "../assets/styles/documents.css";

function PDFViewer({ document, onClose, onDelete }) {
  if (!document) return null;

  return (
    <div className="pdf-viewer-overlay">
      <div className="pdf-viewer-content">
        <button className="pdf-close-btn" onClick={onClose}>
          <X size={22} />
        </button>

        <iframe src={document.file} title="PDF Viewer" className="pdf-frame" />

        <button
          className="pdf-delete-btn"
          onClick={() => onDelete(document.filename)}
        >
          <Trash2 size={20} />
        </button>
      </div>
    </div>
  );
}

export default PDFViewer;
