import { useMemo, useState } from "react";
import {
  AlertTriangle, BarChart3, CheckCircle2, ChevronRight,
  FileText, LayoutDashboard, MessageSquare, PenTool, Search,
  Settings, ShieldCheck, UploadCloud
} from "lucide-react";
import type { Analysis, Clause, DocumentInfo, RiskLevel } from "./types";
import { uploadDocument } from "./api";

const demoAnalysis: Analysis = {
  overallScore: 74,
  risks: [
    { category: "Privacy", level: "HIGH", score: 85 },
    { category: "Financial", level: "HIGH", score: 80 },
    { category: "Cancellation", level: "MEDIUM", score: 60 },
    { category: "Data", level: "MEDIUM", score: 55 },
    { category: "Arbitration", level: "LOW", score: 25 }
  ],
  clauses: [
    {
      id: "c1", section: "Section 7.2", title: "Data Sharing", category: "Privacy",
      riskLevel: "HIGH",
      text: "The company may disclose information to service providers and other third parties.",
      explanation: "Certain information may be shared with third-party organizations involved in providing the service."
    },
    {
      id: "c2", section: "Section 8.1", title: "Automatic Renewal", category: "Financial",
      riskLevel: "HIGH",
      text: "Your subscription shall automatically renew at the end of each billing period.",
      explanation: "Your subscription may continue automatically and you may be charged again unless you cancel according to the stated procedure."
    },
    {
      id: "c3", section: "Section 9.4", title: "Data Retention", category: "Data",
      riskLevel: "MEDIUM",
      text: "Certain information may be retained after termination of your account.",
      explanation: "Deleting your account may not immediately result in deletion of all information associated with it."
    }
  ]
};

type Page = "dashboard" | "documents" | "analysis" | "ask" | "clause" | "settings";

const nav = [
  ["dashboard", "Dashboard", LayoutDashboard],
  ["documents", "Documents", FileText],
  ["analysis", "Analysis", BarChart3],
  ["ask", "Ask Agreement", MessageSquare],
  ["clause", "Clause Assistant", PenTool],
  ["settings", "Settings", Settings]
] as const;

function RiskBadge({ level }: { level: RiskLevel }) {
  return <span className={`badge ${level.toLowerCase()}`}>{level}</span>;
}

function Sidebar({ page, setPage }: { page: Page; setPage: (p: Page) => void }) {
  return <aside className="sidebar">
    <div className="brand"><span>⚖</span><strong>ClauseIQ</strong></div>
    <div className="nav">
      {nav.map(([id, label, Icon]) => (
        <button className={page === id ? "nav-btn active" : "nav-btn"} onClick={() => setPage(id)} key={id}>
          <Icon size={19}/>{label}
        </button>
      ))}
    </div>
    <div className="sidebar-bottom">
      <span>Agreement Understanding Assistant</span>
      <small>Milestone 1 • v0.1</small>
    </div>
  </aside>;
}

function UploadBox({ onUploaded }: { onUploaded: (d: DocumentInfo) => void }) {
  const [loading, setLoading] = useState(false);
  const [drag, setDrag] = useState(false);

  async function handle(file?: File) {
    if (!file) return;
    const ext = file.name.toLowerCase().split(".").pop();
    if (!["pdf", "docx", "txt"].includes(ext || "")) {
      alert("Please select a PDF, DOCX or TXT file.");
      return;
    }
    setLoading(true);
    try {
      try {
        const result = await uploadDocument(file);
        onUploaded(result);
      } catch {
        onUploaded({
          id: crypto.randomUUID(),
          name: file.name,
          type: ext || "file",
          size: file.size,
          uploadedAt: new Date().toISOString(),
          status: "demo"
        });
      }
    } finally {
      setLoading(false);
    }
  }

  return <label
    className={`upload ${drag ? "drag" : ""}`}
    onDragOver={e => { e.preventDefault(); setDrag(true); }}
    onDragLeave={() => setDrag(false)}
    onDrop={e => { e.preventDefault(); setDrag(false); void handle(e.dataTransfer.files[0]); }}
  >
    <input type="file" accept=".pdf,.docx,.txt" onChange={e => void handle(e.target.files?.[0])}/>
    <UploadCloud size={42}/>
    <strong>{loading ? "Processing..." : "Drop your agreement here"}</strong>
    <span>or click to browse</span>
    <small>PDF • DOCX • TXT</small>
  </label>;
}

function Dashboard({ onUploaded }: { onUploaded: (d: DocumentInfo) => void }) {
  return <div>
    <div className="hero">
      <div>
        <div className="eyebrow">AGREEMENT UNDERSTANDING</div>
        <h2>Don't just accept.<br/>Understand what you're agreeing to.</h2>
        <p>Upload an agreement to identify important clauses and areas that deserve your attention.</p>
      </div>
      <div className="hero-mark">⚖</div>
    </div>
    <div className="two-col">
      <section className="card">
        <div className="section-title"><div><h3>Analyze a new agreement</h3><p>Start with a PDF, DOCX or TXT document.</p></div></div>
        <UploadBox onUploaded={onUploaded}/>
      </section>
      <section className="card">
        <h3>What ClauseIQ analyzes</h3>
        <div className="feature-list">
          {["Privacy & data sharing","Financial obligations","Cancellation & renewal","Account termination","Intellectual property","Contractual provisions"].map(x =>
            <div key={x}><CheckCircle2 size={17}/><span>{x}</span></div>
          )}
        </div>
        <div className="notice"><ShieldCheck size={18}/><span>Risk indicators are for awareness and informational purposes, not legal determinations.</span></div>
      </section>
    </div>
  </div>;
}

function AnalysisPage({ analysis, document }: { analysis: Analysis; document?: DocumentInfo }) {
  const [selected, setSelected] = useState<Clause>(analysis.clauses[0]);
  return <div>
    <div className="page-heading">
      <div><div className="eyebrow">ANALYSIS REPORT</div><h2>{document?.name || "Agreement Analysis"}</h2><p>AI-assisted clause and attention analysis.</p></div>
      <div className="score"><small>ATTENTION SCORE</small><strong>{analysis.overallScore}</strong><span>/ 100</span></div>
    </div>
    <div className="risk-grid">
      {analysis.risks.map(r => <div className="risk-card" key={r.category}>
        <div className="risk-top"><span>{r.category}</span><AlertTriangle size={18}/></div>
        <RiskBadge level={r.level}/><div className="bar"><i style={{width: `${r.score}%`}}/></div><small>{r.score}/100 attention</small>
      </div>)}
    </div>
    <div className="viewer">
      <div className="clause-list">
        <div className="panel-head"><strong>Important Clauses</strong><span>{analysis.clauses.length}</span></div>
        {analysis.clauses.map(c => <button key={c.id} className={selected.id === c.id ? "clause-row selected" : "clause-row"} onClick={() => setSelected(c)}>
          <div><small>{c.section}</small><strong>{c.title}</strong><span>{c.category}</span></div><RiskBadge level={c.riskLevel}/><ChevronRight size={16}/>
        </button>)}
      </div>
      <div className="clause-detail">
        <div className="detail-head"><div><small>{selected.section}</small><h3>{selected.title}</h3></div><RiskBadge level={selected.riskLevel}/></div>
        <div className="source-box"><label>ORIGINAL CLAUSE</label><p>{selected.text}</p></div>
        <div className="explanation"><label>WHAT THIS MEANS</label><p>{selected.explanation}</p></div>
        <div className="why"><label>WHY IT MAY MATTER</label><p>This provision is highlighted because it may affect your obligations, permissions, costs, or rights. Review the surrounding agreement language before making a decision.</p></div>
      </div>
    </div>
  </div>;
}

function Placeholder({ title, text }: { title: string; text: string }) {
  return <div className="card placeholder"><div className="placeholder-icon"><MessageSquare size={25}/></div><h2>{title}</h2><p>{text}</p><span>Planned for Milestone 2 / 3</span></div>;
}

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [document, setDocument] = useState<DocumentInfo>();
  const analysis = useMemo(() => demoAnalysis, []);

  function uploaded(d: DocumentInfo) {
    setDocument(d);
    setPage("analysis");
  }

  return <div className="app">
    <Sidebar page={page} setPage={setPage}/>
    <main className="main">
      <header className="topbar"><div><span className="mobile-brand">ClauseIQ</span><small>AI-POWERED AGREEMENT ASSISTANT</small></div><div className="avatar">U</div></header>
      <div className="content">
        {page === "dashboard" && <Dashboard onUploaded={uploaded}/>}
        {page === "analysis" && <AnalysisPage analysis={analysis} document={document}/>}
        {page === "documents" && <Placeholder title="Documents" text="Uploaded agreements and analysis history will appear here."/>}
        {page === "ask" && <Placeholder title="Ask the Agreement" text="Grounded question answering with source clauses is part of Milestone 2."/>}
        {page === "clause" && <Placeholder title="Clause Assistant" text="AI-assisted clause drafting is planned for Milestone 3."/>}
        {page === "settings" && <Placeholder title="Settings" text="Application and privacy settings will be added as the desktop app matures."/>}
      </div>
    </main>
  </div>;
}