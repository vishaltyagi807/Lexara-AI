"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Lock, Loader2, ArrowRight, AlertTriangle, Eye, EyeOff } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const { login, loginOAuth } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") || "/chat";
  const errorParam = searchParams.get("error");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(errorParam ? decodeURIComponent(errorParam) : null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);

    try {
      await login(email, password);
      router.push(redirect);
    } catch (err: any) {
      setFormError(err.message || "Something went wrong. Please try again.");
      setSubmitting(false);
    }
  };

  const handleOAuthLogin = async (provider: string) => {
    setFormError(null);
    try {
      await loginOAuth(provider);
    } catch (err: any) {
      setFormError(err.message || `Failed to initiate ${provider} login.`);
    }
  };

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-12">
      {/* Dynamic Aurora Glow */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,oklch(0.05_0.02_260)_95%)]" />
        <div className="absolute -top-40 left-1/2 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-gradient-to-br from-cyan/30 via-violet/20 to-transparent blur-3xl" />
        <div className="absolute inset-0 bg-grid opacity-30 [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_75%)]" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="glass-strong relative z-10 w-full max-w-md overflow-hidden rounded-3xl p-8 md:p-10"
      >
        {/* Glow border effect */}
        <div className="absolute -inset-px rounded-3xl bg-gradient-to-br from-cyan/20 to-violet/20 opacity-40 blur-sm pointer-events-none" />

        <div className="relative">
          {/* Header */}
          <div className="flex flex-col items-center text-center">
            <Link href="/" className="group flex items-center gap-2 mb-6">
              <span className="font-display text-2xl font-bold tracking-wider text-gradient">
                LEXARA
              </span>
            </Link>
            <h1 className="font-display text-2xl font-bold tracking-tight text-foreground md:text-3xl">
              Welcome back
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Sign in to your LexaraAI account
            </p>
          </div>

          {/* Errors */}
          <AnimatePresence>
            {formError && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6 overflow-hidden"
              >
                <div className="glass flex items-start gap-3 rounded-2xl border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-200">
                  <AlertTriangle className="h-5 w-5 shrink-0 text-rose-400" />
                  <div>
                    <span className="font-semibold">Authentication Error</span>
                    <p className="mt-1 text-xs opacity-90">{formError}</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Form */}
          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label htmlFor="email" className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Email Address
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-4 text-muted-foreground">
                  <Mail className="h-4 w-4" />
                </span>
                <input
                  id="email"
                  type="email"
                  required
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-2xl border border-white/10 bg-white/5 py-3.5 pl-11 pr-4 text-sm text-foreground outline-none transition-all placeholder:text-muted-foreground/60 hover:bg-white/10 focus:border-cyan/50 focus:bg-white/5 focus:ring-1 focus:ring-cyan/30"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label htmlFor="password" className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Password
                </label>
                <a href="#" className="text-xs text-cyan hover:underline">
                  Forgot?
                </a>
              </div>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-4 text-muted-foreground">
                  <Lock className="h-4 w-4" />
                </span>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-2xl border border-white/10 bg-white/5 py-3.5 pl-11 pr-12 text-sm text-foreground outline-none transition-all placeholder:text-muted-foreground/60 hover:bg-white/10 focus:border-cyan/50 focus:bg-white/5 focus:ring-1 focus:ring-cyan/30"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-4 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="relative flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-cyan to-violet py-3.5 text-sm font-semibold text-white shadow-lg shadow-cyan/10 transition-all hover:brightness-110 active:scale-[0.98] disabled:pointer-events-none disabled:opacity-50"
            >
              {submitting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  Sign In
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="my-8 flex items-center justify-between gap-4">
            <span className="h-px flex-1 bg-white/10" />
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/60">
              or continue with
            </span>
            <span className="h-px flex-1 bg-white/10" />
          </div>

          {/* Social Logins */}
          <div className="grid grid-cols-4 gap-3">
            {/* Google */}
            <button
              onClick={() => handleOAuthLogin("google")}
              title="Sign in with Google"
              className="glass flex items-center justify-center rounded-2xl py-3 hover:bg-white/10 transition-all active:scale-95"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24">
                <path
                  fill="#EA4335"
                  d="M12 5.04c1.62 0 3.08.56 4.22 1.65l3.15-3.15C17.45 1.74 14.93 1 12 1 7.35 1 3.39 3.65 1.41 7.5l3.78 2.93C6.07 7.29 8.78 5.04 12 5.04z"
                />
                <path
                  fill="#4285F4"
                  d="M23.49 12.27c0-.81-.07-1.59-.2-2.34H12v4.44h6.44c-.28 1.47-1.11 2.71-2.36 3.55l3.66 2.84c2.14-1.98 3.75-4.89 3.75-8.49z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.19 14.57c-.24-.72-.38-1.49-.38-2.29s.14-1.57.38-2.29L1.41 7.06C.51 8.85 0 10.87 0 13s.51 4.15 1.41 5.94l3.78-2.93z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c3.24 0 5.97-1.07 7.96-2.91l-3.66-2.84c-1.01.68-2.31 1.09-4.3 1.09-3.22 0-5.93-2.25-6.81-5.39L1.41 15.9c1.98 3.85 5.94 6.5 10.59 6.5z"
                />
              </svg>
            </button>

            {/* GitHub */}
            <button
              onClick={() => handleOAuthLogin("github")}
              title="Sign in with GitHub"
              className="glass flex items-center justify-center rounded-2xl py-3 hover:bg-white/10 transition-all active:scale-95"
            >
              <svg className="h-5 w-5 fill-foreground" viewBox="0 0 24 24">
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
              </svg>
            </button>

            {/* Discord */}
            <button
              onClick={() => handleOAuthLogin("discord")}
              title="Sign in with Discord"
              className="glass flex items-center justify-center rounded-2xl py-3 hover:bg-white/10 transition-all active:scale-95"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24">
                <path
                  fill="#5865F2"
                  d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.873-.894.077.077 0 0 1-.008-.128c.126-.093.252-.19.372-.287a.075.075 0 0 1 .077-.011c3.92 1.793 8.18 1.793 12.061 0a.073.073 0 0 1 .078.009c.12.099.246.195.373.289a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.894.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.156-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.156 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.156-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.156 2.418z"
                />
              </svg>
            </button>

            {/* Microsoft */}
            <button
              onClick={() => handleOAuthLogin("microsoft")}
              title="Sign in with Microsoft"
              className="glass flex items-center justify-center rounded-2xl py-3 hover:bg-white/10 transition-all active:scale-95"
            >
              <svg className="h-5 w-5" viewBox="0 0 23 23">
                <rect x="0" y="0" width="10.8" height="10.8" fill="#F25022" />
                <rect x="12.2" y="0" width="10.8" height="10.8" fill="#7FBA00" />
                <rect x="0" y="12.2" width="10.8" height="10.8" fill="#00A4EF" />
                <rect x="12.2" y="12.2" width="10.8" height="10.8" fill="#FFB900" />
              </svg>
            </button>
          </div>

          {/* Footer */}
          <p className="mt-10 text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="font-semibold text-cyan hover:underline">
              Create one
            </Link>
          </p>
        </div>
      </motion.div>
    </main>
  );
}
