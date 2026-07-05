"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Play,
  Cpu,
  Coins,
  Shield,
  BarChart3,
  Activity,
  Layers,
  Check,
  X,
  Sparkles,
  Zap,
  Gauge,
  Network,
} from "lucide-react";
import { useState } from "react";
import Lightfall from "@/components/backgrounds/Lightfall";
import { Nav } from "@/components/landing/Nav";
import { RoutingNetwork } from "@/components/landing/RoutingNetwork";

const providers = [
  "OpenAI",
  "Anthropic",
  "Google",
  "Groq",
  "DeepSeek",
  "Together AI",
  "OpenRouter",
  "Mistral",
];

const features = [
  {
    icon: Cpu,
    title: "Smart Routing Engine",
    desc: "LexaraAI predicts the optimal provider in real time using prompt telemetry, complexity scoring, and model capability matching.",
  },
  {
    icon: Coins,
    title: "Token Optimization",
    desc: "Compress, cache, and rewrite prompts intelligently. Cut spend by routing simple tasks to lean models.",
  },
  {
    icon: Shield,
    title: "Fallback Orchestration",
    desc: "Provider down? LexaraAI fails over instantly with zero user interruption and full state continuity.",
  },
  {
    icon: BarChart3,
    title: "Cost Intelligence",
    desc: "Live dashboards forecast spend across providers and surface savings opportunities before they vanish.",
  },
  {
    icon: Activity,
    title: "Real-Time Analytics",
    desc: "Stream latency, throughput, and routing decisions into your observability stack with sub-second resolution.",
  },
  {
    icon: Layers,
    title: "Provider Abstraction",
    desc: "Integrate once with a unified API. Swap models, regions, and vendors without touching application code.",
  },
];

const flowSteps = [
  { n: "01", title: "Receive Prompt", desc: "Ingest request" },
  { n: "02", title: "Analyze Complexity", desc: "Score intent + tokens" },
  { n: "03", title: "Predict Cost", desc: "Model price oracle" },
  { n: "04", title: "Choose Best Model", desc: "Capability match" },
  { n: "05", title: "Execute Request", desc: "Stream with retries" },
  { n: "06", title: "Return Response", desc: "Optimized output" },
];

const comparison = [
  ["Single Provider Lock-in", false, true],
  ["Automatic Fallback", false, true],
  ["Cost Optimization", false, true],
  ["Token-Aware Routing", false, true],
  ["Capability Matching", false, true],
  ["Latency Optimization", false, true],
];

const testimonials = [
  {
    name: "Maya Chen",
    role: "Staff Engineer · Vela",
    quote:
      "We cut LLM spend 71% in two weeks. The routing decisions are sharper than what our team was hand-tuning.",
  },
  {
    name: "Daniel Roth",
    role: "CTO · Northbeam",
    quote:
      "LexaraAI is the missing layer. One API, every model, and a dashboard that actually tells us where money is going.",
  },
  {
    name: "Priya Anand",
    role: "AI Lead · Helio Labs",
    quote:
      "The fallback story is unreal. Anthropic had an outage and our users didn't notice. That's the entire pitch.",
  },
];

const plans = [
  {
    name: "Starter",
    price: "$0",
    tag: "For builders",
    features: [
      "10K requests / mo",
      "All providers",
      "Basic analytics",
      "Community support",
    ],
    cta: "Start Free",
  },
  {
    name: "Pro",
    price: "$49",
    tag: "For teams",
    features: [
      "1M requests / mo",
      "Smart routing engine",
      "Cost forecasting",
      "Priority support",
      "Custom fallback chains",
    ],
    cta: "Start Pro",
    highlight: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    tag: "For scale",
    features: [
      "Unlimited routing",
      "On-prem deployment",
      "SOC2 + HIPAA",
      "Dedicated SRE",
      "Custom SLAs",
    ],
    cta: "Book Demo",
  },
];

export default function Landing() {
  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background text-foreground">
      <Nav />

      {/* HERO */}
      <section className="relative flex min-h-screen items-center pt-24 overflow-hidden">
        <Lightfall
          colors={["#A6C8FF", "#5227FF", "#FF9FFC"]}
          backgroundColor="#0A29FF"
          speed={0.5}
          streakCount={2}
          streakWidth={0.2}
          streakLength={1.4}
          glow={2}
          density={0.4}
          twinkle={0.5}
          zoom={2.5}
          backgroundGlow={0.2}
          opacity={2}
          mouseInteraction={false}
          mouseStrength={0.9}
          mouseRadius={0.5}
          className="absolute inset-0 z-0 pointer-events-none"
        />
        <div className="relative mx-auto grid w-full max-w-7xl grid-cols-1 gap-12 px-6 lg:grid-cols-2 lg:items-center z-10">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass mb-6 inline-flex items-center gap-2 rounded-full px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-muted-foreground"
            >
              <Sparkles className="h-3 w-3 text-cyan" />
              AI Routing Platform
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="font-display text-6xl font-bold leading-[0.95] tracking-tight md:text-8xl"
            >
              <span className="text-gradient">LEXARA</span>
              <span className="text-foreground">AI</span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground md:text-xl"
            >
              Automatically route every AI request to the smartest model,
              <br className="hidden md:block" />
              at the lowest cost, with maximum performance.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-8 flex flex-wrap gap-3"
            >
              <Link
                href="/chat"
                className="group inline-flex items-center gap-2 rounded-full bg-linear-to-r text-white from-cyan to-violet px-6 py-3 text-sm font-semibold glow-cyan transition hover:scale-[1.02]"
              >
                Start Building
                <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
              </Link>
              <button className="glass inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm font-medium text-foreground transition hover:bg-white/10">
                <Play className="h-4 w-4" />
                Watch Demo
              </button>
            </motion.div>

            {/* stats */}
            <div className="mt-12 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                { v: "87%", l: "Token Savings" },
                { v: "42ms", l: "Routing Decision" },
                { v: "99.99%", l: "Availability" },
                { v: "8+", l: "Providers" },
              ].map((s, i) => (
                <motion.div
                  key={s.l}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 + i * 0.07 }}
                  className="glass rounded-2xl p-4 animate-float"
                  style={{ animationDelay: `${i * 0.5}s` }}
                >
                  <div className="font-display text-2xl font-bold text-gradient">
                    {s.v}
                  </div>
                  <div className="mt-1 text-[11px] uppercase tracking-wider text-muted-foreground">
                    {s.l}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            <RoutingNetwork />
          </motion.div>
        </div>
      </section>

      {/* TRUST BAR */}
      <section className="relative border-y border-border/50 bg-background/40 py-8 backdrop-blur">
        <div className="mb-3 text-center text-[11px] uppercase tracking-[0.25em] text-muted-foreground">
          Orchestrating every major model provider
        </div>
        <div className="relative overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_15%,black_85%,transparent)]">
          <div className="flex w-max animate-marquee gap-16 px-8">
            {[...providers, ...providers].map((p, i) => (
              <div
                key={i}
                className="font-display text-2xl font-semibold tracking-tight text-muted-foreground/80"
              >
                {p}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" className="relative px-6 py-32">
        <div className="mx-auto max-w-7xl">
          <SectionHeader
            kicker="Infrastructure"
            title="Built For Intelligent AI Infrastructure"
            sub="Production-grade primitives for teams shipping AI at real scale."
          />
          <div className="mt-16 grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="glass group relative overflow-hidden rounded-3xl p-6 transition hover:bg-white/[0.07]"
              >
                <div className="absolute -right-12 -top-12 h-40 w-40 rounded-full bg-gradient-to-br from-cyan/30 to-violet/20 opacity-0 blur-3xl transition group-hover:opacity-100" />
                <div className="relative">
                  <div className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-br from-white/10 to-white/5 ring-1 ring-white/10">
                    <f.icon className="h-5 w-5 text-cyan" />
                  </div>
                  <h3 className="mt-5 font-display text-xl font-semibold">
                    {f.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {f.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* SAVINGS CALCULATOR */}
      <SavingsCalculator />

      {/* FLOW */}
      <section id="flow" className="relative px-6 py-32">
        <div className="mx-auto max-w-7xl">
          <SectionHeader
            kicker="Pipeline"
            title="The AI Routing Flow"
            sub="Every request traverses a six-stage decision graph in under 50ms."
          />
          <div className="relative mt-16 overflow-x-auto pb-4">
            <div className="flex min-w-max items-stretch gap-4">
              {flowSteps.map((s, i) => (
                <motion.div
                  key={s.n}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08 }}
                  className="glass relative w-56 rounded-2xl p-5"
                >
                  <div className="font-mono text-xs text-cyan">{s.n}</div>
                  <div className="mt-3 font-display text-lg font-semibold">
                    {s.title}
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    {s.desc}
                  </div>
                  {i < flowSteps.length - 1 && (
                    <div className="absolute right-[-18px] top-1/2 hidden -translate-y-1/2 md:block">
                      <ArrowRight className="h-4 w-4 text-cyan/60" />
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* DASHBOARD PREVIEW */}
      <section id="dashboard" className="relative px-6 py-32">
        <div className="mx-auto max-w-7xl">
          <SectionHeader
            kicker="Mission Control"
            title="Your AI ops, fully observable."
            sub="A dark glassmorphic command center for every request, every dollar, every millisecond."
          />
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="glass-strong relative mt-16 overflow-hidden rounded-3xl p-6"
          >
            <div className="absolute inset-0 bg-grid opacity-30" />
            <div className="relative grid grid-cols-2 gap-4 lg:grid-cols-4">
              {[
                { k: "Requests", v: "2.4M", c: "+12.3%", icon: Zap },
                { k: "Spend", v: "$1,284", c: "-71% vs single", icon: Coins },
                {
                  k: "P50 Latency",
                  v: "318ms",
                  c: "fastest tier",
                  icon: Gauge,
                },
                {
                  k: "Tokens Saved",
                  v: "94.1M",
                  c: "this month",
                  icon: Network,
                },
              ].map((m) => (
                <div key={m.k} className="glass rounded-2xl p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs uppercase tracking-wider text-muted-foreground">
                      {m.k}
                    </span>
                    <m.icon className="h-4 w-4 text-cyan" />
                  </div>
                  <div className="mt-2 font-display text-2xl font-bold">
                    {m.v}
                  </div>
                  <div className="text-[11px] text-emerald">{m.c}</div>
                </div>
              ))}
            </div>
            <div className="relative mt-4 grid gap-4 lg:grid-cols-3">
              <div className="glass lg:col-span-2 rounded-2xl p-5">
                <div className="mb-3 flex items-center justify-between text-xs">
                  <span className="font-medium">Latency · last 24h</span>
                  <span className="text-muted-foreground">P50 / P95 / P99</span>
                </div>
                <FakeChart />
              </div>
              <div className="glass rounded-2xl p-5">
                <div className="mb-3 text-xs font-medium">
                  Model Distribution
                </div>
                <div className="space-y-2.5">
                  {[
                    ["Claude 4 Sonnet", 38, "from-cyan to-emerald"],
                    ["GPT-5 mini", 27, "from-violet to-cyan"],
                    ["Gemini 2.5 Flash", 19, "from-emerald to-cyan"],
                    ["Groq Llama 4", 11, "from-cyan to-violet"],
                    ["DeepSeek V3.2", 5, "from-violet to-emerald"],
                  ].map(([n, p, g]) => (
                    <div key={n as string}>
                      <div className="mb-1 flex justify-between text-[11px] text-muted-foreground">
                        <span>{n}</span>
                        <span>{p}%</span>
                      </div>
                      <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                        <div
                          className={`h-full bg-gradient-to-r ${g}`}
                          style={{ width: `${p}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* COMPARISON */}
      <section className="relative px-6 py-32">
        <div className="mx-auto max-w-5xl">
          <SectionHeader
            kicker="VS"
            title="Traditional AI vs LexaraAI"
            sub="The same prompt, a different planet."
          />
          <div className="glass-strong mt-12 overflow-hidden rounded-3xl">
            <div className="grid grid-cols-3 border-b border-border/60 bg-white/[0.03] px-6 py-4 text-xs uppercase tracking-wider text-muted-foreground">
              <div>Capability</div>
              <div className="text-center">Traditional</div>
              <div className="text-center text-gradient">LexaraAI</div>
            </div>
            {comparison.map(([cap, a, b], i) => (
              <div
                key={i}
                className="grid grid-cols-3 items-center border-b border-border/40 px-6 py-4 text-sm last:border-0"
              >
                <div>{cap as string}</div>
                <div className="grid place-items-center">
                  {a ? (
                    <Check className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <X className="h-4 w-4 text-destructive/80" />
                  )}
                </div>
                <div className="grid place-items-center">
                  {b ? (
                    <Check className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <X className="h-4 w-4 text-destructive/80" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="relative px-6 py-32">
        <div className="mx-auto max-w-7xl">
          <SectionHeader
            kicker="Loved by builders"
            title="Teams shipping with LexaraAI"
          />
          <div className="mt-12 grid gap-5 md:grid-cols-3">
            {testimonials.map((t, i) => (
              <motion.div
                key={t.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="glass rounded-3xl p-6"
              >
                <p className="text-sm leading-relaxed text-foreground/90">
                  &ldquo;{t.quote}&rdquo;
                </p>
                <div className="mt-6 flex items-center gap-3">
                  <div className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-cyan to-violet font-display text-xs font-bold text-background">
                    {t.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </div>
                  <div>
                    <div className="text-sm font-semibold">{t.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {t.role}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* PRICING */}
      <section id="pricing" className="relative px-6 py-32">
        <div className="mx-auto max-w-7xl">
          <SectionHeader
            kicker="Pricing"
            title="Intelligence at any scale"
            sub="Pay only for what you route."
          />
          <div className="mt-16 grid gap-5 md:grid-cols-3">
            {plans.map((p) => (
              <div
                key={p.name}
                className={`relative rounded-3xl p-7 ${p.highlight ? "glass-strong glow-cyan ring-1 ring-cyan/40" : "glass"}`}
              >
                {p.highlight && (
                  <div className="absolute inset-x-0 -top-3 mx-auto w-fit rounded-full bg-gradient-to-r from-cyan to-violet px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-background">
                    Most Popular
                  </div>
                )}
                <div className="text-xs uppercase tracking-wider text-muted-foreground">
                  {p.tag}
                </div>
                <div className="mt-2 font-display text-2xl font-semibold">
                  {p.name}
                </div>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="font-display text-5xl font-bold">
                    {p.price}
                  </span>
                  {p.price !== "Custom" && (
                    <span className="text-sm text-muted-foreground">/ mo</span>
                  )}
                </div>
                <ul className="mt-6 space-y-2.5 text-sm">
                  {p.features.map((f) => (
                    <li
                      key={f}
                      className="flex items-center gap-2 text-foreground/85"
                    >
                      <Check className="h-4 w-4 text-cyan" /> {f}
                    </li>
                  ))}
                </ul>
                <button
                  className={`mt-8 w-full rounded-full px-4 py-2.5 text-sm font-semibold transition ${
                    p.highlight
                      ? "bg-gradient-to-r from-cyan to-violet text-background hover:opacity-90"
                      : "border border-border bg-white/5 text-foreground hover:bg-white/10"
                  }`}
                >
                  {p.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="relative px-6 py-40 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <Lightfall
            colors={["#A6C8FF", "#5227FF", "#FF9FFC"]}
            backgroundColor="#0A29FF"
            speed={1.1}
            streakCount={3}
            streakWidth={0.2}
            streakLength={1.4}
            glow={2}
            density={0.6}
            twinkle={0.2}
            zoom={2}
            backgroundGlow={0.7}
            opacity={1}
            mouseInteraction={false}
            mouseStrength={0.9}
            mouseRadius={0.5}
            className="absolute inset-0 z-0"
          />
        </div>
        <div className="relative mx-auto max-w-4xl text-center">
          <h2 className="font-display text-5xl font-bold leading-[1.05] tracking-tight md:text-7xl">
            Stop overpaying for{" "}
            <span className="text-gradient">intelligence</span>
          </h2>
          <p className="mx-auto mt-6 max-w-xl text-lg text-muted-foreground">
            Route smarter. Scale faster. Spend less.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-3">
            <Link
              href="/chat"
              className="rounded-full bg-gradient-to-r from-cyan to-violet px-8 py-3.5 text-sm font-semibold text-background glow-cyan"
            >
              Start Free
            </Link>
            <button className="glass rounded-full px-8 py-3.5 text-sm font-medium">
              Book Demo
            </button>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="relative border-t border-border/50 px-6 py-12">
        <div className="mx-auto grid max-w-7xl gap-8 md:grid-cols-5">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2">
              <div className="grid h-8 w-8 place-items-center rounded-lg bg-linear-to-br from-cyan to-violet">
                <Zap className="h-4 w-4 text-background" strokeWidth={2.5} />
              </div>
              <span className="font-display text-lg font-semibold">
                Lexara<span className="text-gradient">AI</span>
              </span>
            </div>
            <p className="mt-3 max-w-xs text-sm text-muted-foreground">
              One gateway. Infinite intelligence. Built for teams scaling AI in
              production.
            </p>
          </div>
          {[
            ["Product", ["Routing", "Analytics", "Pricing", "Changelog"]],
            ["Developers", ["Docs", "API", "GitHub", "Status"]],
            ["Company", ["About", "Blog", "Careers", "Contact"]],
          ].map(([h, items]) => (
            <div key={h as string}>
              <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {h}
              </div>
              <ul className="space-y-2 text-sm">
                {(items as string[]).map((it) => (
                  <li key={it}>
                    <a
                      href="#"
                      className="text-foreground/80 hover:text-foreground"
                    >
                      {it}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mx-auto mt-10 flex max-w-7xl items-center justify-between border-t border-border/40 pt-6 text-xs text-muted-foreground">
          <span>© 2035 LexaraAI · One Gateway. Infinite Intelligence.</span>
          <span className="font-mono">v2.4.0 · 99.99% uptime</span>
        </div>
      </footer>
    </div>
  );
}

function SectionHeader({
  kicker,
  title,
  sub,
}: {
  kicker: string;
  title: string;
  sub?: string;
}) {
  return (
    <div className="mx-auto max-w-3xl text-center">
      <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-white/5 px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-cyan">
        {kicker}
      </div>
      <h2 className="mt-4 font-display text-4xl font-bold leading-tight tracking-tight md:text-5xl">
        {title}
      </h2>
      {sub && (
        <p className="mt-4 text-base text-muted-foreground md:text-lg">{sub}</p>
      )}
    </div>
  );
}

function FakeChart() {
  const data = Array.from(
    { length: 40 },
    (_, i) => 30 + Math.sin(i / 3) * 12 + (Math.abs(Math.sin(i * 9.13)) % 1) * 14,
  );
  const max = Math.max(...data);
  const pts = data
    .map(
      (v, i) =>
        `${((i / (data.length - 1)) * 100).toFixed(4)},${(100 - (v / max) * 90).toFixed(4)}`,
    )
    .join(" ");
  const pts2 = data
    .map(
      (v, i) =>
        `${((i / (data.length - 1)) * 100).toFixed(4)},${(100 - ((v * 0.6) / max) * 90).toFixed(4)}`,
    )
    .join(" ");
  return (
    <svg
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      className="h-40 w-full"
    >
      <defs>
        <linearGradient id="fill" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="oklch(0.85 0.16 200)" stopOpacity="0.5" />
          <stop offset="1" stopColor="oklch(0.85 0.16 200)" stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={`0,100 ${pts} 100,100`} fill="url(#fill)" />
      <polyline
        points={pts}
        fill="none"
        stroke="oklch(0.85 0.16 200)"
        strokeWidth="0.8"
      />
      <polyline
        points={pts2}
        fill="none"
        stroke="oklch(0.7 0.22 290)"
        strokeWidth="0.6"
        strokeDasharray="2 2"
      />
    </svg>
  );
}

function SavingsCalculator() {
  const [reqs, setReqs] = useState(500_000);
  const [tokens, setTokens] = useState(1200);
  const baselineCostPer1k = 0.012;
  const lexaraCostPer1k = baselineCostPer1k * 0.13;
  const without = ((reqs * tokens) / 1000) * baselineCostPer1k;
  const withL = ((reqs * tokens) / 1000) * lexaraCostPer1k;
  const savings = without - withL;
  const efficiency = Math.min(99, Math.round((1 - withL / without) * 100));

  return (
    <section id="savings" className="relative px-6 py-32">
      <div className="mx-auto max-w-7xl">
        <SectionHeader
          kicker="Calculator"
          title="See your savings in real time"
          sub="A holographic estimator for your actual workload."
        />
        <div className="glass-strong mt-16 grid gap-6 rounded-3xl p-6 md:p-10 lg:grid-cols-2">
          <div className="space-y-6">
            <Slider
              label="Monthly Requests"
              value={reqs}
              min={10_000}
              max={5_000_000}
              step={10_000}
              format={(v) => v.toLocaleString()}
              onChange={setReqs}
            />
            <Slider
              label="Avg Tokens / Request"
              value={tokens}
              min={100}
              max={8000}
              step={50}
              format={(v) => v.toLocaleString()}
              onChange={setTokens}
            />
            <div className="glass flex items-center justify-between rounded-2xl p-4">
              <div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground">
                  Efficiency Score
                </div>
                <div className="mt-1 font-display text-3xl font-bold text-gradient">
                  {efficiency}%
                </div>
              </div>
              <div className="relative h-16 w-16">
                <svg viewBox="0 0 36 36" className="h-full w-full -rotate-90">
                  <circle
                    cx="18"
                    cy="18"
                    r="15"
                    fill="none"
                    stroke="oklch(1 0 0 / 0.08)"
                    strokeWidth="3"
                  />
                  <circle
                    cx="18"
                    cy="18"
                    r="15"
                    fill="none"
                    stroke="url(#gg)"
                    strokeWidth="3"
                    strokeDasharray={`${efficiency * 0.94} 100`}
                    strokeLinecap="round"
                  />
                  <defs>
                    <linearGradient id="gg">
                      <stop stopColor="oklch(0.85 0.16 200)" />
                      <stop offset="1" stopColor="oklch(0.7 0.22 290)" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
          </div>
          <div className="grid gap-4">
            <Metric
              label="Without LexaraAI"
              value={`$${without.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
              dim
            />
            <Metric
              label="With LexaraAI"
              value={`$${withL.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
              accent
            />
            <div className="glass-strong relative overflow-hidden rounded-2xl p-6">
              <div className="absolute -inset-px rounded-2xl bg-gradient-to-r from-cyan/20 to-violet/20 opacity-50 blur-2xl" />
              <div className="relative">
                <div className="text-xs uppercase tracking-wider text-muted-foreground">
                  You save
                </div>
                <div className="mt-2 font-display text-5xl font-bold text-gradient">
                  $
                  {savings.toLocaleString(undefined, {
                    maximumFractionDigits: 0,
                  })}
                </div>
                <div className="mt-1 text-xs text-muted-foreground">
                  per month, automatically.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  format,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  format: (v: number) => string;
  onChange: (v: number) => void;
}) {
  return (
    <div>
      <div className="mb-2 flex items-baseline justify-between">
        <label className="text-sm text-muted-foreground">{label}</label>
        <span className="font-display text-xl font-semibold text-gradient">
          {format(value)}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-[oklch(0.78_0.17_210)]"
      />
    </div>
  );
}

function Metric({
  label,
  value,
  dim,
  accent,
}: {
  label: string;
  value: string;
  dim?: boolean;
  accent?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl p-5 ${dim ? "glass opacity-70" : accent ? "glass-strong ring-1 ring-cyan/30" : "glass"}`}
    >
      <div className="text-xs uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
      <div
        className={`mt-2 font-display text-3xl font-bold ${accent ? "text-gradient" : "text-foreground"}`}
      >
        {value}
      </div>
    </div>
  );
}
