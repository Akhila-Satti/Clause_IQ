export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Clause {
  id: string;
  section: string;
  title: string;
  category: string;
  riskLevel: RiskLevel;
  text: string;
  explanation: string;
}

export interface Risk {
  category: string;
  level: RiskLevel;
  score: number;
}

export interface Analysis {
  overallScore: number;
  risks: Risk[];
  clauses: Clause[];
}

export interface DocumentInfo {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: string;
  status: string;
}