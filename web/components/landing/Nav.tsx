"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Zap, LogOut } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export function Nav() {
  const { user, logout } = useAuth();

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-4"
    >
      <nav className="glass flex w-full max-w-6xl items-center justify-between rounded-full px-5 py-2.5 backdrop-blur-2xl">
        <Link href="/" className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-linear-to-br from-cyan to-violet">
            <Zap className="h-4 w-4 text-foreground" strokeWidth={2.5} />
          </div>
          <span className="font-display text-lg font-semibold tracking-tight">
            <span className="text-gradient">Lexara</span> AI
          </span>
        </Link>
        <div className="hidden items-center gap-6 text-sm text-foreground md:flex">
          <a href="#features" className="hover:text-foreground">
            Features
          </a>
          <a href="#flow" className="hover:text-foreground">
            Routing
          </a>
          <a href="#savings" className="hover:text-foreground">
            Savings
          </a>
          <a href="#pricing" className="hover:text-foreground">
            Pricing
          </a>
          <a href="#dashboard" className="hover:text-foreground">
            Dashboard
          </a>
        </div>
        <div className="flex items-center gap-2">
          {user ? (
            <>
              <span className="hidden text-xs text-muted-foreground mr-2 sm:inline-block">
                Hello, <span className="font-semibold text-foreground">{user.full_name}</span>
              </span>
              <Link
                href="/chat"
                className="rounded-full border border-border bg-white/5 px-4 py-1.5 text-xs font-medium text-foreground transition hover:bg-white/10"
              >
                Go to Chat
              </Link>
              <button
                onClick={() => logout()}
                className="flex items-center gap-1 rounded-full text-foreground bg-white/5 border border-border px-3 py-1.5 text-xs font-semibold transition hover:bg-rose-500/10 hover:border-rose-500/20 hover:text-rose-400"
                title="Sign Out"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Sign Out</span>
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="hidden rounded-full border border-border bg-white/5 px-4 py-1.5 text-xs font-medium text-foreground transition hover:bg-white/10 sm:inline-flex"
              >
                Open App
              </Link>
              <Link
                href="/signup"
                className="rounded-full text-foreground bg-linear-to-r from-cyan to-violet px-4 py-1.5 text-xs font-semibold shadow-[0_0_30px_-8px_oklch(0.78_0.17_210)] transition hover:opacity-90"
              >
                Start Free
              </Link>
            </>
          )}
        </div>
      </nav>
    </motion.header>
  );
}
