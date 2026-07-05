"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useAuth } from "@/lib/auth-context";

// ─── Types ────────────────────────────────────────────────────────────────────

export type Msg = {
  id: string;
  role: "user" | "assistant";
  content: string;
  model?: string;
  queryType?: string;
  routedTo?: string;
  streaming?: boolean;
};

export type Session = {
  id: string;
  title: string;
  createdAt: number;
  messages: Msg[];
};

const API_BASE = "http://localhost:8000/api/v1";

// ─── Context ─────────────────────────────────────────────────────────────────

interface ChatContextValue {
  sessions: Session[];
  setSessions: React.Dispatch<React.SetStateAction<Session[]>>;
  fetchHistory: () => Promise<void>;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function useChatContext() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChatContext must be used within ChatProvider");
  return ctx;
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);

  const fetchHistory = useCallback(async () => {
    if (!user) return;
    try {
      const res = await fetch(`${API_BASE}/chat/history`, {
        credentials: "include",
      });
      if (res.ok) {
        const historyList = await res.json();
        setSessions((prev) =>
          historyList.map((h: any) => {
            const existing = prev.find((s) => s.id === h.id);
            return {
              id: h.id,
              title: h.title || "Untitled Chat",
              createdAt: new Date(h.created_at).getTime(),
              messages: existing ? existing.messages : [],
            };
          })
        );
      }
    } catch (err) {
      console.error("Failed to load conversation history from DB:", err);
    }
  }, [user]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return (
    <ChatContext.Provider value={{ sessions, setSessions, fetchHistory }}>
      {children}
    </ChatContext.Provider>
  );
}
