import { Trash2 } from "lucide-react";
import "../assets/styles/documents.css";

function DocumentCard({ document, onOpen, onDelete }) {
  return (
    <div className="document-card" onClick={() => onOpen(document)}>
      <img src={document.thumbnail} alt="" className="document-thumbnail" />

      <button
        className="delete-icon"
        onClick={(e) => {
          e.stopPropagation();
          onDelete(document.filename);
        }}
      >
        <Trash2 size={18} />
      </button>
    </div>
  );
}

export default DocumentCard;
