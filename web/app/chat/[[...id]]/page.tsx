"use client";

import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus,
  MessageSquare,
  Cpu,
  BarChart3,
  Settings,
  User,
  Send,
  Paperclip,
  Mic,
  Image as ImageIcon,
  Activity,
  Coins,
  Gauge,
  Sparkles,
  ChevronRight,
  Shield,
  Trash2,
  RefreshCw,
  Copy,
  Check,
  Loader2,
} from "lucide-react";
import { Suspense, use, useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import LightRays from "@/components/backgrounds/LightRays";
import { ChatMarkdown } from "@/components/chat/ChatMarkdown";
import { useAuth } from "@/lib/auth-context";
import { useChatContext, type Msg, type Session } from "../chat-context";

const API_BASE = "http://localhost:8000/api/v1";

const providersInfo = [
  { name: "OpenAI", conf: 91, cost: 88, lat: 76, cap: 95 },
  { name: "Claude", conf: 96, cost: 72, lat: 81, cap: 98, selected: false },
  { name: "Gemini", conf: 84, cost: 91, lat: 88, cap: 89 },
  { name: "Groq", conf: 70, cost: 96, lat: 99, cap: 78 },
  { name: "DeepSeek", conf: 73, cost: 97, lat: 80, cap: 82 },
];

const routingSteps = [
  "Analyzing prompt complexity",
  "Comparing providers",
  "Optimizing cost / latency",
  "Selecting best model",
  "Streaming response",
];

type IntentMeta = {
  query_type: string;
  complexity_score: number;
  execution_cost: string;
  routed_to: string;
  model: string;
};

function deriveTitle(text: string): string {
  return text.trim().slice(0, 48) + (text.trim().length > 48 ? "…" : "");
}

interface PageProps {
  params: Promise<{ id?: string[] }>;
}

export default function ChatPage({ params }: PageProps) {
  const unwrapped = use(params);

  const activeId =
    unwrapped.id && unwrapped.id.length > 0 ? unwrapped.id[0] : "new";

  return (
    <Suspense
      fallback={
        <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background">
          <div className="relative z-10 flex flex-col items-center gap-4 text-center">
            <Loader2 className="h-12 w-12 animate-spin text-cyan" />
            <h2 className="font-display text-lg font-semibold tracking-wide text-foreground animate-pulse">
              Loading your workspace
            </h2>
          </div>
        </main>
      }
    >
      <ChatApp activeId={activeId} />
    </Suspense>
  );
}

function ChatApp({ activeId }: { activeId: string }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  const { sessions, setSessions, fetchHistory } = useChatContext();

  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [routingStep, setRoutingStep] = useState(0);
  const [intent, setIntent] = useState<IntentMeta | null>(null);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!loading && !user) router.push("/login?redirect=/chat");
  }, [user, loading, router]);

  useEffect(() => {
    if (activeId === "new" || !user?.id) return;

    const current = sessions.find((s) => s.id === activeId);
    if (current && current.messages.length > 0) return;

    const load = async () => {
      try {
        const res = await fetch(`${API_BASE}/chat/${activeId}`, {
          credentials: "include",
        });
        if (res.ok) {
          const details = await res.json();
          const loadedMsgs: Msg[] = details.messages.map((m: any) => ({
            id: m.id,
            role: m.role,
            content: m.content,
            model: m.model,
            queryType: m.query_type,
            routedTo: m.routed_to,
          }));
          setSessions((prev) => {
            const exists = prev.some((s) => s.id === activeId);
            if (exists) {
              return prev.map((s) =>
                s.id === activeId
                  ? {
                      ...s,
                      title: details.title || s.title,
                      messages: loadedMsgs,
                    }
                  : s,
              );
            }
            return [
              {
                id: activeId,
                title: details.title || "Untitled Chat",
                createdAt: details.created_at
                  ? new Date(details.created_at).getTime()
                  : Date.now(),
                messages: loadedMsgs,
              },
              ...prev,
            ];
          });
        }
      } catch (err) {
        console.error("Failed to fetch conversation details:", err);
      }
    };
    load();
  }, [activeId, user?.id]);

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) return;

    const threshold = 150;
    const isNearBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight <=
      threshold;

    if (isNearBottom || !streaming) {
      endRef.current?.scrollIntoView({
        behavior: streaming ? "auto" : "smooth",
      });
    }
  }, [sessions, streaming]);

  const activeSession: Session | null =
    activeId === "new"
      ? { id: "new", title: "New Chat", createdAt: Date.now(), messages: [] }
      : (sessions.find((s) => s.id === activeId) ?? null);

  const newChat = useCallback(() => {
    if (streaming) {
      abortRef.current?.abort();
      setStreaming(false);
    }
    setIntent(null);
    setError(null);
    router.push("/chat");
  }, [router, streaming]);

  const openSession = useCallback(
    (id: string) => {
      if (streaming) {
        abortRef.current?.abort();
        setStreaming(false);
      }
      setIntent(null);
      setError(null);
      router.push(`/chat/${id}`);
    },
    [streaming, router],
  );

  const deleteSession = useCallback(
    async (id: string, e: React.MouseEvent) => {
      e.stopPropagation();
      try {
        const res = await fetch(`${API_BASE}/chat/${id}`, {
          method: "DELETE",
          credentials: "include",
        });
        if (res.ok) {
          const next = sessions.filter((s) => s.id !== id);
          setSessions(next);
          if (id === activeId) {
            router.push(next.length > 0 ? `/chat/${next[0].id}` : "/chat");
          }
        }
      } catch (err) {
        console.error("Failed to delete session:", err);
      }
    },
    [activeId, router, sessions, setSessions],
  );

  const updateSession = useCallback(
    (sessionId: string, updater: (s: Session) => Session) => {
      setSessions((prev) =>
        prev.map((s) => (s.id === sessionId ? updater(s) : s)),
      );
    },
    [setSessions],
  );

  const send = useCallback(async () => {
    if (!input.trim() || streaming || !user) return;

    const message = input.trim();
    setInput("");
    setError(null);
    setStreaming(true);
    setRoutingStep(0);
    setIntent(null);

    const isNew = activeId === "new";
    const convId = isNew ? crypto.randomUUID() : activeId;

    const userMsg: Msg = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };
    const assistantMsgId = crypto.randomUUID();
    const placeholder: Msg = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      streaming: true,
    };

    setSessions((prev) => {
      const existing = prev.find((s) => s.id === convId);
      if (existing) {
        return prev.map((s) =>
          s.id === convId
            ? {
                ...s,
                title: s.messages.length === 0 ? deriveTitle(message) : s.title,
                messages: [...s.messages, userMsg, placeholder],
              }
            : s,
        );
      }
      const fresh: Session = {
        id: convId,
        title: deriveTitle(message),
        createdAt: Date.now(),
        messages: [userMsg, placeholder],
      };
      return [fresh, ...prev];
    });

    if (isNew) router.replace(`/chat/${convId}`);

    const iv = setInterval(() => {
      setRoutingStep((s) => (s + 1 < routingSteps.length ? s + 1 : s));
    }, 700);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        signal: controller.signal,
        body: JSON.stringify({ message, conversation_id: convId }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);

      clearInterval(iv);
      setRoutingStep(routingSteps.length - 1);

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() ?? "";

        for (const part of parts) {
          if (!part.trim()) continue;

          const sseLines = part.split("\n");
          let event = "";
          const dataLines: string[] = [];
          let inData = false;

          for (const line of sseLines) {
            if (line.startsWith("event:")) {
              event = line.slice(6).trim();
              inData = false;
            } else if (line.startsWith("data:")) {
              dataLines.push(line.slice(5));
              inData = true;
            } else if (inData) dataLines.push(line);
          }

          const rawData = dataLines.join("\n");

          if (event === "metadata") {
            try {
              const parsed: IntentMeta = JSON.parse(rawData);
              setIntent(parsed);
              updateSession(convId, (s) => ({
                ...s,
                messages: s.messages.map((m) =>
                  m.id === assistantMsgId
                    ? {
                        ...m,
                        model: parsed.model,
                        queryType: parsed.query_type,
                        routedTo: parsed.routed_to,
                      }
                    : m,
                ),
              }));
            } catch {}
          } else if (event === "token") {
            let token = rawData;
            try {
              token = JSON.parse(rawData);
            } catch {}
            if (token) {
              updateSession(convId, (s) => ({
                ...s,
                messages: s.messages.map((m) =>
                  m.id === assistantMsgId
                    ? { ...m, content: m.content + token }
                    : m,
                ),
              }));
            }
          } else if (event === "title") {
            let generatedTitle = rawData;
            try {
              generatedTitle = JSON.parse(rawData);
            } catch {}
            if (generatedTitle) {
              updateSession(convId, (s) => ({
                ...s,
                title: generatedTitle,
              }));
            }
          } else if (event === "error") {
            setError(rawData || "An error occurred during streaming.");
          }
        }
      }
    } catch (err: unknown) {
      clearInterval(iv);
      if (err instanceof Error && err.name !== "AbortError") {
        setError(
          err.message.includes("Failed to fetch")
            ? "Cannot connect to backend. Is it running on :8000?"
            : err.message,
        );
      }
    } finally {
      clearInterval(iv);
      updateSession(convId, (s) => ({
        ...s,
        messages: s.messages.map((m) =>
          m.id === assistantMsgId ? { ...m, streaming: false } : m,
        ),
      }));
      setStreaming(false);
      setRoutingStep(0);
      fetchHistory();
    }
  }, [
    input,
    streaming,
    activeId,
    user,
    updateSession,
    fetchHistory,
    router,
    setSessions,
  ]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  if (loading || !user) {
    return (
      <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background">
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,oklch(0.05_0.02_260)_95%)]" />
          <div className="absolute -top-40 left-1/2 h-125 w-125 -translate-x-1/2 rounded-full bg-gradient-to-br from-cyan/20 via-violet/10 to-transparent blur-3xl" />
        </div>
        <div className="relative z-10 flex flex-col items-center gap-4 text-center">
          <div className="relative flex h-16 w-16 items-center justify-center">
            <Loader2 className="absolute h-12 w-12 animate-spin text-cyan" />
            <div className="h-6 w-6 rounded-full bg-linear-to-br from-cyan to-violet opacity-80 blur-[2px]" />
          </div>
          <h2 className="font-display text-lg font-semibold tracking-wide text-foreground animate-pulse">
            Loading your workspace
          </h2>
        </div>
      </main>
    );
  }

  return (
    <div className="relative flex h-screen overflow-hidden bg-background text-foreground">
      <div className="absolute inset-0 pointer-events-none z-0">
        <LightRays className="absolute inset-0" />
      </div>

      {/* ── SIDEBAR ── */}
      <aside className="relative z-10 hidden w-64 flex-col border-r border-border/60 bg-background/60 backdrop-blur-2xl md:flex">
        <div className="flex items-center justify-between px-4 py-4 border-b border-border/40">
          <Link href="/" className="flex items-center gap-2">
            <img
              src="/fav.png"
              alt="LexaraAI"
              className="h-8 w-8 object-contain rounded-lg"
            />
            <span className="font-display text-sm font-semibold">
              Lexara<span className="text-gradient">AI</span>
            </span>
          </Link>
        </div>

        <div className="px-3 pt-3">
          <button
            id="new-chat-btn"
            onClick={newChat}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm bg-linear-to-r from-cyan/20 to-violet/15 text-foreground ring-1 ring-cyan/30 hover:from-cyan/30 transition"
          >
            <Plus className="h-4 w-4" />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto scrollbar-thin px-3 pb-3 pt-4">
          {sessions.length === 0 ? (
            <div className="text-center text-xs text-muted-foreground pt-8">
              No conversations yet
            </div>
          ) : (
            <>
              <div className="px-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Recent
              </div>
              <div className="space-y-0.5">
                {sessions.map((s) => (
                  <motion.div
                    key={s.id}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    onClick={() => openSession(s.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => e.key === "Enter" && openSession(s.id)}
                    className={`group flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-xs transition cursor-pointer select-none ${
                      s.id === activeId
                        ? "bg-white/10 text-foreground ring-1 ring-white/15"
                        : "text-foreground/70 hover:bg-white/5 hover:text-foreground"
                    }`}
                  >
                    <MessageSquare className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                    <span className="flex-1 truncate">{s.title}</span>
                    <button
                      onClick={(e) => deleteSession(s.id, e)}
                      className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive transition rounded"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </motion.div>
                ))}
              </div>
            </>
          )}
        </div>

        <div className="border-t border-border/40 px-3 py-3 space-y-0.5">
          {[
            { label: "Models", icon: Cpu },
            { label: "Analytics", icon: BarChart3 },
            { label: "Settings", icon: Settings },
          ].map((item) => (
            <button
              key={item.label}
              className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-muted-foreground hover:bg-white/5 hover:text-foreground transition"
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </button>
          ))}
        </div>

        <div className="border-t border-border/60 p-3 space-y-2">
          <div className="glass flex items-center gap-2 rounded-xl px-3 py-2">
            {user?.avatar_url ? (
              <img
                src={user.avatar_url}
                alt=""
                className="h-7 w-7 rounded-full object-cover"
              />
            ) : (
              <div className="grid h-7 w-7 place-items-center rounded-full bg-linear-to-br from-cyan to-violet text-background">
                <User className="h-3.5 w-3.5" />
              </div>
            )}
            <div className="min-w-0 flex-1">
              <div className="truncate text-xs font-medium">
                {user?.full_name}
              </div>
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                {user?.tier} Tier
              </div>
            </div>
          </div>
          <button
            onClick={() => logout()}
            className="flex w-full items-center justify-center gap-1.5 rounded-xl border border-border/40 bg-white/5 py-2 text-xs font-medium text-foreground hover:bg-rose-500/10 hover:border-rose-500/20 hover:text-rose-400 transition"
          >
            Sign Out
          </button>
        </div>
      </aside>

      {/* ── MAIN CHAT ── */}
      <main className="relative z-10 flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border/60 bg-background/40 px-6 py-3 backdrop-blur-xl">
          <div>
            <div className="text-[11px] uppercase tracking-wider text-muted-foreground">
              Session
            </div>
            <div className="font-display text-base font-semibold truncate max-w-xs">
              {activeSession?.title ?? "Lexara AI Workspace"}
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs">
            {intent ? (
              <>
                <Pill
                  icon={Cpu}
                  label="Model"
                  value={intent.model?.split("-").slice(0, 2).join("-") ?? "—"}
                />
                <Pill
                  icon={Sparkles}
                  label="Type"
                  value={intent.query_type?.replace(/_/g, " ") ?? "—"}
                />
                <Pill
                  icon={Gauge}
                  label="Cost"
                  value={intent.execution_cost ?? "—"}
                />
              </>
            ) : (
              <>
                <Pill icon={Cpu} label="Auto-route" value="Ready" />
                <Pill icon={Sparkles} label="Mode" value="Balanced" />
              </>
            )}
          </div>
        </header>

        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto scrollbar-thin px-6 py-8"
        >
          <div className="mx-auto flex max-w-3xl flex-col gap-6">
            {activeSession?.messages.length === 0 && !streaming && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col items-center justify-center py-24 text-center"
              >
                <div className="grid h-16 w-16 place-items-center rounded-2xl bg-linear-to-br from-cyan/20 to-violet/15 ring-1 ring-cyan/30 mb-6">
                  <Sparkles className="h-8 w-8 text-cyan" />
                </div>
                <h2 className="font-display text-2xl font-bold mb-2">
                  How can LexaraAI help?
                </h2>
                <p className="text-muted-foreground text-sm max-w-sm">
                  Ask anything. Your request is automatically routed to the best
                  model across 8+ providers in real time.
                </p>
                <div className="mt-8 grid grid-cols-2 gap-3 text-left max-w-lg">
                  {[
                    "Explain the difference between RAG and fine-tuning",
                    "Write a Python FastAPI auth middleware",
                    "Compare GPT-4o vs Claude 3.5 for coding tasks",
                    "Optimize my LLM prompt for cost efficiency",
                  ].map((s) => (
                    <button
                      key={s}
                      onClick={() => setInput(s)}
                      className="glass rounded-xl p-3 text-xs text-left text-foreground/80 hover:text-foreground hover:bg-white/10 transition"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </motion.div>
            )}

            {activeSession?.messages.map((m) => (
              <MessageBubble key={m.id} m={m} />
            ))}

            <AnimatePresence>
              {streaming &&
                (activeSession?.messages.at(-1)?.content ?? "") === "" && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="glass-strong relative overflow-hidden rounded-2xl p-4"
                  >
                    <div className="absolute inset-0 bg-linear-to-r from-cyan/5 via-violet/5 to-transparent" />
                    <div className="relative">
                      <div className="mb-3 flex items-center gap-2 text-xs">
                        <span className="relative flex h-2 w-2">
                          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan opacity-75" />
                          <span className="relative inline-flex h-2 w-2 rounded-full bg-cyan" />
                        </span>
                        <span className="font-mono uppercase tracking-wider text-cyan">
                          Routing
                        </span>
                      </div>
                      <div className="space-y-1.5">
                        {routingSteps.map((s, i) => (
                          <div
                            key={s}
                            className={`flex items-center gap-2 text-xs transition ${i <= routingStep ? "text-foreground" : "text-muted-foreground/50"}`}
                          >
                            <ChevronRight
                              className={`h-3 w-3 ${i === routingStep ? "animate-pulse text-cyan" : ""}`}
                            />
                            {s}
                            {i === routingStep ? "..." : ""}
                          </div>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                )}
            </AnimatePresence>

            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="rounded-xl border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive flex items-center justify-between gap-3"
                >
                  <span>{error}</span>
                  <button
                    onClick={() => setError(null)}
                    className="shrink-0 text-destructive/70 hover:text-destructive transition"
                  >
                    ✕
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            <div ref={endRef} />
          </div>
        </div>

        <div className="border-t border-border/60 bg-background/40 px-6 py-4 backdrop-blur-xl">
          <div className="mx-auto max-w-3xl">
            <div className="glass-strong relative flex items-end gap-2 rounded-2xl p-2 ring-1 ring-white/5 focus-within:ring-cyan/40 transition">
              <div className="flex gap-1 pl-2 text-muted-foreground items-center">
                <IconBtn icon={Paperclip} />
                <IconBtn icon={ImageIcon} />
                <IconBtn icon={Mic} />
              </div>
              <textarea
                id="chat-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                disabled={streaming}
                placeholder={
                  streaming
                    ? "Generating response…"
                    : "Ask anything — LexaraAI will route to the best model..."
                }
                className="min-h-10 flex-1 resize-none bg-transparent px-2 py-2 text-sm placeholder:text-muted-foreground/60 focus:outline-none disabled:opacity-50"
                style={{ maxHeight: "200px", overflowY: "auto" }}
              />
              {streaming ? (
                <button
                  onClick={() => abortRef.current?.abort()}
                  className="grid h-9 w-9 place-items-center rounded-xl bg-destructive/80 text-white shadow transition-all hover:scale-105"
                >
                  <RefreshCw className="h-4 w-4 animate-spin" />
                </button>
              ) : (
                <button
                  id="send-btn"
                  onClick={send}
                  disabled={!input.trim()}
                  className="grid h-9 w-9 place-items-center rounded-xl bg-linear-to-br from-cyan to-violet text-background shadow-primary shadow transition-all hover:scale-105 disabled:shadow-none disabled:opacity-40"
                >
                  <Send className="h-4 w-4 text-foreground" />
                </button>
              )}
            </div>
            <div className="mt-2 text-center text-[10px] text-muted-foreground">
              Auto-routing across 8 providers · Press{" "}
              <kbd className="rounded bg-white/10 px-1">Enter</kbd> to send ·{" "}
              <kbd className="rounded bg-white/10 px-1">Shift+Enter</kbd> for
              newline
            </div>
          </div>
        </div>
      </main>

      {/* ── INTELLIGENCE PANEL ── */}
      <aside className="relative z-10 hidden w-80 flex-col border-l border-border/60 bg-background/60 backdrop-blur-2xl xl:flex">
        <div className="border-b border-border/60 px-5 py-4">
          <div className="text-[11px] uppercase tracking-wider text-muted-foreground">
            Intelligence
          </div>
          <div className="font-display text-base font-semibold">
            Live Telemetry
          </div>
        </div>
        <div className="flex-1 space-y-4 overflow-y-auto scrollbar-thin p-4">
          <Panel title="Routing Decision" icon={Cpu}>
            {intent ? (
              <div className="space-y-2">
                <InfoRow label="Model" value={intent.model} highlight />
                <InfoRow
                  label="Query Type"
                  value={intent.query_type?.replace(/_/g, " ")}
                />
                <InfoRow label="Routed To" value={intent.routed_to} />
                <InfoRow label="Cost Tier" value={intent.execution_cost} />
              </div>
            ) : (
              <div className="space-y-2">
                {providersInfo.map((p) => (
                  <div
                    key={p.name}
                    className={`rounded-xl p-2.5 ${p.selected ? "bg-linear-to-r from-cyan/15 to-violet/10 ring-1 ring-cyan/30" : "bg-white/3"}`}
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-medium">{p.name}</span>
                      {p.selected && (
                        <span className="rounded-full bg-cyan/20 px-2 py-0.5 text-[9px] font-semibold uppercase text-cyan">
                          Selected
                        </span>
                      )}
                    </div>
                    <div className="mt-2 grid grid-cols-4 gap-1.5 text-[9px]">
                      {(["Conf", "Cost", "Lat", "Cap"] as const).map((k, i) => (
                        <div key={k}>
                          <div className="text-muted-foreground">{k}</div>
                          <div className="mt-0.5 h-1 overflow-hidden rounded-full bg-white/10">
                            <div
                              className="h-full bg-linear-to-r from-cyan to-violet"
                              style={{
                                width: `${[p.conf, p.cost, p.lat, p.cap][i]}%`,
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Panel>

          <Panel title="Session Stats" icon={Activity}>
            <div className="space-y-2 text-xs">
              <InfoRow
                label="Messages"
                value={String(activeSession?.messages.length ?? 0)}
              />
              <InfoRow
                label="Session ID"
                value={activeId === "new" ? "—" : activeId.slice(0, 12) + "…"}
              />
              <InfoRow label="Sessions" value={String(sessions.length)} />
            </div>
          </Panel>

          <Panel title="Request Cost" icon={Coins}>
            <div className="flex items-baseline justify-between">
              <span className="font-display text-2xl font-bold text-gradient">
                {intent?.execution_cost ?? "—"}
              </span>
              <span className="text-[10px] text-emerald-400">
                auto-optimized
              </span>
            </div>
          </Panel>

          <Panel title="Provider Health" icon={Shield}>
            <div className="space-y-1.5">
              {[
                ["OpenAI", "operational"],
                ["Anthropic", "operational"],
                ["Gemini", "degraded"],
                ["Groq", "operational"],
              ].map(([n, s]) => (
                <div
                  key={n}
                  className="flex items-center justify-between text-xs"
                >
                  <span>{n}</span>
                  <span
                    className={`flex items-center gap-1.5 ${s === "operational" ? "text-emerald-400" : "text-yellow-400"}`}
                  >
                    <span
                      className={`h-1.5 w-1.5 rounded-full ${s === "operational" ? "bg-emerald-400" : "bg-yellow-400"}`}
                    />
                    {s}
                  </span>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Stream Status" icon={Gauge}>
            <div className="flex items-center gap-2 text-xs">
              <span
                className={`relative flex h-2 w-2 ${streaming ? "block" : "hidden"}`}
              >
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-cyan" />
              </span>
              <span
                className={
                  streaming ? "text-cyan font-mono" : "text-muted-foreground"
                }
              >
                {streaming ? "Streaming…" : "Idle"}
              </span>
            </div>
          </Panel>
        </div>
      </aside>
    </div>
  );
}

function MsgCopyBtn({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text).catch(() => {});
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      title="Copy response"
      className="flex items-center gap-1.5 rounded-md px-2 py-1 text-[10px] text-muted-foreground hover:bg-white/5 hover:text-foreground transition"
    >
      {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
      <span>{copied ? "Copied!" : "Copy"}</span>
    </button>
  );
}

function MessageBubble({ m }: { m: Msg }) {
  const isUser = m.role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div className={`max-w-[85%] w-full ${isUser ? "flex justify-end" : ""}`}>
        {!isUser && (
          <div className="mb-1.5 flex items-center justify-between">
            <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-muted-foreground">
              <Sparkles className="h-3 w-3 text-cyan" />
              {m.model && (
                <span className="text-cyan">
                  {m.model.split("-").slice(0, 3).join("-")}
                </span>
              )}
              {m.routedTo && <span>· {m.routedTo.replace(/_/g, " ")}</span>}
              {!m.model && !m.routedTo && (
                <span className="text-cyan">LexaraAI</span>
              )}
            </div>
            {m.content && !m.streaming && <MsgCopyBtn text={m.content} />}
          </div>
        )}
        <div
          className={
            isUser
              ? "rounded-2xl rounded-tr-sm bg-linear-to-br from-cyan/20 to-violet/15 px-4 py-3 text-sm text-foreground ring-1 ring-cyan/25 shadow-[0_0_30px_-12px_oklch(0.78_0.17_210)]"
              : "glass-strong rounded-2xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed text-foreground/95"
          }
        >
          {m.streaming && m.content === "" ? (
            <span className="inline-flex gap-1 items-center text-muted-foreground">
              {[0, 150, 300].map((d) => (
                <span
                  key={d}
                  className="animate-bounce"
                  style={{ animationDelay: `${d}ms` }}
                >
                  ●
                </span>
              ))}
            </span>
          ) : isUser ? (
            <div className="whitespace-pre-wrap text-sm">{m.content}</div>
          ) : (
            <ChatMarkdown content={m.content} streaming={m.streaming} />
          )}
        </div>
      </div>
    </motion.div>
  );
}

function Pill({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
}) {
  return (
    <div className="glass hidden items-center gap-2 rounded-full px-3 py-1.5 md:flex">
      <Icon className="h-3 w-3 text-cyan" />
      <span className="text-muted-foreground">{label}</span>
      <span className="font-mono font-medium">{value}</span>
    </div>
  );
}

function IconBtn({
  icon: Icon,
}: {
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <button className="grid h-8 w-8 place-items-center rounded-lg text-muted-foreground transition hover:bg-white/5 hover:text-foreground">
      <Icon className="h-4 w-4" />
    </button>
  );
}

function Panel({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}) {
  return (
    <div className="glass rounded-2xl p-4">
      <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        <Icon className="h-3.5 w-3.5 text-cyan" />
        {title}
      </div>
      {children}
    </div>
  );
}

function InfoRow({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className="flex items-center justify-between text-xs">
      <span className="text-muted-foreground">{label}</span>
      <span
        className={highlight ? "text-cyan font-mono font-medium" : "font-mono"}
      >
        {value}
      </span>
    </div>
  );
}
