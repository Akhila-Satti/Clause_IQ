import type { User } from "./types";


const TOKEN_KEY = "clauseiq_token";
const USER_KEY = "clauseiq_user";


export function saveAuth(
  token: string,
  user: User
) {
  localStorage.setItem(
    TOKEN_KEY,
    token
  );

  localStorage.setItem(
    USER_KEY,
    JSON.stringify(user)
  );
}


export function getToken(): string | null {
  return localStorage.getItem(
    TOKEN_KEY
  );
}


export function getStoredUser(): User | null {
  const value =
    localStorage.getItem(USER_KEY);

  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}


export function clearAuth() {
  localStorage.removeItem(
    TOKEN_KEY
  );

  localStorage.removeItem(
    USER_KEY
  );
}