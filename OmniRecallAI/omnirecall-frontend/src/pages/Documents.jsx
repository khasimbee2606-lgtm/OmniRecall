import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import SearchBar from "../components/SearchBar";
import VoiceSearch from "../components/VoiceSearch";
import DocumentCard from "../components/DocumentCard";
import PDFViewer from "../components/PDFViewer";

import API from "../services/api";

import "../assets/styles/documents.css";

function Documents() {
  const [documents, setDocuments] = useState([]);
  const [allDocuments, setAllDocuments] = useState([]);
  const [viewer, setViewer] = useState(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    loadDocuments();
  }, []);

  async function loadDocuments() {
    try {
      const res = await API.get("/documents");

      setDocuments(res.data);
      setAllDocuments(res.data);
    } catch (err) {
      console.log(err);
    }
  }

  async function searchDocuments(text) {
    setQuery(text);

    if (text.trim() === "") {
      setDocuments(allDocuments);
      return;
    }

    try {
      const res = await API.post("/pdf_search", {
        query: text,
      });

      setDocuments(res.data);
    } catch (err) {
      console.log(err);
    }
  }

  async function deletePDF(filename) {
    try {
      await API.delete(`/delete_pdf/${filename}`);

      setViewer(null);

      loadDocuments();
    } catch (err) {
      console.log(err);
    }
  }

  return (
    <>
      <Sidebar />

      <div className="documents-page">
        <Navbar />

        <div className="documents-container">
          {/* Header */}

          <div className="documents-header">
            <h1>📄 Documents</h1>

            <p>Search your uploaded PDF files instantly.</p>
          </div>

          {/* Search */}

          <div className="documents-search">
            <SearchBar
              value={query}
              placeholder="Search documents..."
              onChange={(e) => searchDocuments(e.target.value)}
            />

            <VoiceSearch
              onResult={(text) => {
                searchDocuments(text);
              }}
            />
          </div>

          {/* Count */}

          <div className="documents-count">
            Total Documents : <strong>{documents.length}</strong>
          </div>

          {/* Grid */}

          <div className="documents-grid">
            {documents.length === 0 ? (
              <div className="no-documents">No PDF files uploaded.</div>
            ) : (
              documents.map((doc) => (
                <DocumentCard
                  key={doc.id}
                  document={doc}
                  onOpen={setViewer}
                  onDelete={deletePDF}
                />
              ))
            )}
          </div>
        </div>

        {/* PDF Viewer */}

        {viewer && (
          <PDFViewer
            document={viewer}
            onClose={() => setViewer(null)}
            onDelete={deletePDF}
          />
        )}
      </div>
    </>
  );
}

export default Documents;
