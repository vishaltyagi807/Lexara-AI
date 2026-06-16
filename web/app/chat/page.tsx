"use client";

import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus,
  MessageSquare,
  FolderKanban,
  Cpu,
  BarChart3,
  Settings,
  User,
  Send,
  Paperclip,
  Mic,
  Image as ImageIcon,
  Zap,
  Activity,
  Coins,
  Gauge,
  Sparkles,
  ChevronRight,
  Shield,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import LightRays from "@/components/backgrounds/LightRays";

type Msg = {
  id: string;
  role: "user" | "assistant";
  content: string;
  model?: string;
};

const sidebarSections = [
  { label: "New Chat", icon: Plus, primary: true },
  { label: "Recent", icon: MessageSquare },
  { label: "Projects", icon: FolderKanban },
  { label: "Models", icon: Cpu },
  { label: "Analytics", icon: BarChart3 },
  { label: "Settings", icon: Settings },
];

const recent = [
  "Optimize embedding pipeline",
  "Compare GPT-5 vs Claude 4",
  "Refactor auth middleware",
  "Cost forecast Q1 2036",
  "Latency anomaly debug",
];

const providersInfo = [
  { name: "OpenAI", conf: 91, cost: 88, lat: 76, cap: 95 },
  { name: "Claude", conf: 96, cost: 72, lat: 81, cap: 98, selected: true },
  { name: "Gemini", conf: 84, cost: 91, lat: 88, cap: 89 },
  { name: "Groq", conf: 70, cost: 96, lat: 99, cap: 78 },
  { name: "DeepSeek", conf: 73, cost: 97, lat: 80, cap: 82 },
];

const routingSteps = [
  "Analyzing prompt complexity",
  "Comparing 8 providers",
  "Optimizing cost / latency",
  "Selected Claude 4 Sonnet",
  "Streaming response",
];

export default function ChatApp() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: "1",
      role: "user",
      content:
        "Help me design a token-efficient RAG pipeline for a 200M doc corpus.",
    },
    {
      id: "2",
      role: "assistant",
      model: "Claude 4 Sonnet",
      content:
        "Great problem. For 200M docs, I'd recommend a tiered architecture:\n\n1. **Coarse retrieval** with a small, fast embedding model (e.g. bge-small) sharded across regions.\n2. **Re-rank** with a stronger cross-encoder only on the top 100.\n3. **Adaptive context window** — feed the LLM only the spans your re-ranker scored above threshold.\n\nLexaraAI would route the coarse step to Groq for sub-50ms latency, re-rank to OpenAI's embedding-3, and the final generation to Claude for reasoning.",
    },
  ]);
  const [input, setInput] = useState("");
  const [routing, setRouting] = useState(false);
  const [step, setStep] = useState(0);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, routing]);

  function send() {
    if (!input.trim()) return;
    const user: Msg = {
      id: Math.random().toString(),
      role: "user",
      content: input,
    };
    setMessages((m) => [...m, user]);
    setInput("");
    setRouting(true);
    setStep(0);
    const iv = setInterval(
      () => setStep((s) => (s + 1 >= routingSteps.length ? s : s + 1)),
      600,
    );
    setTimeout(
      () => {
        clearInterval(iv);
        setRouting(false);
        setStep(0);
        setMessages((m) => [
          ...m,
          {
            id: Math.random().toString(),
            role: "assistant",
            model: "Claude 4 Sonnet",
            content:
              "Routed to Claude 4 Sonnet based on reasoning complexity. Here's the optimized response with the lowest expected cost across all eligible providers.",
          },
        ]);
      },
      routingSteps.length * 600 + 300,
    );
  }

  return (
    <div className="relative flex h-screen overflow-hidden bg-background text-foreground">
      <div className="absolute inset-0 pointer-events-none z-0">
        <LightRays className="absolute inset-0" />
      </div>

      {/* SIDEBAR */}
      <aside className="relative z-10 hidden w-64 flex-col border-r border-border/60 bg-background/60 backdrop-blur-2xl md:flex">
        <div className="flex items-center justify-between px-4 py-4">
          <Link href="/" className="flex items-center gap-2">
            <div className="grid h-8 w-8 place-items-center rounded-lg bg-linear-to-br from-cyan to-violet">
              <Zap className="h-4 w-4 text-foreground" strokeWidth={2.5} />
            </div>
            <span className="font-display text-sm font-semibold">
              Lexara<span className="text-gradient">AI</span>
            </span>
          </Link>
        </div>
        <div className="flex-1 overflow-y-auto scrollbar-thin px-3 pb-3 pt-2">
          <div className="space-y-0.5">
            {sidebarSections.map((s) => (
              <button
                key={s.label}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm transition ${
                  s.primary
                    ? "bg-linear-to-r from-cyan/20 to-violet/15 text-foreground ring-1 ring-cyan/30 hover:from-cyan/30"
                    : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                }`}
              >
                <s.icon className="h-4 w-4" />
                {s.label}
              </button>
            ))}
          </div>
          <div className="mt-6">
            <div className="px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Recent
            </div>
            <div className="mt-2 space-y-0.5">
              {recent.map((r, i) => (
                <button
                  key={i}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-1.5 text-left text-xs text-foreground/75 hover:bg-white/5 hover:text-foreground"
                >
                  <MessageSquare className="h-3 w-3 shrink-0 text-muted-foreground" />
                  <span className="truncate">{r}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="border-t border-border/60 p-3">
          <div className="glass flex items-center gap-2 rounded-xl px-3 py-2">
            <div className="grid h-7 w-7 place-items-center rounded-full bg-linear-to-br from-cyan to-violet text-background">
              <User className="h-3.5 w-3.5" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-xs font-medium">alex@lexara.ai</div>
              <div className="text-[10px] text-muted-foreground">
                Pro · 1M tokens left
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN CHAT */}
      <main className="relative z-10 flex min-w-0 flex-1 flex-col">
        {/* header */}
        <header className="flex items-center justify-between border-b border-border/60 bg-background/40 px-6 py-3 backdrop-blur-xl">
          <div>
            <div className="text-[11px] uppercase tracking-wider text-muted-foreground">
              Workspace
            </div>
            <div className="font-display text-base font-semibold">
              Lexara AI Workspace
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <Pill icon={Cpu} label="Auto-route" value="Claude 4" />
            <Pill icon={Sparkles} label="Mode" value="Balanced" />
            <Pill icon={Gauge} label="Latency" value="318ms" />
            <Pill icon={Coins} label="Cost" value="$0.0042" />
          </div>
        </header>

        {/* messages */}
        <div className="flex-1 overflow-y-auto scrollbar-thin px-6 py-8">
          <div className="mx-auto flex max-w-3xl flex-col gap-6">
            {messages.map((m) => (
              <MessageBubble key={m.id} m={m} />
            ))}
            <AnimatePresence>
              {routing && (
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
                          className={`flex items-center gap-2 text-xs transition ${i <= step ? "text-foreground" : "text-muted-foreground/50"}`}
                        >
                          <ChevronRight
                            className={`h-3 w-3 ${i === step ? "animate-pulse text-cyan" : ""}`}
                          />
                          {s}
                          {i === step ? "..." : ""}
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={endRef} />
          </div>
        </div>

        {/* input */}
        <div className="border-t border-border/60 bg-background/40 px-6 py-4 backdrop-blur-xl">
          <div className="mx-auto max-w-5xl">
            <div className="glass-strong relative bg-white flex items-center justify-center gap-2 rounded-2xl p-2 ring-1 ring-white/5 focus-within:ring-cyan/40">
              <div className="flex gap-1 pl-2 text-muted-foreground items-center justify-center">
                <IconBtn icon={Paperclip} />
                <IconBtn icon={ImageIcon} />
                <IconBtn icon={Mic} />
              </div>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                }}
                rows={1}
                placeholder="Ask anything — LexaraAI will route to the best model..."
                className="min-h-10 flex-1 resize-none bg-transparent px-2 py-2 text-sm placeholder:text-muted-foreground/60 focus:outline-none"
              />
              <button
                onClick={send}
                disabled={!input.trim()}
                className="grid h-9 w-9 place-items-center rounded-xl bg-linear-to-br from-cyan to-violet text-background shadow-primary shadow transition-all hover:scale-105 disabled:shadow-none disabled:opacity-40"
              >
                <Send className="h-4 w-4 text-foreground" />
              </button>
            </div>
            <div className="mt-2 text-center text-[10px] text-muted-foreground">
              Auto-routing across 8 providers · Press{" "}
              <kbd className="rounded bg-white/10 px-1">Enter</kbd> to send
            </div>
          </div>
        </div>
      </main>

      {/* INTELLIGENCE PANEL */}
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
          <Panel title="Provider Selection" icon={Cpu}>
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
                    {[
                      ["Conf", p.conf],
                      ["Cost", p.cost],
                      ["Lat", p.lat],
                      ["Cap", p.cap],
                    ].map(([k, v]) => (
                      <div key={k as string}>
                        <div className="text-muted-foreground">{k}</div>
                        <div className="mt-0.5 h-1 overflow-hidden rounded-full bg-white/10">
                          <div
                            className="h-full bg-linear-to-r from-cyan to-violet"
                            style={{ width: `${v}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Token Usage" icon={Activity}>
            <MiniSpark color="oklch(0.85 0.16 200)" />
            <div className="mt-2 flex justify-between text-xs">
              <span className="text-muted-foreground">This session</span>
              <span className="font-mono">12,847</span>
            </div>
          </Panel>

          <Panel title="Request Cost" icon={Coins}>
            <div className="flex items-baseline justify-between">
              <span className="font-display text-2xl font-bold text-gradient">
                $0.0042
              </span>
              <span className="text-[10px] text-emerald-400">
                -83% vs GPT-5
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

          <Panel title="Budget Tracking" icon={Gauge}>
            <div className="mb-1 flex justify-between text-xs">
              <span className="text-muted-foreground">$42 / $500 mo</span>
              <span className="font-mono text-cyan">8.4%</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full bg-linear-to-r from-cyan to-violet"
                style={{ width: "8.4%" }}
              />
            </div>
          </Panel>
        </div>
      </aside>
    </div>
  );
}

function MessageBubble({ m }: { m: Msg }) {
  const user = m.role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={`flex ${user ? "justify-end" : "justify-start"}`}
    >
      <div className={`max-w-[85%] ${user ? "order-2" : ""}`}>
        {!user && m.model && (
          <div className="mb-1.5 flex items-center gap-2 text-[10px] uppercase tracking-wider text-muted-foreground">
            <Sparkles className="h-3 w-3 text-cyan" />
            <span className="text-cyan">{m.model}</span>
            <span>· routed by LexaraAI</span>
          </div>
        )}
        <div
          className={
            user
              ? "rounded-2xl rounded-tr-sm bg-linear-to-br from-cyan/20 to-violet/15 px-4 py-3 text-sm text-foreground ring-1 ring-cyan/25 shadow-[0_0_30px_-12px_oklch(0.78_0.17_210)]"
              : "glass-strong rounded-2xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed text-foreground/95"
          }
        >
          <div className="whitespace-pre-wrap">{m.content}</div>
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
  icon: any;
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

function IconBtn({ icon: Icon }: { icon: any }) {
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
  icon: any;
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

function MiniSpark({ color }: { color: string }) {
  const [pts, setPts] = useState<string>("");

  useEffect(() => {
    const data = Array.from({ length: 30 }, () => 20 + Math.random() * 60);
    const generatedPts = data
      .map((v, i) => `${(i / (data.length - 1)) * 100},${100 - v}`)
      .join(" ");
    setPts(generatedPts);
  }, []);

  if (!pts) {
    return <div className="h-12 w-full" />;
  }

  return (
    <svg
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      className="h-12 w-full"
    >
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" />
    </svg>
  );
}
