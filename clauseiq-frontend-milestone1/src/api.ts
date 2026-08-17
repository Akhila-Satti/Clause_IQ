const API_URL = "http://127.0.0.1:8000";

export async function uploadDocument(file: File) {
  const body = new FormData();
  body.append("file", file);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    body
  });

  if (!response.ok) throw new Error("Upload failed");
  return response.json();
}

export async function getAnalysis(documentId: string) {
  const response = await fetch(`${API_URL}/documents/${documentId}/analysis`);
  if (!response.ok) throw new Error("Analysis request failed");
  return response.json();
}