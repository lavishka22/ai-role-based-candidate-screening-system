import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { api } from "./api/client";
import "./style.css";

function App() {
  const [role, setRole] = useState("AI/ML Engineer");
  const [name, setName] = useState("");
  const [file, setFile] = useState(null);
  const [session, setSession] = useState(null);
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function startInterview(e) {
    e.preventDefault();
    setError("");
    if (!file) return setError("Please upload a PDF or TXT resume.");
    const form = new FormData();
    form.append("role", role);
    form.append("candidate_name", name);
    form.append("resume", file);
    setLoading(true);
    try {
      const res = await api.post("/api/interview/start", form);
      setSession(res.data);
      setQuestion(res.data.first_question);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally { setLoading(false); }
  }

  async function submitAnswer() {
    if (!answer.trim()) return setError("Please type your answer first.");
    setLoading(true); setError("");
    try {
      const res = await api.post(`/api/interview/${session.session_id}/answer`, { question_id: question.id, answer });
      setAnswer("");
      if (res.data.next_question) setQuestion(res.data.next_question);
      else await loadSummary();
    } catch (err) { setError(err.response?.data?.detail || "Could not save answer."); }
    finally { setLoading(false); }
  }

  async function loadSummary() {
    const res = await api.get(`/api/interview/${session.session_id}/summary`);
    setSummary(res.data);
  }

  if (summary) return <main className="container"><h1>Interview Summary</h1><p>{summary.summary}</p><h2>Extracted Profile</h2><pre>{JSON.stringify(summary.extracted_profile, null, 2)}</pre><h2>Questions & Answers</h2>{summary.qa.map((x, i) => <div className="card" key={x.id}><b>Q{i+1}. {x.question}</b><p><b>Answer:</b> {x.answer || "Not answered"}</p><small>{x.topic} · {x.difficulty}</small></div>)}</main>;

  return <main className="container"><h1>AI-Powered Candidate Screening</h1><p className="muted">Resume-aware RAG interview system for role-based technical screening.</p>{error && <p className="error">{error}</p>}{!session ? <form onSubmit={startInterview} className="card"><label>Candidate Name</label><input value={name} onChange={e=>setName(e.target.value)} placeholder="Lavishka Bhardwaj"/><label>Target Role</label><select value={role} onChange={e=>setRole(e.target.value)}><option>AI/ML Engineer</option><option>Backend Engineer</option></select><label>Resume PDF/TXT</label><input type="file" accept=".pdf,.txt" onChange={e=>setFile(e.target.files[0])}/><button disabled={loading}>{loading ? "Starting..." : "Start Interview"}</button></form> : <section className="card"><h2>Question</h2><p>{question?.question}</p><small>Topic: {question?.topic || "mixed"} · Difficulty: {question?.difficulty || "medium"}</small><textarea rows="7" value={answer} onChange={e=>setAnswer(e.target.value)} placeholder="Type candidate answer here..."/><button onClick={submitAnswer} disabled={loading}>{loading ? "Saving..." : "Submit Answer"}</button><button className="secondary" onClick={loadSummary}>Finish & View Summary</button></section>}</main>;
}

createRoot(document.getElementById("root")).render(<App />);
