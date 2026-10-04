import { useEffect, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  FileText,
  LayoutDashboard,
  MessageSquare,
  PenTool,
  Search,
  Settings,
  ShieldCheck,
  UploadCloud,
} from "lucide-react";
import type { Analysis, Clause, DocumentInfo, RiskLevel } from "./types";
import { uploadDocument, getAnalysis, askAgreement, askAboutClause , getDocuments, generateAgreement,} from "./api";

type Page =
  | "dashboard"
  | "documents"
  | "analysis"
  | "ask"
  | "clause"
  | "settings";

const nav = [
  ["dashboard", "Dashboard", LayoutDashboard],
  ["documents", "Documents", FileText],
  ["analysis", "Analysis", BarChart3],
  ["ask", "Ask Agreement", MessageSquare],
  ["clause", "Clause Assistant", PenTool],
  ["settings", "Settings", Settings],
] as const;

function RiskBadge({ level }: { level: RiskLevel }) {
  return <span className={`badge ${level.toLowerCase()}`}>{level}</span>;
}

function Sidebar({
  page,
  setPage,
}: {
  page: Page;
  setPage: (p: Page) => void;
}) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span>⚖</span>
        <strong>ClauseIQ</strong>
      </div>
      <div className="nav">
        {nav.map(([id, label, Icon]) => (
          <button
            className={page === id ? "nav-btn active" : "nav-btn"}
            onClick={() => setPage(id)}
            key={id}
          >
            <Icon size={19} />
            {label}
          </button>
        ))}
      </div>
      <div className="sidebar-bottom">
        <span>Agreement Understanding Assistant</span>
        <small>Milestone 1 • v0.1</small>
      </div>
    </aside>
  );
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
      const result = await uploadDocument(file);
      onUploaded(result);
    } catch (error) {
      console.error(error);
      alert("Failed to upload and analyze the document.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <label
      className={`upload ${drag ? "drag" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        void handle(e.dataTransfer.files[0]);
      }}
    >
      <input
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={(e) => void handle(e.target.files?.[0])}
      />
      <UploadCloud size={42} />
      <strong>{loading ? "Processing..." : "Drop your agreement here"}</strong>
      <span>or click to browse</span>
      <small>PDF • DOCX • TXT</small>
    </label>
  );
}

function Dashboard({ onUploaded }: { onUploaded: (d: DocumentInfo) => void }) {
  return (
    <div>
      <div className="hero">
        <div>
          <div className="eyebrow">AGREEMENT UNDERSTANDING</div>
          <h2>
            Don't just accept.
            <br />
            Understand what you're agreeing to.
          </h2>
          <p>
            Upload an agreement to identify important clauses and areas that
            deserve your attention.
          </p>
        </div>
        <div className="hero-mark">⚖</div>
      </div>
      <div className="two-col">
        <section className="card">
          <div className="section-title">
            <div>
              <h3>Analyze a new agreement</h3>
              <p>Start with a PDF, DOCX or TXT document.</p>
            </div>
          </div>
          <UploadBox onUploaded={onUploaded} />
        </section>
        <section className="card">
          <h3>What ClauseIQ analyzes</h3>
          <div className="feature-list">
            {[
              "Privacy & data sharing",
              "Financial obligations",
              "Cancellation & renewal",
              "Account termination",
              "Intellectual property",
              "Contractual provisions",
            ].map((x) => (
              <div key={x}>
                <CheckCircle2 size={17} />
                <span>{x}</span>
              </div>
            ))}
          </div>
          <div className="notice">
            <ShieldCheck size={18} />
            <span>
              Risk indicators are for awareness and informational purposes, not
              legal determinations.
            </span>
          </div>
        </section>
      </div>
    </div>
  );
}

function AnalysisPage({ 
  analysis, 
  document, 
  initialClauseId,
}: { 
  analysis: Analysis; 
  document?: DocumentInfo;
  initialClauseId?: string;
}) {
 const [selected, setSelected] = useState<Clause | undefined>(
  analysis.clauses.find(
    (clause) => clause.id === initialClauseId,
  ) || analysis.clauses[0],
);
useEffect(() => {
  if (!initialClauseId) {
    return;
  }

  const clause = analysis.clauses.find(
    (item) => item.id === initialClauseId,
  );

  if (clause) {
    setSelected(clause);
  }
}, [initialClauseId, analysis.clauses]);

  const [question, setQuestion] = useState("");
const [clauseAnswer, setClauseAnswer] = useState<string>("");
const [askingClause, setAskingClause] = useState(false);

async function handleAskClause() {
  if (!selected || !document?.id || !question.trim()) {
    return;
  }

  setAskingClause(true);
  setClauseAnswer("");

  try {
    const result = await askAboutClause(
      document.id,
      selected.id,
      question.trim(),
    );

    setClauseAnswer(result.answer);
  } catch (error) {
    console.error(error);
    setClauseAnswer(
      "Sorry, I could not analyze this clause right now.",
    );
  } finally {
    setAskingClause(false);
  }
}

  if (!selected) {
    return (
      <div className="card placeholder">
        <h2>No clauses found</h2>
        <p>
          The analysis completed, but no clauses were returned for this
          document.
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="page-heading">
        <div>
          <div className="eyebrow">ANALYSIS REPORT</div>

          <h2>{document?.name || "Agreement Analysis"}</h2>

          <p>AI-assisted clause and attention analysis.</p>
        </div>

        <div className="score">
          <small>ATTENTION SCORE</small>
          <strong>{analysis.overallScore}</strong>
          <span>/ 100</span>
        </div>
      </div>

      {/* Summary */}
      <div className="card" style={{ marginBottom: "20px" }}>
        <div className="section-title">
          <div>
            <h3>Agreement Summary</h3>
          </div>
        </div>

        <p>{analysis.summary}</p>
      </div>

      {/* Risk Categories */}
      <div className="risk-grid">
        {analysis.risks.map((risk) => (
          <div className="risk-card" key={risk.category}>
            <div className="risk-top">
              <span>{risk.category}</span>
              <AlertTriangle size={18} />
            </div>

            <RiskBadge level={risk.level} />

            <div className="bar">
              <i
                style={{
                  width: `${risk.score}%`,
                }}
              />
            </div>

            <small>{risk.score}/100 attention</small>
          </div>
        ))}
      </div>

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div className="card" style={{ marginBottom: "20px" }}>
          <div className="section-title">
            <div>
              <h3>Recommendations</h3>
              <p>Points worth reviewing before relying on the agreement.</p>
            </div>
          </div>

          <div className="feature-list">
            {analysis.recommendations.map((recommendation, index) => (
              <div key={index}>
                <CheckCircle2 size={17} />
                <span>{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clause Viewer */}
      <div className="viewer">
        {/* Clause List */}
        <div className="clause-list">
          <div className="panel-head">
            <strong>Important Clauses</strong>
            <span>{analysis.clauses.length}</span>
          </div>

          {analysis.clauses.map((clause) => (
            <button
              key={clause.id}
              className={
                selected.id === clause.id ? "clause-row selected" : "clause-row"
              }
              onClick={() => {
  setSelected(clause);
  setQuestion("");
  setClauseAnswer("");
}}
            >
              <div>
                <small>{clause.section}</small>

                <strong>{clause.title}</strong>

                <span>{clause.category}</span>
              </div>

              <RiskBadge level={clause.riskLevel} />

              <ChevronRight size={16} />
            </button>
          ))}
        </div>

        {/* Selected Clause */}
        <div className="clause-detail">
          <div className="detail-head">
            <div>
              <small>{selected.section}</small>

              <h3>{selected.title}</h3>
            </div>

            <RiskBadge level={selected.riskLevel} />
          </div>

          {/* Original Clause */}
          <div className="source-box">
            <label>ORIGINAL CLAUSE</label>

            <p>{selected.text}</p>
          </div>

          {/* Explanation */}
          <div className="explanation">
            <label>WHAT THIS MEANS</label>
            <p>{selected.explanation}</p>
          </div>

          <div className="explanation">
            <label>CLAUSE SUMMARY</label>
            <p>{selected.summary}</p>
          </div>

          <div className="clause-assistant">
  <label>ASK ABOUT THIS CLAUSE</label>

  <div className="clause-question">
    <input
      type="text"
      value={question}
      onChange={(e) => setQuestion(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          void handleAskClause();
        }
      }}
      placeholder="Ask something about this clause..."
      disabled={askingClause}
    />

    <button
      onClick={() => void handleAskClause()}
      disabled={askingClause || !question.trim()}
    >
      {askingClause ? "Asking..." : "Ask ClauseIQ"}
    </button>
  </div>

  {clauseAnswer && (
    <div className="clause-answer">
      <label>CLAUSEIQ ANSWER</label>
      <p>{clauseAnswer}</p>
    </div>
  )}
</div>

          {/* Risks */}
          {selected.risks.length > 0 && (
            <div className="why">
              <label>RISKS TO CONSIDER</label>

              <ul>
                {selected.risks.map((risk, index) => (
                  <li key={index}>{risk}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Obligations */}
          {selected.obligations.length > 0 && (
            <div className="why">
              <label>OBLIGATIONS</label>

              <ul>
                {selected.obligations.map((obligation, index) => (
                  <li key={index}>{obligation}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DocumentsPage({
  onOpenDocument,
}: {
  onOpenDocument: (document: DocumentInfo) => void;
}) {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadDocuments() {
    try {
      const result = await getDocuments();
      setDocuments(result);
    } catch (error) {
      console.error(error);
      alert("Failed to load documents.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
  void loadDocuments();
}, []);

  if (loading) {
    return (
      <div className="card placeholder">
        <div className="placeholder-icon">
          <FileText size={25} />
        </div>

        <h2>Loading documents...</h2>
        <p>Fetching your uploaded agreements.</p>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="card placeholder">
        <div className="placeholder-icon">
          <FileText size={25} />
        </div>

        <h2>No documents yet</h2>
        <p>Upload an agreement from the Dashboard to get started.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <div className="eyebrow">DOCUMENT LIBRARY</div>

          <h2>Your Documents</h2>

          <p>
            View previously uploaded agreements and their analyses.
          </p>
        </div>
      </div>

      <div className="documents-grid">
        {documents.map((doc) => (
          <div className="document-card" key={doc.id}>
            <div className="document-icon">
              <FileText size={24} />
            </div>

            <div className="document-info">
              <h3>{doc.name}</h3>

              <p>
                {doc.type.toUpperCase()} •{" "}
                {(doc.size / 1024).toFixed(1)} KB
              </p>

              <span className={`document-status ${doc.status}`}>
                {doc.status}
              </span>
            </div>

            <button
              className="document-open"
              onClick={() => onOpenDocument(doc)}
            >
              View Analysis
              <ChevronRight size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
function AskAgreementPage({
  document,
  onOpenSource,
}: {
  document?: DocumentInfo;
  onOpenSource: (clauseId: string) => void;
}) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<
    import("./types").SourceClause[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAsk() {
    if (!document) {
      setError("Please upload and analyze a document first.");
      return;
    }

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const result = await askAgreement(
        document.id,
        question.trim()
      );

      setAnswer(result.answer);
      setSources(result.sources);
    } catch (err) {
      console.error(err);
      setError("Could not answer the question.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <div className="eyebrow">ASK AGREEMENT</div>

          <h2>Ask questions about your agreement</h2>

          <p>
            ClauseIQ answers using the clauses retrieved from your
            uploaded document.
          </p>
        </div>
      </div>

      {!document && (
        <div className="card">
          <h3>No agreement selected</h3>
          <p>
            Upload an agreement from the Dashboard before asking
            questions.
          </p>
        </div>
      )}

      {document && (
        <div className="card">
          <div className="section-title">
            <div>
              <h3>{document.name}</h3>
              <p>Ask anything about this agreement.</p>
            </div>
          </div>

          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Example: Can this agreement renew automatically?"
            rows={4}
            style={{
              width: "100%",
              resize: "vertical",
              marginBottom: "12px",
            }}
          />

          <button
            className="nav-btn active"
            onClick={() => void handleAsk()}
            disabled={loading}
          >
            {loading ? "Thinking..." : "Ask Agreement"}
          </button>

          {error && (
            <div className="notice" style={{ marginTop: "16px" }}>
              <AlertTriangle size={18} />
              <span>{error}</span>
            </div>
          )}
        </div>
      )}

      {answer && (
        <div className="card" style={{ marginTop: "20px" }}>
          <div className="section-title">
            <div>
              <h3>Answer</h3>
              <p>Based on the retrieved agreement clauses.</p>
            </div>
          </div>

          <p>{answer}</p>
        </div>
      )}

      {sources.length > 0 && (
        <div className="card" style={{ marginTop: "20px" }}>
          <div className="section-title">
            <div>
              <h3>Sources from your agreement</h3>
              <p>
                These clauses were retrieved and provided to the AI
                for answering your question.
              </p>
            </div>
          </div>

          <div className="feature-list">
            {sources.map((source) => (
  <button
    key={source.clause_id}
    type="button"
    onClick={() => onOpenSource(source.clause_id)}
    style={{
      display: "block",
      width: "100%",
      textAlign: "left",
      padding: "14px",
      border: "none",
      cursor: "pointer",
      background: "transparent",
    }}
  >
    <strong>
      {source.section} — {source.title}
    </strong>

    <small
      style={{
        display: "block",
        margin: "6px 0",
      }}
    >
      {source.category}
    </small>

    <p>{source.text}</p>
  </button>
))}
          </div>
        </div>
      )}
    </div>
  );
}
function ClauseAssistantPage() {
  const [agreementType, setAgreementType] = useState("");
  const [parties, setParties] = useState("");
  const [purpose, setPurpose] = useState("");
  const [location, setLocation] = useState("");
  const [duration, setDuration] = useState("");
  const [financialTerms, setFinancialTerms] = useState("");
  const [additionalRequirements, setAdditionalRequirements] =
    useState("");

  const [agreement, setAgreement] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate() {
    if (!agreementType.trim()) {
      setError("Please select an agreement type.");
      return;
    }

    if (!parties.trim()) {
      setError("Please enter the parties.");
      return;
    }

    if (!purpose.trim()) {
      setError("Please describe the purpose of the agreement.");
      return;
    }

    setLoading(true);
    setError("");
    setAgreement("");

    try {
      const result = await generateAgreement({
        agreement_type: agreementType,
        parties,
        purpose,
        location,
        duration,
        financial_terms: financialTerms,
        additional_requirements: additionalRequirements,
      });

      setAgreement(result.agreement);
    } catch (err) {
      console.error(err);

      setError(
        "Could not generate the agreement. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleDownload() {
    if (!agreement) {
      return;
    }

    const blob = new Blob(
      [agreement],
      {
        type: "text/plain;charset=utf-8",
      }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download =
      `${agreementType || "ClauseIQ-Agreement"}`
        .replace(/\s+/g, "-")
        .toLowerCase() + ".txt";

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <div className="eyebrow">
            CLAUSE ASSISTANT
          </div>

          <h2>
            Draft a new agreement
          </h2>

          <p>
            Describe your requirements and ClauseIQ will
            generate an editable agreement draft.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="section-title">
          <div>
            <h3>Agreement Details</h3>

            <p>
              Provide the information you want included
              in the draft.
            </p>
          </div>
        </div>

        <div className="generator-form">

          <label>
            Agreement Type

            <select
              value={agreementType}
              onChange={(e) =>
                setAgreementType(e.target.value)
              }
            >
              <option value="">
                Select agreement type
              </option>

              <option value="Rental Agreement">
                Rental Agreement
              </option>

              <option value="Employment Agreement">
                Employment Agreement
              </option>

              <option value="Non-Disclosure Agreement">
                Non-Disclosure Agreement
              </option>

              <option value="Service Agreement">
                Service Agreement
              </option>

              <option value="Freelance Agreement">
                Freelance Agreement
              </option>

              <option value="Partnership Agreement">
                Partnership Agreement
              </option>

              <option value="Sale Agreement">
                Sale Agreement
              </option>

              <option value="Other">
                Other
              </option>
            </select>
          </label>

          <label>
            Parties

            <textarea
              value={parties}
              onChange={(e) =>
                setParties(e.target.value)
              }
              placeholder="Example: Landlord and Tenant"
              rows={3}
            />
          </label>

          <label>
            Purpose

            <textarea
              value={purpose}
              onChange={(e) =>
                setPurpose(e.target.value)
              }
              placeholder="Describe the purpose of the agreement..."
              rows={3}
            />
          </label>

          <label>
            Location / Jurisdiction

            <input
              type="text"
              value={location}
              onChange={(e) =>
                setLocation(e.target.value)
              }
              placeholder="Example: Chennai, Tamil Nadu"
            />
          </label>

          <label>
            Duration

            <input
              type="text"
              value={duration}
              onChange={(e) =>
                setDuration(e.target.value)
              }
              placeholder="Example: 11 months"
            />
          </label>

          <label>
            Financial Terms

            <textarea
              value={financialTerms}
              onChange={(e) =>
                setFinancialTerms(e.target.value)
              }
              placeholder="Example: Monthly rent ₹20,000 and security deposit ₹60,000"
              rows={3}
            />
          </label>

          <label>
            Additional Requirements

            <textarea
              value={additionalRequirements}
              onChange={(e) =>
                setAdditionalRequirements(
                  e.target.value
                )
              }
              placeholder="Add any other requirements..."
              rows={4}
            />
          </label>

          {error && (
            <div className="notice">
              <AlertTriangle size={18} />

              <span>{error}</span>
            </div>
          )}

          <button
            className="nav-btn active"
            onClick={() => void handleGenerate()}
            disabled={loading}
          >
            {loading
              ? "Generating..."
              : "Generate Agreement"}
          </button>
        </div>
      </div>

      {agreement && (
        <div
          className="card"
          style={{ marginTop: "20px" }}
        >
          <div className="section-title">
            <div>
              <h3>
                Generated Agreement
              </h3>

              <p>
                Review and edit the draft before using it.
              </p>
            </div>

            <button
              className="nav-btn active"
              onClick={handleDownload}
            >
              Save / Download
            </button>
          </div>

          <textarea
            value={agreement}
            onChange={(e) =>
              setAgreement(e.target.value)
            }
            rows={30}
            style={{
              width: "100%",
              resize: "vertical",
              fontFamily: "inherit",
              lineHeight: 1.6,
              padding: "16px",
              boxSizing: "border-box",
            }}
          />

          <div className="notice" style={{ marginTop: "16px" }}>
            <ShieldCheck size={18} />

            <span>
              This is an AI-generated draft for
              informational purposes. Review the content
              carefully before using it.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
function Placeholder({ title, text }: { title: string; text: string }) {
  return (
    <div className="card placeholder">
      <div className="placeholder-icon">
        <MessageSquare size={25} />
      </div>
      <h2>{title}</h2>
      <p>{text}</p>
      <span>Planned for Milestone 2 / 3</span>
    </div>
  );
}


export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [document, setDocument] = useState<DocumentInfo>();
  const [analysis, setAnalysis] = useState<Analysis>();
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [selectedClauseId, setSelectedClauseId] = useState<string>();
  async function uploaded(d: DocumentInfo) {
  setSelectedClauseId(undefined);
  setDocument(d);
  setLoadingAnalysis(true);
  setPage("analysis");

    try {
      const result = await getAnalysis(d.id);
      setAnalysis(result);
    } catch (error) {
      console.error(error);
      alert("Document uploaded, but analysis could not be loaded.");
    } finally {
      setLoadingAnalysis(false);
    }
  }

  return (
    <div className="app">
      <Sidebar page={page} setPage={setPage} />
      <main className="main">
        <header className="topbar">
          <div>
            <span className="mobile-brand">ClauseIQ</span>
            <small>AI-POWERED AGREEMENT ASSISTANT</small>
          </div>
          <div className="avatar">U</div>
        </header>
        <div className="content">
          {page === "dashboard" && <Dashboard onUploaded={uploaded} />}
          {page === "analysis" &&
            (loadingAnalysis ? (
              <div className="card placeholder">
                <div className="placeholder-icon">
                  <FileText size={25} />
                </div>

                <h2>Analyzing agreement...</h2>

                <p>
                  ClauseIQ is extracting clauses and identifying potential
                  risks.
                </p>
              </div>
            ) : analysis ? (
              <AnalysisPage
  analysis={analysis}
  document={document}
  initialClauseId={selectedClauseId}
/>
            ) : (
              <div className="card placeholder">
                <h2>No analysis available</h2>
                <p>Upload an agreement to begin analysis.</p>
              </div>
            ))}
          {page === "documents" && (
  <DocumentsPage
    onOpenDocument={async (doc) => {
  setSelectedClauseId(undefined);
  setDocument(doc);
  setLoadingAnalysis(true);
  setPage("analysis");

      try {
        const result = await getAnalysis(doc.id);
        setAnalysis(result);
      } catch (error) {
        console.error(error);
        alert("Could not load document analysis.");
      } finally {
        setLoadingAnalysis(false);
      }
    }}
  />
)}
          {page === "ask" && (
  <AskAgreementPage
    document={document}
    onOpenSource={(clauseId) => {
      setSelectedClauseId(clauseId);
      setPage("analysis");
    }}
  />
)}
          {page === "clause" && (
  <ClauseAssistantPage />
)}
          {page === "settings" && (
            <Placeholder
              title="Settings"
              text="Application and privacy settings will be added as the desktop app matures."
            />
          )}
        </div>
      </main>
    </div>
  );
}
