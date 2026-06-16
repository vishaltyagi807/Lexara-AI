"use client";

import React, { useState, useEffect } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  SparklesIcon,
  CpuIcon,
  Settings02Icon,
  ActivityIcon,
  DashboardSquare01Icon,
  ArrowRight01Icon,
  HelpCircleIcon
} from "@hugeicons/core-free-icons";

interface ProviderNode {
  id: string;
  name: string;
  model: string;
  costPer1M: number;
  latencyMs: number;
  color: string;
  logoColor: string;
}

const PROVIDERS: ProviderNode[] = [
  { id: "openai", name: "OpenAI", model: "GPT-4o", costPer1M: 5.0, latencyMs: 320, color: "rgba(16, 185, 129, 0.4)", logoColor: "text-emerald-500" },
  { id: "anthropic", name: "Anthropic", model: "Claude 3.5 Sonnet", costPer1M: 15.0, latencyMs: 450, color: "rgba(239, 68, 68, 0.4)", logoColor: "text-rose-500" },
  { id: "gemini", name: "Google Gemini", model: "Gemini 1.5 Pro", costPer1M: 7.0, latencyMs: 380, color: "rgba(59, 130, 246, 0.4)", logoColor: "text-blue-500" },
  { id: "groq", name: "Groq", model: "Llama 3.1 70B", costPer1M: 0.8, latencyMs: 65, color: "rgba(245, 158, 11, 0.4)", logoColor: "text-amber-500" },
  { id: "deepseek", name: "DeepSeek", model: "DeepSeek-V3", costPer1M: 0.28, latencyMs: 190, color: "rgba(6, 182, 212, 0.4)", logoColor: "text-cyan-500" },
  { id: "together", name: "Together AI", model: "Mixtral 8x22B", costPer1M: 0.6, latencyMs: 140, color: "rgba(139, 92, 246, 0.4)", logoColor: "text-purple-500" }
];

interface PromptOption {
  label: string;
  type: string;
  complexity: string;
  bestProviderId: string;
  desc: string;
}

const PROMPTS: PromptOption[] = [
  { label: "Code Debugging & Refactoring", type: "Complex reasoning", complexity: "High", bestProviderId: "anthropic", desc: "Requires deep semantic code intelligence." },
  { label: "Real-time Customer Support", type: "Low latency target", complexity: "Low", bestProviderId: "groq", desc: "Requires sub-100ms response speed." },
  { label: "Summarize 100 Page PDF", type: "High token volume", complexity: "Medium", bestProviderId: "deepseek", desc: "Requires optimal cost-per-token." },
  { label: "General Creative Writing", type: "Standard generation", complexity: "Medium", bestProviderId: "openai", desc: "Requires well-rounded model capabilities." }
];

export default function RoutingNetwork() {
  const [activePrompt, setActivePrompt] = useState<PromptOption>(PROMPTS[0]);
  const [routingStep, setRoutingStep] = useState<string>("idle"); // idle, analyzing, routing, executing, completed
  const [selectedProvider, setSelectedProvider] = useState<ProviderNode | null>(null);
  const [liveMetrics, setLiveMetrics] = useState({ cost: 0.0, latency: 0, savings: 0 });

  useEffect(() => {
    // Whenever prompt changes, simulate the routing sequence
    setRoutingStep("analyzing");
    setSelectedProvider(null);

    const t1 = setTimeout(() => {
      setRoutingStep("routing");
    }, 800);

    const t2 = setTimeout(() => {
      const provider = PROVIDERS.find(p => p.id === activePrompt.bestProviderId) || PROVIDERS[0];
      setSelectedProvider(provider);
      setRoutingStep("executing");
    }, 1600);

    const t3 = setTimeout(() => {
      setRoutingStep("completed");
      const provider = PROVIDERS.find(p => p.id === activePrompt.bestProviderId) || PROVIDERS[0];
      // Simulate savings compared to always using the most expensive premium provider (Anthropic)
      const maxCost = 15.0; // Anthropic base cost
      const actualCost = provider.costPer1M;
      const savingsPct = Math.round(((maxCost - actualCost) / maxCost) * 100);

      setLiveMetrics({
        cost: actualCost,
        latency: provider.latencyMs,
        savings: savingsPct
      });
    }, 2800);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [activePrompt]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center bg-card/40 border border-border/80 p-6 rounded-3xl backdrop-blur-xl shadow-2xl relative overflow-hidden">
      {/* Sci-fi HUD Border Glow */}
      <div className="absolute inset-0 border border-primary/20 pointer-events-none rounded-3xl" />
      
      {/* Interactive Controls Panel */}
      <div className="lg:col-span-5 space-y-6 z-10">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary text-xs font-mono">
            <HugeiconsIcon icon={ActivityIcon} className="w-3.5 h-3.5 animate-pulse" />
            TELEMETRY EMULATOR
          </div>
          <h3 className="text-2xl font-heading font-semibold tracking-tight mt-2 text-foreground">
            Smart Model Selection
          </h3>
          <p className="text-muted-foreground text-sm leading-relaxed">
            Select a target workflow to see LexaraAI analyze, optimize, and dispatch the request to the most efficient provider in real time.
          </p>
        </div>

        <div className="space-y-2">
          {PROMPTS.map((prompt) => (
            <button
              key={prompt.label}
              onClick={() => setActivePrompt(prompt)}
              className={`w-full text-left p-3.5 rounded-xl border transition-all duration-300 relative group flex items-start justify-between gap-4 ${
                activePrompt.label === prompt.label
                  ? "border-primary bg-primary/5 shadow-[0_0_15px_rgba(99,102,241,0.15)]"
                  : "border-border/60 bg-transparent hover:border-border hover:bg-muted/30"
              }`}
            >
              <div className="space-y-1">
                <span className="text-xs font-mono text-primary group-hover:text-primary/80 block">
                  {prompt.type}
                </span>
                <span className="text-sm font-semibold text-foreground group-hover:text-foreground/90 block">
                  {prompt.label}
                </span>
                <span className="text-xs text-muted-foreground block">
                  {prompt.desc}
                </span>
              </div>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                prompt.complexity === "High" 
                  ? "text-rose-400 border-rose-500/20 bg-rose-500/5" 
                  : prompt.complexity === "Medium"
                  ? "text-amber-400 border-amber-500/20 bg-amber-500/5"
                  : "text-emerald-400 border-emerald-500/20 bg-emerald-500/5"
              }`}>
                {prompt.complexity} Priority
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Floating Network Visualization */}
      <div className="lg:col-span-7 flex flex-col items-center justify-center min-h-[420px] relative z-10">
        
        {/* Real-time Status Overlay HUD */}
        <div className="absolute top-0 left-0 right-0 flex justify-between gap-4 px-4 py-2 rounded-xl bg-background/50 border border-border/40 backdrop-blur-md font-mono text-[10px] text-muted-foreground">
          <div>
            PROMPT ENGINE: <span className="text-foreground font-semibold uppercase">{routingStep}</span>
          </div>
          <div>
            ACTIVE TARGET: <span className="text-primary font-semibold uppercase">{selectedProvider ? selectedProvider.name : "SEARCHING"}</span>
          </div>
        </div>

        {/* Network Diagram Viewport */}
        <svg viewBox="0 0 500 400" className="w-full max-w-[460px] h-auto overflow-visible mt-6">
          <defs>
            <filter id="glow-light" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <linearGradient id="gradient-pulse" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0" />
              <stop offset="50%" stopColor="#06b6d4" stopOpacity="1" />
              <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Connectors & Energy Pulses */}
          {PROVIDERS.map((node, index) => {
            // Circle arrangement positions
            const angle = (index * 2 * Math.PI) / PROVIDERS.length - Math.PI / 2;
            const targetX = 250 + 170 * Math.cos(angle);
            const targetY = 200 + 120 * Math.sin(angle);
            const isSelected = selectedProvider?.id === node.id;

            return (
              <g key={node.id}>
                {/* Connecting Line */}
                <line
                  x1="250"
                  y1="200"
                  x2={targetX}
                  y2={targetY}
                  stroke={isSelected ? "#8b5cf6" : "var(--border)"}
                  strokeWidth={isSelected ? 2.5 : 1}
                  strokeOpacity={isSelected ? 0.8 : 0.25}
                  className="transition-all duration-500"
                />

                {/* Animated beam pulse flowing outward */}
                {routingStep === "executing" && isSelected && (
                  <circle r="4" fill="#67e8f9" filter="url(#glow-light)">
                    <animateMotion
                      dur="1s"
                      repeatCount="indefinite"
                      path={`M 250,200 L ${targetX},${targetY}`}
                    />
                  </circle>
                )}
              </g>
            );
          })}

          {/* Surrounding Provider Nodes */}
          {PROVIDERS.map((node, index) => {
            const angle = (index * 2 * Math.PI) / PROVIDERS.length - Math.PI / 2;
            const targetX = 250 + 170 * Math.cos(angle);
            const targetY = 200 + 120 * Math.sin(angle);
            const isSelected = selectedProvider?.id === node.id;

            return (
              <g
                key={node.id}
                className="cursor-pointer group"
                transform={`translate(${targetX}, ${targetY})`}
              >
                {/* Outer Glow ring */}
                <circle
                  r="30"
                  fill="none"
                  stroke={isSelected ? "#a855f7" : "transparent"}
                  strokeWidth="2"
                  filter="url(#glow-light)"
                  className="transition-all duration-500 opacity-60"
                />
                
                {/* Main Node Circle */}
                <circle
                  r="24"
                  fill="var(--card)"
                  stroke={isSelected ? "#8b5cf6" : "var(--border)"}
                  strokeWidth={isSelected ? 2 : 1}
                  className="transition-all duration-300 shadow-md"
                />

                {/* Micro provider indicators */}
                <text
                  textAnchor="middle"
                  y="-32"
                  className="font-sans text-[10px] font-semibold fill-foreground tracking-wide"
                >
                  {node.name}
                </text>
                <text
                  textAnchor="middle"
                  y="4"
                  className="font-mono text-[9px] fill-muted-foreground"
                >
                  {node.model}
                </text>
                
                {/* Provider cost stats tag */}
                <text
                  textAnchor="middle"
                  y="34"
                  className={`font-mono text-[8px] ${isSelected ? "fill-primary font-bold" : "fill-muted-foreground/60"}`}
                >
                  ${node.costPer1M}/1M tkn
                </text>
              </g>
            );
          })}

          {/* LexaraAI Core Center Node */}
          <g transform="translate(250, 200)">
            {/* Pulsing energy rings */}
            <circle
              r="45"
              fill="none"
              stroke="#6366f1"
              strokeWidth="1.5"
              className={`animate-ping opacity-25`}
              style={{ animationDuration: "3s" }}
            />
            <circle
              r="38"
              fill="rgba(99, 102, 241, 0.08)"
              stroke="url(#gradient-pulse)"
              strokeWidth="2"
              className="animate-spin"
              style={{ animationDuration: "10s" }}
            />
            {/* Hexagon/Circle core */}
            <circle
              r="32"
              fill="var(--card)"
              stroke="#6366f1"
              strokeWidth="2"
              filter="url(#glow-light)"
            />
            {/* Core Label */}
            <text
              textAnchor="middle"
              y="-4"
              className="font-sans text-[9px] font-extrabold fill-foreground tracking-widest"
            >
              LEXARA
            </text>
            <text
              textAnchor="middle"
              y="8"
              className="font-sans text-[8px] font-medium fill-primary/80 tracking-wide"
            >
              CORE
            </text>

            {/* Glowing router state icon */}
            <g transform="translate(0, 18) scale(0.5)">
              <foreignObject x="-12" y="-20" width="24" height="24">
                <HugeiconsIcon
                  icon={CpuIcon}
                  className={`w-5 h-5 text-primary ${routingStep === "analyzing" || routingStep === "routing" ? "animate-spin" : ""}`}
                />
              </foreignObject>
            </g>
          </g>
        </svg>

        {/* Real-time Telemetry Stats Widget */}
        <div className="w-full mt-4 bg-muted/30 border border-border/40 rounded-2xl p-4 grid grid-cols-3 gap-2 text-center backdrop-blur-md">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-muted-foreground block">EST. LATENCY</span>
            <span className="text-lg font-mono font-bold text-foreground">
              {routingStep === "completed" ? `${liveMetrics.latency}ms` : "---"}
            </span>
          </div>
          <div className="border-x border-border/40 space-y-1">
            <span className="text-[10px] font-mono text-muted-foreground block">COST/1M TOKENS</span>
            <span className="text-lg font-mono font-bold text-foreground">
              {routingStep === "completed" ? `$${liveMetrics.cost.toFixed(2)}` : "---"}
            </span>
          </div>
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-primary font-semibold block">TOKEN SAVINGS</span>
            <span className="text-lg font-mono font-bold text-emerald-400">
              {routingStep === "completed" ? `${liveMetrics.savings}%` : "---"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
