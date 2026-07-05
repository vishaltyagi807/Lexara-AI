"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Lock, User, Loader2, ArrowRight, AlertTriangle, Check, X, Eye, EyeOff } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function SignupPage() {
  const { signup } = useAuth();
  const router = useRouter();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Password requirements validation state
  const hasMinLength = password.length >= 8;
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /[0-9]/.test(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!hasMinLength || !hasLetter || !hasNumber) {
      setFormError("Password does not meet the complexity requirements.");
      return;
    }

    setSubmitting(true);

    try {
      await signup(email, password, fullName);
      router.push("/chat");
    } catch (err: any) {
      setFormError(err.message || "Registration failed. Please try again.");
      setSubmitting(false);
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
              Create your account
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Get started with automated LLM routing
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
                    <span className="font-semibold">Registration Issue</span>
                    <p className="mt-1 text-xs opacity-90">{formError}</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Form */}
          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label htmlFor="fullName" className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Display Name
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-4 text-muted-foreground">
                  <User className="h-4 w-4" />
                </span>
                <input
                  id="fullName"
                  type="text"
                  required
                  placeholder="John Doe"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-2xl border border-white/10 bg-white/5 py-3.5 pl-11 pr-4 text-sm text-foreground outline-none transition-all placeholder:text-muted-foreground/60 hover:bg-white/10 focus:border-cyan/50 focus:bg-white/5 focus:ring-1 focus:ring-cyan/30"
                />
              </div>
            </div>

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
              <label htmlFor="password" className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Password
              </label>
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

              {/* Password Requirements Checklist */}
              <div className="mt-3.5 space-y-1.5 rounded-2xl bg-white/2.5 p-3.5 border border-white/5">
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/75 mb-1">
                  Complexity Checklist
                </p>
                <div className="flex items-center gap-2 text-xs">
                  {hasMinLength ? (
                    <span className="flex h-4 w-4 items-center justify-center rounded-full bg-emerald/20 text-emerald">
                      <Check className="h-3 w-3 stroke-[3]" />
                    </span>
                  ) : (
                    <span className="flex h-4 w-4 items-center justify-center rounded-full bg-white/5 text-muted-foreground/50">
                      <X className="h-3 w-3" />
                    </span>
                  )}
                  <span className={hasMinLength ? "text-muted-foreground line-through opacity-50" : "text-muted-foreground"}>
                    At least 8 characters
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  {hasLetter ? (
                    <span className="flex h-4 w-4 items-center justify-center rounded-full bg-emerald/20 text-emerald">
                      <Check className="h-3 w-3 stroke-[3]" />
                    </span>
                  ) : (
                    <span className="flex h-4 w-4 items-center justify-center rounded-full bg-white/5 text-muted-foreground/50">
                      <X className="h-3 w-3" />
                    </span>
                  )}
                  <span className={hasLetter ? "text-muted-foreground line-through opacity-50" : "text-muted-foreground"}>
                    At least one letter
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  {hasNumber ? (
                    <span className="flex h-4 w-4 items-center justify-center rounded-full bg-emerald/20 text-emerald">
                      <Check className="h-3 w-3 stroke-[3]" />
                    </span>
                  ) : (
                    <span className="flex h-4 w-4 items-center justify-center rounded-full bg-white/5 text-muted-foreground/50">
                      <X className="h-3 w-3" />
                    </span>
                  )}
                  <span className={hasNumber ? "text-muted-foreground line-through opacity-50" : "text-muted-foreground"}>
                    At least one digit
                  </span>
                </div>
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
                  Create Account
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <p className="mt-10 text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-cyan hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </main>
  );
}
