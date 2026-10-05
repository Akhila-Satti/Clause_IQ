export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Clause {
  id: string;
  section: string;
  title: string;
  category: string;
  riskLevel: RiskLevel;
  text: string;
  explanation: string;
  summary: string;
  risks: string[];
  obligations: string[];
}

export interface Risk {
  category: string;
  level: RiskLevel;
  score: number;
}

export interface Analysis {
  summary: string;
  overallScore: number;
  risks: Risk[];
  recommendations: string[];
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

export interface AskResponse {
  question: string;
  answer: string;
}

export interface SourceClause {
  clause_id: string;
  section: string;
  title: string;
  category: string;
  text: string;
}

export interface AskQuestionResponse {
  question: string;
  answer: string;
  sources: SourceClause[];
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  age?: number | null;
  income?: number | null;
  occupation?: string | null;
  location?: string | null;
  personalization_consent: boolean;
}

export interface AuthResponse {
  message: string;
  access_token: string;
  user: User;
}