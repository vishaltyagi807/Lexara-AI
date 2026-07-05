"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export interface User {
  id: string;
  email: string;
  full_name: string;
  tier: string;
  is_verified: boolean;
  avatar_url: string | null;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  loginOAuth: (provider: string) => Promise<void>;
  checkUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE = "http://localhost:8000/api/v1";

// PKCE utility functions
function dec2hex(dec: number): string {
  return dec.toString(16).padStart(2, "0");
}

function generateCodeVerifier(): string {
  const array = new Uint8Array(43);
  window.crypto.getRandomValues(array);
  return Array.from(array, dec2hex).join("").slice(0, 128);
}

async function sha256(plain: string): Promise<ArrayBuffer> {
  const encoder = new TextEncoder();
  const data = encoder.encode(plain);
  return window.crypto.subtle.digest("SHA-256", data);
}

function base64urlencode(a: ArrayBuffer): string {
  let str = "";
  const bytes = new Uint8Array(a);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    str += String.fromCharCode(bytes[i]);
  }
  return btoa(str)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

async function generateCodeChallenge(verifier: string): Promise<string> {
  const hashed = await sha256(verifier);
  return base64urlencode(hashed);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Helper fetcher with auto-refresh mechanism
  const apiFetch = async (path: string, options: RequestInit = {}): Promise<Response> => {
    const url = `${API_BASE}${path}`;
    const headers = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    const config: RequestInit = {
      credentials: "include", // Ensure cookies are sent
      ...options,
      headers,
    };

    let response = await fetch(url, config);

    // If 401 Unauthorized, try to refresh tokens
    if (response.status === 401 && !path.includes("/auth/login") && !path.includes("/auth/refresh")) {
      try {
        const refreshResponse = await fetch(`${API_BASE}/auth/refresh`, {
          method: "POST",
          credentials: "include",
        });

        if (refreshResponse.ok) {
          // Retry the original request
          response = await fetch(url, config);
        } else {
          // Refresh failed, clear user state
          setUser(null);
        }
      } catch (err) {
        setUser(null);
      }
    }

    return response;
  };

  const checkUser = async () => {
    try {
      const res = await apiFetch("/auth/me");
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Initial user check on mount
  useEffect(() => {
    checkUser();
  }, []);

  const login = async (email: string, password: string) => {
    const res = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(errData.detail || "Invalid email or password");
    }

    const data = await res.json();
    setUser(data);
    router.push("/chat");
  };

  const signup = async (email: string, password: string, fullName: string) => {
    const res = await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: "Registration failed" }));
      throw new Error(errData.detail || "Failed to create account");
    }

    // Auto login after signup
    await login(email, password);
  };

  const logout = async () => {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } catch {
      // Ignore network errors on logout
    } finally {
      setUser(null);
      router.push("/login");
    }
  };

  const loginOAuth = async (provider: string) => {
    try {
      const verifier = generateCodeVerifier();
      const challenge = await generateCodeChallenge(verifier);

      // Store verifier for token exchange on callback
      sessionStorage.setItem(`oauth_verifier_${provider}`, verifier);

      const res = await apiFetch(`/auth/oauth/${provider}/authorize`, {
        method: "POST",
        body: JSON.stringify({
          provider,
          code_challenge: challenge,
          code_challenge_method: "S256",
          client_type: "web",
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: "OAuth authorization failed" }));
        throw new Error(errData.detail || "OAuth initialization failed");
      }

      const { authorization_url } = await res.json();
      window.location.href = authorization_url;
    } catch (err: any) {
      console.error("OAuth Init Error:", err);
      throw err;
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, loginOAuth, checkUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
