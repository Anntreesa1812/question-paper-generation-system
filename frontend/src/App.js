import React, { useState } from "react";

function App() {
  // ---------- SYLLABUS STATE ----------
  const [topics, setTopics] = useState(null);
  const [syllabusLoading, setSyllabusLoading] = useState(false);

  // ---------- TEXTBOOK STATE ----------
  const [chunks, setChunks] = useState([]);
  const [chunkCount, setChunkCount] = useState(0);
  const [textbookLoading, setTextbookLoading] = useState(false);

  // ================================
  // SYLLABUS UPLOAD
  // ================================
  const uploadSyllabus = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setSyllabusLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/extract-syllabus",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();
      setTopics(data);
    } catch (error) {
      alert("Error uploading syllabus");
    }

    setSyllabusLoading(false);
  };

  // ================================
  // TEXTBOOK UPLOAD & CHUNKING
  // ================================
  const uploadTextbook = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setTextbookLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/chunk-textbook",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();
      setChunks(data.chunks || []);
      setChunkCount(data.total_chunks || 0);
    } catch (error) {
      alert("Error uploading textbook");
    }

    setTextbookLoading(false);
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h2>📄 Question Paper Generation System</h2>

      {/* ================= SYLLABUS SECTION ================= */}
      <hr />
      <h3>📘 Syllabus Upload & Topic Extraction</h3>

      <input type="file" accept=".pdf" onChange={uploadSyllabus} />

      {syllabusLoading && <p>Processing syllabus...</p>}

      {topics &&
        Object.keys(topics).map((module) => (
          <div key={module}>
            <h4>{module}</h4>
            <ul>
              {topics[module].map((topic, index) => (
                <li key={index}>{topic}</li>
              ))}
            </ul>
          </div>
        ))}

      {/* ================= TEXTBOOK SECTION ================= */}
      <hr />
      <h3>📕 Textbook Upload & Chunking</h3>

      <input type="file" accept=".pdf" onChange={uploadTextbook} />

      {textbookLoading && <p>Chunking textbook...</p>}

      {chunkCount > 0 && (
        <>
          <p>
            <strong>Total Chunks:</strong> {chunkCount}
          </p>

          <h4>Sample Chunks</h4>
          <ul>
            {chunks.slice(0, 5).map((chunk, index) => (
              <li key={index}>{chunk}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default App;
