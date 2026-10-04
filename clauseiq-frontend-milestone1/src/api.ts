import type {
  Analysis,
  DocumentInfo,
  AskResponse,
  AskQuestionResponse,
} from "./types";

const API_URL = "http://127.0.0.1:8000";

export async function uploadDocument(file: File): Promise<DocumentInfo> {
  const body = new FormData();
  body.append("file", file);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    body,
  });

  if (!response.ok) {
    throw new Error("Upload failed");
  }

  return response.json();
}

export async function getAnalysis(
  documentId: string
): Promise<Analysis> {
  const response = await fetch(
    `${API_URL}/documents/${documentId}/analysis`
  );

  if (!response.ok) {
    throw new Error("Analysis request failed");
  }

  return response.json();
}

export async function getDocuments(): Promise<DocumentInfo[]> {
  const response = await fetch(`${API_URL}/documents`);

  if (!response.ok) {
    throw new Error("Failed to load documents");
  }

  return response.json();
}



export interface ClauseQuestionResponse {
  answer: string;
  clause_id: string;
  section: string;
  title: string;
}

export async function askAboutClause(
  documentId: string,
  clauseId: string,
  question: string
): Promise<ClauseQuestionResponse> {
  const response = await fetch(
    `${API_URL}/documents/${documentId}/clauses/${clauseId}/ask`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
      }),
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Clause question failed");
  }

  return response.json();
}

export async function askAgreement(
  documentId: string,
  question: string
): Promise<AskQuestionResponse> {
  const response = await fetch(
    `${API_URL}/documents/${documentId}/ask`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
      }),
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Question request failed");
  }

  return response.json();
}

export interface AgreementGenerationRequest {
  agreement_type: string;
  parties: string;
  purpose: string;
  location: string;
  duration: string;
  financial_terms: string;
  additional_requirements: string;
}

export interface AgreementGenerationResponse {
  agreement_type: string;
  agreement: string;
}

export async function generateAgreement(
  request: AgreementGenerationRequest
): Promise<AgreementGenerationResponse> {
  const response = await fetch(
    `${API_URL}/agreements/generate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    }
  );

  if (!response.ok) {
    const error = await response.text();

    throw new Error(
      error || "Agreement generation failed"
    );
  }

  return response.json();
}