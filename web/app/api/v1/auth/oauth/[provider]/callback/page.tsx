"use client";

import React, { useEffect, useState, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, AlertCircle } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

interface PageProps {
  params: Promise<{ provider: string }>;
}

export default function OAuthCallbackPage({ params }: PageProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { checkUser } = useAuth();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const started = useRef(false);

  const code = searchParams.get("code");
  const state = searchParams.get("state");

  const resolvedParams = React.use(params);
  const provider = resolvedParams.provider;

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    async function exchangeCode() {
      if (!code || !state) {
        setErrorMsg("Missing authorization code or state from provider.");
        return;
      }

      const verifier = sessionStorage.getItem(`oauth_verifier_${provider}`);
      if (!verifier) {
        setErrorMsg("PKCE code verifier not found. Please try logging in again.");
        return;
      }

      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/auth/oauth/${provider}/callback?code=${code}&state=${state}&code_verifier=${verifier}`,
          {
            method: "GET",
            credentials: "include",
          }
        );

        if (!response.ok) {
          const errData = await response.json().catch(() => ({ detail: "Token exchange failed" }));
          throw new Error(errData.detail || "Authentication failed during token exchange.");
        }

        // Clean up verifier
        sessionStorage.removeItem(`oauth_verifier_${provider}`);

        // Sync auth context state
        await checkUser();

        // Redirect to dashboard/chat
        router.push("/chat");
      } catch (err: any) {
        console.error("Callback Error:", err);
        setErrorMsg(err.message || "Failed to complete social login.");
      }
    }

    exchangeCode();
  }, [code, state, provider, router, checkUser]);

  if (errorMsg) {
    return (
      <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
        {/* Glow Background */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,oklch(0.05_0.02_260)_95%)]" />
          <div className="absolute -top-40 left-1/2 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-gradient-to-br from-rose-500/10 via-violet/5 to-transparent blur-3xl" />
        </div>

        <div className="glass-strong relative z-10 w-full max-w-md rounded-3xl p-8 border-rose-500/20 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-500/15 text-rose-500 mb-4">
            <AlertCircle className="h-6 w-6" />
          </div>
          <h2 className="font-display text-xl font-bold text-foreground">Authentication Failed</h2>
          <p className="mt-2 text-sm text-muted-foreground">{errorMsg}</p>
          <button
            onClick={() => router.push("/login")}
            className="mt-6 w-full rounded-2xl bg-white/5 border border-white/10 py-3 text-sm font-semibold hover:bg-white/10 active:scale-95 transition-all"
          >
            Back to Login
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden">
      {/* Dynamic Aurora Glow */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,oklch(0.05_0.02_260)_95%)]" />
        <div className="absolute -top-40 left-1/2 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-gradient-to-br from-cyan/20 via-violet/10 to-transparent blur-3xl" />
      </div>

      <div className="relative z-10 flex flex-col items-center gap-4 text-center">
        <div className="relative flex h-16 w-16 items-center justify-center">
          <Loader2 className="absolute h-12 w-12 animate-spin text-cyan" />
          <div className="h-6 w-6 rounded-full bg-gradient-to-br from-cyan to-violet opacity-80 blur-[2px]" />
        </div>
        <h2 className="font-display text-lg font-semibold tracking-wide text-foreground">
          Verifying credentials
        </h2>
        <p className="text-xs text-muted-foreground">
          Completing authentication with {provider}...
        </p>
      </div>
    </main>
  );
}
