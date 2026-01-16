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
    <div style={styles.page}>
      {/* HEADER */}
      <header style={styles.header}>
        <h1 style={styles.mainTitle}>
          Question Paper Generation System
        </h1>
        <p style={styles.subtitle}>
          An intelligent NLP-based academic assessment platform
        </p>
      </header>

      {/* SYLLABUS SECTION */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>
          Syllabus Upload & Topic Extraction
        </h2>

        <label style={styles.uploadButtonBlue}>
          Upload Syllabus PDF
          <input
            type="file"
            accept=".pdf"
            onChange={uploadSyllabus}
            hidden
          />
        </label>

        {syllabusLoading && (
          <p style={styles.loadingBlue}>Processing syllabus…</p>
        )}

        {topics &&
          Object.keys(topics).map((module) => (
            <div key={module} style={styles.moduleBlock}>
              <span style={styles.moduleBadge}>{module}</span>
              <ul style={styles.list}>
                {topics[module].map((topic, index) => (
                  <li key={index}>{topic}</li>
                ))}
              </ul>
            </div>
          ))}
      </section>

      {/* TEXTBOOK SECTION */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>
          Textbook Upload & Content Chunking
        </h2>

        <label style={styles.uploadButtonPurple}>
          Upload Textbook PDF
          <input
            type="file"
            accept=".pdf"
            onChange={uploadTextbook}
            hidden
          />
        </label>

        {textbookLoading && (
          <p style={styles.loadingPurple}>Chunking textbook…</p>
        )}

        {chunkCount > 0 && (
          <>
            <p style={styles.chunkCount}>
              <strong>Total Chunks Generated:</strong> {chunkCount}
            </p>

            <ul style={styles.list}>
              {chunks.slice(0, 5).map((chunk, index) => (
                <li key={index} style={styles.chunkItem}>
                  {chunk}
                </li>
              ))}
            </ul>
          </>
        )}
      </section>
    </div>
  );
}

/* ================= STYLES ================= */

const styles = {
  page: {
    minHeight: "100vh",
    padding: "50px 80px",
    background:
      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "#ffffff",
  },

  /* HEADER */
  header: {
    textAlign: "center",
    marginBottom: "60px",
  },
  mainTitle: {
    fontSize: "38px",
    fontWeight: "600",
    letterSpacing: "0.6px",
    marginBottom: "10px",
  },
  subtitle: {
    fontSize: "16px",
    opacity: 0.9,
    fontStyle: "italic",
  },

  /* SECTIONS */
  section: {
    marginBottom: "70px",
  },
  sectionTitle: {
    fontSize: "22px",
    fontWeight: "600",
    marginBottom: "20px",
    borderBottom: "1px solid rgba(255,255,255,0.25)",
    paddingBottom: "8px",
  },

  /* BUTTONS */
  uploadButtonBlue: {
    display: "inline-block",
    background: "linear-gradient(135deg, #3b82f6, #2563eb)",
    color: "#ffffff",
    padding: "10px 26px",
    borderRadius: "30px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
    marginBottom: "15px",
    boxShadow: "0 6px 15px rgba(37,99,235,0.35)",
  },
  uploadButtonPurple: {
    display: "inline-block",
    background: "linear-gradient(135deg, #8b5cf6, #6d28d9)",
    color: "#ffffff",
    padding: "10px 26px",
    borderRadius: "30px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
    marginBottom: "15px",
    boxShadow: "0 6px 15px rgba(109,40,217,0.35)",
  },

  /* LOADING */
  loadingBlue: {
    marginTop: "10px",
    color: "#dbeafe",
  },
  loadingPurple: {
    marginTop: "10px",
    color: "#ede9fe",
  },

  /* CONTENT */
  moduleBlock: {
    marginTop: "20px",
  },
  moduleBadge: {
    display: "inline-block",
    background: "rgba(255,255,255,0.2)",
    padding: "4px 14px",
    borderRadius: "20px",
    fontSize: "13px",
    marginBottom: "8px",
  },
  list: {
    paddingLeft: "20px",
    marginTop: "8px",
  },
  chunkCount: {
    marginTop: "15px",
    marginBottom: "10px",
  },
  chunkItem: {
    background: "rgba(255,255,255,0.12)",
    padding: "10px",
    borderRadius: "8px",
    marginBottom: "10px",
    lineHeight: "1.5",
  },
};

export default App;
