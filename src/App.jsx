import React, { useState } from "react";

const BLOOM_LEVELS = [
  "Remember",
  "Understand",
  "Apply",
  "Analyze",
  "Evaluate",
  "Create",
];

const MODULES = ["Module 1", "Module 2", "Module 3", "Module 4"];

function App() {
  // ---------- SYLLABUS STATE ----------
  const [topics, setTopics] = useState(null);
  const [syllabusLoading, setSyllabusLoading] = useState(false);

  // ---------- TEXTBOOK STATE ----------
  const [chunks, setChunks] = useState([]);
  const [chunkCount, setChunkCount] = useState(0);
  const [textbookLoading, setTextbookLoading] = useState(false);

  // ---------- PATTERN STATE ----------
  const [examName, setExamName] = useState("Mid-Semester Exam");
  const [parts, setParts] = useState([
    {
      part_name: "Part A",
      answer_type: "ALL",
      marks_per_question: 1,
      total_questions: 10,
      questions_to_answer: 10,
      bloom_levels: ["Remember", "Understand"],
      questions: [
        { question_no: 1, marks: 1, module: "Module 1", bloom_level: "Remember", has_internal_choice: false, sub_questions: [] },
        { question_no: 2, marks: 1, module: "Module 2", bloom_level: "Understand", has_internal_choice: false, sub_questions: [] },
      ],
    },
  ]);
  const [expandedParts, setExpandedParts] = useState({});
  const [patternLoading, setPatternLoading] = useState(false);

  // ---------- GENERATION STATE ----------
  const [generationLoading, setGenerationLoading] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState({});
  const [generationError, setGenerationError] = useState(null);

  // ================================
  // PATTERN CONFIGURATION
  // ================================
  const setQuestionPattern = async () => {
    const pattern = {
      exam_name: examName,
      parts: parts,
    };

    setPatternLoading(true);
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/set-question-pattern",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(pattern),
        }
      );

      const data = await response.json();
      console.log("Pattern saved:", data);
      alert("Pattern saved successfully!");
    } catch (error) {
      console.error("Error setting pattern:", error);
      alert("Error setting question pattern");
    }
    setPatternLoading(false);
  };

  // ================================
  // QUESTION GENERATION
  // ================================
  const generateQuestions = async () => {
    const pattern = {
      exam_name: examName,
      parts: parts,
    };

    setGenerationLoading(true);
    setGenerationError(null);
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/generate-questions",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(pattern),
        }
      );

      const data = await response.json();
      console.log("Generated questions:", data);
      
      if (data.questions) {
        setGeneratedQuestions(data.questions);
        alert("Questions generated successfully!");
      } else {
        setGenerationError("No questions generated");
      }
    } catch (error) {
      console.error("Error generating questions:", error);
      setGenerationError("Failed to generate questions");
      alert("Error generating questions");
    }
    setGenerationLoading(false);
  };

  // ================================
  // HELPER FUNCTIONS
  // ================================
  const updatePart = (partIndex, field, value) => {
    const updatedParts = [...parts];
    updatedParts[partIndex] = { ...updatedParts[partIndex], [field]: value };
    setParts(updatedParts);
  };

  const updateQuestion = (partIndex, qIndex, field, value) => {
    const updatedParts = [...parts];
    updatedParts[partIndex].questions[qIndex] = {
      ...updatedParts[partIndex].questions[qIndex],
      [field]: value,
    };
    setParts(updatedParts);
  };

  const addPart = () => {
    const newPart = {
      part_name: `Part ${String.fromCharCode(65 + parts.length)}`,
      answer_type: "ALL",
      marks_per_question: 2,
      total_questions: 5,
      questions_to_answer: 5,
      bloom_levels: ["Apply"],
      questions: [{ question_no: 1, marks: 2, module: "Module 1", bloom_level: "Apply", has_internal_choice: false, sub_questions: [] }],
    };
    setParts([...parts, newPart]);
  };

  const removePart = (partIndex) => {
    if (parts.length > 1) {
      setParts(parts.filter((_, i) => i !== partIndex));
    }
  };

  const togglePartExpansion = (partIndex) => {
    setExpandedParts({
      ...expandedParts,
      [partIndex]: !expandedParts[partIndex],
    });
  };

  const calculateSummary = () => {
    let totalQuestions = 0;
    let totalMarks = 0;
    parts.forEach((part) => {
      totalQuestions += part.total_questions;
      totalMarks += part.marks_per_question * part.total_questions;
    });
    return { totalQuestions, totalMarks };
  };
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

  const summary = calculateSummary();

  return (
    <div style={styles.page}>
      {/* HEADER */}
      <header style={styles.header}>
        <h1 style={styles.mainTitle}>Question Paper Generation System</h1>
        <p style={styles.subtitle}>An intelligent NLP-based academic assessment platform</p>
      </header>

      {/* SYLLABUS SECTION */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>Syllabus Upload & Topic Extraction</h2>
        <label style={styles.uploadButtonBlue}>
          Upload Syllabus PDF
          <input type="file" accept=".pdf" onChange={uploadSyllabus} hidden />
        </label>
        {syllabusLoading && <p style={styles.loadingBlue}>Processing syllabus…</p>}
        {topics && Object.keys(topics).map((module) => (
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
        <h2 style={styles.sectionTitle}>Textbook Upload & Content Chunking</h2>
        <label style={styles.uploadButtonPurple}>
          Upload Textbook PDF
          <input type="file" accept=".pdf" onChange={uploadTextbook} hidden />
        </label>
        {textbookLoading && <p style={styles.loadingPurple}>Chunking textbook…</p>}
        {chunkCount > 0 && (
          <>
            <p style={styles.chunkCount}><strong>Total Chunks Generated:</strong> {chunkCount}</p>
            <ul style={styles.list}>
              {chunks.slice(0, 5).map((chunk, index) => (
                <li key={index} style={styles.chunkItem}>{chunk}</li>
              ))}
            </ul>
          </>
        )}
      </section>

      {/* PATTERN CONFIGURATION SECTION */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>Question Pattern Configuration</h2>
        
        {/* Exam Name */}
        <div style={styles.formGroup}>
          <label style={styles.label}>Exam Name:</label>
          <input
            type="text"
            value={examName}
            onChange={(e) => setExamName(e.target.value)}
            style={styles.input}
          />
        </div>

        {/* Summary Card */}
        <div style={styles.summaryCard}>
          <div><strong>Total Questions:</strong> {summary.totalQuestions}</div>
          <div><strong>Total Marks:</strong> {summary.totalMarks}</div>
        </div>

        {/* Parts */}
        {parts.map((part, partIndex) => (
          <div key={partIndex} style={styles.partContainer}>
            <div style={styles.partHeader} onClick={() => togglePartExpansion(partIndex)}>
              <span style={styles.partName}>{part.part_name}</span>
              <span style={styles.expandIcon}>{expandedParts[partIndex] ? "▼" : "▶"}</span>
            </div>

            {expandedParts[partIndex] && (
              <div style={styles.partContent}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Answer Type:</label>
                  <select
                    value={part.answer_type}
                    onChange={(e) => updatePart(partIndex, "answer_type", e.target.value)}
                    style={styles.input}
                  >
                    <option value="ALL">Answer All</option>
                    <option value="ANY">Answer Any</option>
                  </select>
                </div>

                <div style={styles.formGroup}>
                  <label style={styles.label}>Marks Per Question:</label>
                  <input
                    type="number"
                    value={part.marks_per_question}
                    onChange={(e) => updatePart(partIndex, "marks_per_question", parseInt(e.target.value))}
                    style={styles.input}
                  />
                </div>

                <div style={styles.formGroup}>
                  <label style={styles.label}>Total Questions:</label>
                  <input
                    type="number"
                    value={part.total_questions}
                    onChange={(e) => updatePart(partIndex, "total_questions", parseInt(e.target.value))}
                    style={styles.input}
                  />
                </div>

                {/* Questions in this part */}
                <div style={styles.questionsContainer}>
                  <h4>Questions:</h4>
                  {part.questions.map((question, qIndex) => (
                    <div key={qIndex} style={styles.questionCard}>
                      <div style={styles.formGroup}>
                        <label style={styles.label}>Question {question.question_no} - Module:</label>
                        <select
                          value={question.module}
                          onChange={(e) => updateQuestion(partIndex, qIndex, "module", e.target.value)}
                          style={styles.input}
                        >
                          {MODULES.map((m) => (
                            <option key={m} value={m}>{m}</option>
                          ))}
                        </select>
                      </div>

                      <div style={styles.formGroup}>
                        <label style={styles.label}>Bloom Level:</label>
                        <select
                          value={question.bloom_level}
                          onChange={(e) => updateQuestion(partIndex, qIndex, "bloom_level", e.target.value)}
                          style={styles.input}
                        >
                          {BLOOM_LEVELS.map((level) => (
                            <option key={level} value={level}>{level}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  ))}
                </div>

                <button onClick={() => removePart(partIndex)} style={styles.deleteButton}>
                  Remove {part.part_name}
                </button>
              </div>
            )}
          </div>
        ))}

        <button onClick={addPart} style={styles.addButton}>+ Add Part</button>

        <div style={styles.actionButtons}>
          <button onClick={setQuestionPattern} disabled={patternLoading} style={styles.saveButton}>
            {patternLoading ? "Saving..." : "Save Pattern"}
          </button>
          <button onClick={generateQuestions} disabled={generationLoading} style={styles.generateButton}>
            {generationLoading ? "Generating..." : "Generate Questions"}
          </button>
        </div>
      </section>

      {/* GENERATED QUESTIONS SECTION */}
      {generatedQuestions && Object.keys(generatedQuestions).length > 0 && (
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Generated Questions</h2>
          {Object.entries(generatedQuestions).map(([partName, questions]) => (
            <div key={partName} style={styles.generatedPart}>
              <h3 style={styles.partNameHeading}>{partName}</h3>
              {Array.isArray(questions) && questions.map((question, idx) => (
                <div key={idx} style={styles.generatedQuestion}>
                  <p><strong>Q{idx + 1}:</strong> {question.text || question.question_text || "No text provided"}</p>
                  <p style={styles.questionMeta}>
                    Marks: {question.marks} | Module: {question.module} | Bloom: {question.bloom_level}
                  </p>
                </div>
              ))}
            </div>
          ))}
        </section>
      )}

      {generationError && (
        <div style={styles.errorMessage}>{generationError}</div>
      )}
    </div>
  );
}

/* ================= STYLES ================= */

const styles = {
  page: {
    minHeight: "100vh",
    padding: "50px 80px",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "#ffffff",
  },

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

  section: {
    marginBottom: "70px",
    background: "rgba(255,255,255,0.08)",
    padding: "25px",
    borderRadius: "15px",
    backdropFilter: "blur(10px)",
    border: "1px solid rgba(255,255,255,0.15)",
  },
  sectionTitle: {
    fontSize: "22px",
    fontWeight: "600",
    marginBottom: "20px",
    borderBottom: "1px solid rgba(255,255,255,0.25)",
    paddingBottom: "8px",
  },

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

  loadingBlue: {
    marginTop: "10px",
    color: "#dbeafe",
  },
  loadingPurple: {
    marginTop: "10px",
    color: "#ede9fe",
  },

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

  // Form styles
  formGroup: {
    marginBottom: "15px",
  },
  label: {
    display: "block",
    marginBottom: "5px",
    fontSize: "14px",
    fontWeight: "500",
  },
  input: {
    width: "100%",
    padding: "10px 12px",
    borderRadius: "8px",
    border: "1px solid rgba(255,255,255,0.3)",
    background: "rgba(255,255,255,0.1)",
    color: "#ffffff",
    fontSize: "14px",
    boxSizing: "border-box",
  },

  summaryCard: {
    background: "rgba(255,255,255,0.15)",
    padding: "15px 20px",
    borderRadius: "10px",
    marginBottom: "20px",
    display: "flex",
    gap: "30px",
    fontSize: "16px",
  },

  partContainer: {
    background: "rgba(255,255,255,0.08)",
    borderRadius: "10px",
    marginBottom: "15px",
    border: "1px solid rgba(255,255,255,0.2)",
    overflow: "hidden",
  },
  partHeader: {
    padding: "15px 20px",
    cursor: "pointer",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    background: "rgba(255,255,255,0.12)",
    fontWeight: "600",
  },
  partName: {
    fontSize: "16px",
  },
  expandIcon: {
    fontSize: "12px",
    opacity: 0.7,
  },
  partContent: {
    padding: "20px",
  },

  questionsContainer: {
    marginTop: "20px",
    paddingTop: "20px",
    borderTop: "1px solid rgba(255,255,255,0.2)",
  },
  questionCard: {
    background: "rgba(255,255,255,0.08)",
    padding: "15px",
    borderRadius: "8px",
    marginBottom: "12px",
    border: "1px solid rgba(255,255,255,0.15)",
  },

  addButton: {
    background: "linear-gradient(135deg, #10b981, #059669)",
    color: "#ffffff",
    padding: "10px 20px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    marginTop: "15px",
    fontSize: "14px",
    fontWeight: "500",
  },
  deleteButton: {
    background: "linear-gradient(135deg, #ef4444, #dc2626)",
    color: "#ffffff",
    padding: "8px 16px",
    borderRadius: "6px",
    border: "none",
    cursor: "pointer",
    fontSize: "13px",
    marginTop: "10px",
  },

  actionButtons: {
    display: "flex",
    gap: "15px",
    marginTop: "25px",
  },
  saveButton: {
    background: "linear-gradient(135deg, #06b6d4, #0891b2)",
    color: "#ffffff",
    padding: "12px 24px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontSize: "15px",
    fontWeight: "600",
    flex: 1,
  },
  generateButton: {
    background: "linear-gradient(135deg, #f59e0b, #d97706)",
    color: "#ffffff",
    padding: "12px 24px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontSize: "15px",
    fontWeight: "600",
    flex: 1,
  },

  generatedPart: {
    marginBottom: "30px",
    background: "rgba(255,255,255,0.08)",
    padding: "20px",
    borderRadius: "10px",
    border: "1px solid rgba(255,255,255,0.2)",
  },
  partNameHeading: {
    fontSize: "18px",
    marginBottom: "15px",
    color: "#fbbf24",
  },
  generatedQuestion: {
    background: "rgba(255,255,255,0.1)",
    padding: "15px",
    borderRadius: "8px",
    marginBottom: "12px",
    lineHeight: "1.6",
  },
  questionMeta: {
    fontSize: "13px",
    opacity: 0.8,
    marginTop: "8px",
  },

  errorMessage: {
    background: "rgba(239,68,68,0.2)",
    border: "1px solid rgba(239,68,68,0.5)",
    padding: "15px",
    borderRadius: "8px",
    color: "#fca5a5",
  },
};

export default App;
