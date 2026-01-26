import React, { useState } from "react";

// Constants for Bloom Levels and Modules
const BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"];
const MODULES = ["Module 1", "Module 2", "Module 3", "Module 4"];

function App() {
  // ---------- SYLLABUS STATE ----------
  const [topics, setTopics] = useState(null);
  const [syllabusLoading, setSyllabusLoading] = useState(false);

  // ---------- TEXTBOOK STATE ----------
  const [chunks, setChunks] = useState([]);
  const [chunkCount, setChunkCount] = useState(0);
  const [textbookLoading, setTextbookLoading] = useState(false);

  // ---------- QUESTION PATTERN STATE ----------
  const [patternLoading, setPatternLoading] = useState(false);
  const [examName, setExamName] = useState("");
  const [parts, setParts] = useState([
    {
      part_name: "PART A",
      answer_type: "ALL",
      marks_per_question: 1,
      total_questions: 2,
      questions_to_answer: null,
      bloom_levels: ["Remember"],
      questions: [
        {
          question_no: 1,
          marks: 1,
          module: "Module 1",
          bloom_level: "Remember",
          has_internal_choice: false,
          sub_questions: null
        },
        {
          question_no: 2,
          marks: 1,
          module: "Module 2",
          bloom_level: "Remember",
          has_internal_choice: false,
          sub_questions: null
        }
      ]
    }
  ]);

  // ---------- COLLAPSIBLE PARTS STATE ----------
  const [expandedParts, setExpandedParts] = useState([0]); // Default: first part expanded

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

  // ================================
  // SET QUESTION PATTERN
  // ================================
  const setQuestionPattern = async () => {
    if (!examName) {
      alert("Please enter exam name");
      return;
    }

    if (parts.length === 0) {
      alert("Please add at least one part");
      return;
    }

    // Validate all parts have questions
    for (let part of parts) {
      if (!part.part_name) {
        alert("Please fill in all part names");
        return;
      }
      if (!part.questions || part.questions.length === 0) {
        alert(`${part.part_name} must have at least one question`);
        return;
      }
    }

    const patternData = {
      exam_name: examName,
      parts: parts
    };

    setPatternLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/set-question-pattern",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(patternData)
        }
      );

      const data = await response.json();
      alert("Question pattern saved successfully!");
      console.log("Generation Plan:", data.generation_plan);
    } catch (error) {
      alert("Error setting question pattern: " + error.message);
      console.error(error);
    }

    setPatternLoading(false);
  };

  // Update part
  const updatePart = (partIndex, field, value) => {
    const newParts = [...parts];
    newParts[partIndex][field] = value;
    setParts(newParts);
  };

  // Update question in a part
  const updateQuestion = (partIndex, questionIndex, field, value) => {
    const newParts = [...parts];
    newParts[partIndex].questions[questionIndex][field] = value;
    setParts(newParts);
  };

  // Add new part
  const addPart = () => {
    const partNum = String.fromCharCode(64 + parts.length + 1); // A, B, C...
    setParts([...parts, {
      part_name: `PART ${partNum}`,
      answer_type: "ALL",
      marks_per_question: 1,
      total_questions: 1,
      questions_to_answer: null,
      bloom_levels: ["Remember"],
      questions: [
        {
          question_no: 1,
          marks: 1,
          module: "Module 1",
          bloom_level: "Remember",
          has_internal_choice: false,
          sub_questions: null
        }
      ]
    }]);
  };

  // Remove part
  const removePart = (partIndex) => {
    setParts(parts.filter((_, i) => i !== partIndex));
  };

  // Add question to part
  const addQuestionToPart = (partIndex) => {
    const newParts = [...parts];
    const newQNum = newParts[partIndex].questions.length + 1;
    newParts[partIndex].questions.push({
      question_no: newQNum,
      marks: newParts[partIndex].marks_per_question || 1,
      module: "Module 1",
      bloom_level: "Remember",
      has_internal_choice: false,
      sub_questions: null
    });
    newParts[partIndex].total_questions = newParts[partIndex].questions.length;
    setParts(newParts);
  };

  // Remove question from part
  const removeQuestionFromPart = (partIndex, questionIndex) => {
    const newParts = [...parts];
    newParts[partIndex].questions = newParts[partIndex].questions.filter(
      (_, i) => i !== questionIndex
    );
    // Re-number questions
    newParts[partIndex].questions = newParts[partIndex].questions.map(
      (q, i) => ({ ...q, question_no: i + 1 })
    );
    newParts[partIndex].total_questions = newParts[partIndex].questions.length;
    setParts(newParts);
  };

  // Toggle part expansion
  const togglePartExpansion = (partIndex) => {
    setExpandedParts((prev) =>
      prev.includes(partIndex)
        ? prev.filter((i) => i !== partIndex)
        : [...prev, partIndex]
    );
  };

  // Calculate summary statistics
  const calculateSummary = () => {
    let totalQuestions = 0;
    let totalMarks = 0;
    const partStats = parts.map((part) => {
      const qCount = part.questions?.length || 0;
      const pMarks = part.questions?.reduce((sum, q) => sum + (q.marks || 0), 0) || 0;
      totalQuestions += qCount;
      totalMarks += pMarks;
      return { questions: qCount, marks: pMarks };
    });
    return { totalQuestions, totalMarks, partStats };
  };

  // Calculate marks for a specific part
  const getPartMarks = (partIndex) => {
    return (
      parts[partIndex]?.questions?.reduce((sum, q) => sum + (q.marks || 0), 0) || 0
    );
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
          <p className="loading">Processing syllabus…</p>
        )}

        {topics &&
          Object.keys(topics).map((module) => {
            const value = topics[module];

            return (
              <div key={module} style={styles.moduleBlock}>
                <span className="module-badge">{module}</span>
                <ul style={styles.list}>
                  {Array.isArray(value)
                    ? value.map((topic, index) => (
                        <li key={index}>{topic}</li>
                      ))
                    : Array.isArray(value?.topics)
                    ? value.topics.map((topic, index) => (
                        <li key={index}>{topic}</li>
                      ))
                    : (
                        <li>{String(value)}</li>
                      )}
                </ul>
              </div>
            );
          })}
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
          <p className="loading">Chunking textbook…</p>
        )}

        {chunkCount > 0 && (
          <>
            <p style={styles.chunkCount}>
              <strong>Total Chunks Generated:</strong> {chunkCount}
            </p>

            <ul style={styles.list}>
              {chunks.slice(0, 5).map((chunk, index) => (
                <li key={index} className="chunk-item">
                  {chunk}
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      {/* QUESTION PATTERN SECTION */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>
          Question Paper Pattern Configuration
        </h2>

        {/* Summary Card */}
        {examName && parts.length > 0 && (() => {
          const summary = calculateSummary();
          return (
            <div style={styles.summaryCard}>
              <h3 style={styles.summaryTitle}>📊 Pattern Summary</h3>
              <div style={styles.summaryGrid}>
                <div style={styles.summaryItem}>
                  <span style={styles.summaryLabel}>Total Questions:</span>
                  <span style={styles.summaryValue}>{summary.totalQuestions}</span>
                </div>
                <div style={styles.summaryItem}>
                  <span style={styles.summaryLabel}>Total Marks:</span>
                  <span style={styles.summaryValue}>{summary.totalMarks}</span>
                </div>
                {summary.partStats.map((stat, idx) => (
                  <div key={idx} style={styles.summaryItem}>
                    <span style={styles.summaryLabel}>{parts[idx].part_name}:</span>
                    <span style={styles.summaryValue}>
                      {stat.questions}Q / {stat.marks}M
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })()}

        {/* Exam Name Input */}
        <div style={styles.formGroup}>
          <label style={styles.label}>Exam Name:</label>
          <input
            type="text"
            value={examName}
            onChange={(e) => setExamName(e.target.value)}
            placeholder="e.g., Mid Semester Exam"
            style={styles.input}
          />
        </div>

        {/* Parts Configuration */}
        <div style={styles.partsContainer}>
          <h3 style={styles.subTitle}>Question Parts</h3>

          {parts.map((part, partIndex) => (
            <div key={partIndex} style={styles.partBlock}>
              <div style={styles.partHeader}>
                <div style={styles.partHeaderLeft}>
                  <button
                    onClick={() => togglePartExpansion(partIndex)}
                    style={styles.expandButton}
                    title={expandedParts.includes(partIndex) ? "Collapse" : "Expand"}
                  >
                    {expandedParts.includes(partIndex) ? "▼" : "▶"}
                  </button>
                  <h4 style={styles.partTitle}>{part.part_name}</h4>
                  <span style={styles.partStats}>
                    {part.questions?.length || 0} Questions • {getPartMarks(partIndex)} Marks
                  </span>
                </div>
                {parts.length > 1 && (
                  <button
                    onClick={() => removePart(partIndex)}
                    style={styles.removeButton}
                  >
                    Remove Part
                  </button>
                )}
              </div>

              {/* Part Settings - Collapsible */}
              {expandedParts.includes(partIndex) && (
                <div style={styles.partSettings}>
                  <div style={styles.formRow3}>
                    <div style={styles.formGroup}>
                      <label>Part Name:</label>
                      <input
                        type="text"
                        value={part.part_name}
                        onChange={(e) =>
                          updatePart(partIndex, "part_name", e.target.value)
                        }
                        placeholder="e.g., PART A"
                        style={styles.input}
                      />
                    </div>

                    <div style={styles.formGroup}>
                      <label>Answer Type:</label>
                      <select
                        value={part.answer_type}
                        onChange={(e) =>
                          updatePart(partIndex, "answer_type", e.target.value)
                        }
                        style={styles.input}
                      >
                        <option value="ALL">ALL (Answer All Questions)</option>
                        <option value="ANY">ANY (Answer Any N Questions)</option>
                      </select>
                    </div>

                    <div style={styles.formGroup}>
                      <label>Bloom Levels (comma-separated):</label>
                      <input
                        type="text"
                        value={part.bloom_levels.join(", ")}
                        onChange={(e) =>
                          updatePart(
                            partIndex,
                            "bloom_levels",
                            e.target.value
                              .split(",")
                              .map((s) => s.trim())
                              .filter((s) => s)
                          )
                        }
                        placeholder="e.g., Remember, Understand"
                        style={styles.input}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Questions in Part */}
              {expandedParts.includes(partIndex) && (
                <div style={styles.questionsContainer}>
                <h5 style={styles.questionsTitle}>
                  Questions in {part.part_name}
                </h5>

                {part.questions &&
                  part.questions.map((question, qIndex) => (
                    <div key={qIndex} style={styles.questionBlock}>
                      <div style={styles.questionHeader}>
                        <span style={styles.questionNum}>
                          Q{question.question_no}
                        </span>
                        {part.questions.length > 1 && (
                          <button
                            onClick={() =>
                              removeQuestionFromPart(partIndex, qIndex)
                            }
                            style={styles.removeQButton}
                          >
                            Remove Q
                          </button>
                        )}
                      </div>

                      <div style={styles.questionFields}>
                        <div style={styles.formGroup}>
                          <label>Question No:</label>
                          <input
                            type="number"
                            value={question.question_no}
                            onChange={(e) =>
                              updateQuestion(
                                partIndex,
                                qIndex,
                                "question_no",
                                parseInt(e.target.value)
                              )
                            }
                            min="1"
                            style={styles.smallInput}
                          />
                        </div>

                        <div style={styles.formGroup}>
                          <label>Marks:</label>
                          <input
                            type="number"
                            value={question.marks}
                            onChange={(e) =>
                              updateQuestion(
                                partIndex,
                                qIndex,
                                "marks",
                                parseInt(e.target.value)
                              )
                            }
                            min="1"
                            style={styles.smallInput}
                          />
                        </div>

                        <div style={styles.formGroup}>
                          <label>Module:</label>
                          <select
                            value={question.module}
                            onChange={(e) =>
                              updateQuestion(
                                partIndex,
                                qIndex,
                                "module",
                                e.target.value
                              )
                            }
                            style={styles.smallInput}
                          >
                            {MODULES.map((mod) => (
                              <option key={mod} value={mod}>
                                {mod}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div style={styles.formGroup}>
                          <label>Bloom Level:</label>
                          <select
                            value={question.bloom_level || "Remember"}
                            onChange={(e) =>
                              updateQuestion(
                                partIndex,
                                qIndex,
                                "bloom_level",
                                e.target.value
                              )
                            }
                            style={styles.smallInput}
                          >
                            {BLOOM_LEVELS.map((level) => (
                              <option key={level} value={level}>
                                {level}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div style={styles.formGroup}>
                          <label>Has Internal Choice:</label>
                          <input
                            type="checkbox"
                            checked={question.has_internal_choice}
                            onChange={(e) =>
                              updateQuestion(
                                partIndex,
                                qIndex,
                                "has_internal_choice",
                                e.target.checked
                              )
                            }
                            style={styles.checkbox}
                          />
                        </div>
                      </div>
                    </div>
                  ))}

                <button
                  onClick={() => addQuestionToPart(partIndex)}
                  style={styles.addQButton}
                >
                  + Add Question to {part.part_name}
                </button>
                </div>
              )}
            </div>
          ))}
        </div>

        <button onClick={addPart} style={styles.addButton}>
          + Add Part
        </button>

        <button
          onClick={setQuestionPattern}
          disabled={patternLoading}
          style={styles.submitButton}
        >
          {patternLoading ? "Saving..." : "Save Question Pattern"}
        </button>
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

  header: {
    textAlign: "center",
    marginBottom: "60px",
  },
  mainTitle: {
    fontSize: "38px",
    fontWeight: "600",
    marginBottom: "10px",
  },
  subtitle: {
    fontSize: "16px",
    opacity: 0.9,
    fontStyle: "italic",
  },

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

  uploadButtonBlue: {
    display: "inline-block",
    background: "linear-gradient(135deg, #3b82f6, #2563eb)",
    padding: "10px 26px",
    borderRadius: "30px",
    cursor: "pointer",
    marginBottom: "15px",
  },
  uploadButtonPurple: {
    display: "inline-block",
    background: "linear-gradient(135deg, #8b5cf6, #6d28d9)",
    padding: "10px 26px",
    borderRadius: "30px",
    cursor: "pointer",
    marginBottom: "15px",
  },

  moduleBlock: {
    marginTop: "20px",
  },
  list: {
    paddingLeft: "20px",
    marginTop: "8px",
  },
  chunkCount: {
    marginTop: "15px",
    marginBottom: "10px",
  },

  summaryCard: {
    background: "linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(16, 185, 129, 0.15))",
    border: "1px solid rgba(74, 222, 128, 0.4)",
    borderRadius: "12px",
    padding: "18px",
    marginBottom: "25px",
    backdropFilter: "blur(10px)",
  },
  summaryTitle: {
    fontSize: "16px",
    fontWeight: "600",
    marginBottom: "12px",
    color: "#86efac",
  },
  summaryGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: "12px",
  },
  summaryItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "8px 12px",
    backgroundColor: "rgba(0, 0, 0, 0.2)",
    borderRadius: "6px",
    border: "1px solid rgba(255, 255, 255, 0.1)",
  },
  summaryLabel: {
    fontSize: "12px",
    color: "rgba(255, 255, 255, 0.7)",
  },
  summaryValue: {
    fontSize: "14px",
    fontWeight: "600",
    color: "#86efac",
    marginLeft: "8px",
  },

  formGroup: {
    marginBottom: "12px",
    display: "flex",
    flexDirection: "column",
  },
  label: {
    marginBottom: "5px",
    fontWeight: "500",
    fontSize: "14px",
  },
  input: {
    padding: "8px 12px",
    borderRadius: "6px",
    border: "1px solid rgba(255,255,255,0.3)",
    backgroundColor: "rgba(255,255,255,0.1)",
    color: "#fff",
    fontSize: "14px",
    fontFamily: "inherit",
  },
  smallInput: {
    padding: "6px 10px",
    borderRadius: "4px",
    border: "1px solid rgba(255,255,255,0.3)",
    backgroundColor: "rgba(255,255,255,0.1)",
    color: "#fff",
    fontSize: "13px",
    fontFamily: "inherit",
  },
  checkbox: {
    width: "20px",
    height: "20px",
    cursor: "pointer",
  },
  formRow3: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr 1fr",
    gap: "12px",
  },
  partHeaderLeft: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    flex: 1,
  },
  expandButton: {
    background: "none",
    border: "none",
    color: "#fbbf24",
    fontSize: "16px",
    cursor: "pointer",
    padding: "4px 8px",
    transition: "transform 0.2s",
    fontWeight: "600",
  },
  partStats: {
    fontSize: "12px",
    color: "rgba(255, 255, 255, 0.6)",
    fontStyle: "italic",
  },
  partsContainer: {
    marginTop: "25px",
    marginBottom: "20px",
  },
  subTitle: {
    fontSize: "16px",
    marginBottom: "15px",
    color: "rgba(255,255,255,0.95)",
  },
  partBlock: {
    padding: "18px",
    backgroundColor: "rgba(255,255,255,0.08)",
    borderRadius: "10px",
    marginBottom: "18px",
    border: "1px solid rgba(255,255,255,0.2)",
  },
  partHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "12px",
    paddingBottom: "8px",
    borderBottom: "1px solid rgba(255,255,255,0.15)",
  },
  partTitle: {
    fontSize: "15px",
    fontWeight: "600",
    margin: 0,
    color: "#fbbf24",
  },
  partSettings: {
    marginBottom: "18px",
    paddingBottom: "15px",
    borderBottom: "1px solid rgba(255,255,255,0.15)",
  },
  questionsContainer: {
    backgroundColor: "rgba(0,0,0,0.2)",
    padding: "12px",
    borderRadius: "8px",
    marginBottom: "12px",
  },
  questionsTitle: {
    fontSize: "13px",
    fontWeight: "600",
    marginBottom: "12px",
    color: "rgba(255,255,255,0.85)",
    margin: "0 0 12px 0",
    textTransform: "uppercase",
  },
  questionBlock: {
    padding: "10px",
    backgroundColor: "rgba(255,255,255,0.05)",
    borderRadius: "6px",
    marginBottom: "10px",
    border: "1px solid rgba(255,255,255,0.1)",
  },
  questionHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "10px",
  },
  questionNum: {
    fontWeight: "600",
    fontSize: "13px",
    color: "#60a5fa",
    minWidth: "40px",
  },
  questionFields: {
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gap: "10px",
  },
  removeButton: {
    background: "linear-gradient(135deg, #f87171, #ef4444)",
    padding: "6px 14px",
    borderRadius: "20px",
    border: "none",
    color: "#fff",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: "500",
  },
  removeQButton: {
    background: "linear-gradient(135deg, #fb923c, #f97316)",
    padding: "4px 10px",
    borderRadius: "16px",
    border: "none",
    color: "#fff",
    cursor: "pointer",
    fontSize: "11px",
    fontWeight: "500",
  },
  addQButton: {
    background: "linear-gradient(135deg, #34d399, #10b981)",
    padding: "8px 14px",
    borderRadius: "20px",
    border: "none",
    color: "#fff",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: "500",
    marginTop: "8px",
    width: "100%",
  },
  addButton: {
    background: "linear-gradient(135deg, #10b981, #059669)",
    padding: "10px 20px",
    borderRadius: "20px",
    border: "none",
    color: "#fff",
    cursor: "pointer",
    marginBottom: "15px",
    fontWeight: "500",
  },
  submitButton: {
    background: "linear-gradient(135deg, #f59e0b, #d97706)",
    padding: "12px 30px",
    borderRadius: "30px",
    border: "none",
    color: "#fff",
    cursor: "pointer",
    fontSize: "16px",
    fontWeight: "500",
  },
};

export default App;
