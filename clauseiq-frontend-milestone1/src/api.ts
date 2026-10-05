import type {
  Analysis,
  DocumentInfo,
  AskResponse,
  AskQuestionResponse,
  User,
  AuthResponse,
} from "./types";

import { getToken, clearAuth } from "./auth";

const API_URL = "http://127.0.0.1:8000";

/*
 * Adds the JWT Authorization header to protected requests.
 */
function authHeaders(
  headers: Record<string, string> = {}
): Record<string, string> {
  const token = getToken();

  if (!token) {
    return headers;
  }

  return {
    ...headers,
    Authorization: `Bearer ${token}`,
  };
}

/*
 * Handles expired/invalid authentication.
 */
function handleUnauthorized(response: Response) {
  if (response.status === 401) {
    clearAuth();
  }
}

export async function uploadDocument(file: File): Promise<DocumentInfo> {
  const body = new FormData();
  body.append("file", file);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    headers: authHeaders(),
    body,
  });

  if (!response.ok) {
    handleUnauthorized(response);

    const error = await response.text();
    throw new Error(error || "Upload failed");
  }

  return response.json();
}

export async function getAnalysis(
  documentId: string
): Promise<Analysis> {
  const response = await fetch(
    `${API_URL}/documents/${documentId}/analysis`,
    {
      headers: authHeaders(),
    }
  );

  if (!response.ok) {
    handleUnauthorized(response);

    const error = await response.text();
    throw new Error(error || "Analysis request failed");
  }

  return response.json();
}

export async function getDocuments(): Promise<DocumentInfo[]> {
  const response = await fetch(`${API_URL}/documents`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    handleUnauthorized(response);

    const error = await response.text();
    throw new Error(error || "Failed to load documents");
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
      headers: authHeaders({
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({
        question,
      }),
    }
  );

  if (!response.ok) {
    handleUnauthorized(response);

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
      headers: authHeaders({
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({
        question,
      }),
    }
  );

  if (!response.ok) {
    handleUnauthorized(response);

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
      headers: authHeaders({
        "Content-Type": "application/json",
      }),
      body: JSON.stringify(request),
    }
  );

  if (!response.ok) {
    handleUnauthorized(response);

    const error = await response.text();

    throw new Error(
      error || "Agreement generation failed"
    );
  }

  return response.json();
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name: string;
  age?: number | null;
  income?: number | null;
  occupation?: string | null;
  location?: string | null;
  personalization_consent: boolean;
}

export async function signup(
  request: SignupRequest
): Promise<AuthResponse> {
  const response = await fetch(
    `${API_URL}/auth/signup`,
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
      error || "Signup failed"
    );
  }

  return response.json();
}

export async function login(
  email: string,
  password: string
): Promise<AuthResponse> {
  const response = await fetch(
    `${API_URL}/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    }
  );

  if (!response.ok) {
    const error = await response.text();

    throw new Error(
      error || "Login failed"
    );
  }

  return response.json();
}

export async function getCurrentUser(
  token: string
): Promise<User> {
  const response = await fetch(
    `${API_URL}/auth/me`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    handleUnauthorized(response);

    throw new Error(
      "Authentication expired"
    );
  }

  return response.json();
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: import("./types").User;
}

export async function loginUser(
  request: LoginRequest
): Promise<LoginResponse> {
  const response = await fetch(
    `${API_URL}/auth/login`,
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
      error || "Login failed"
    );
  }

  return response.json();
}

export interface SignupResponse {
  access_token: string;
  token_type: string;
  user: import("./types").User;
}

export async function signupUser(
  request: SignupRequest
): Promise<SignupResponse> {
  const response = await fetch(
    `${API_URL}/auth/signup`,
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
      error || "Signup failed"
    );
  }

  return response.json();
}