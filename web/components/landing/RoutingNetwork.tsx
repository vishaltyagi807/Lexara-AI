"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

const providers = [
  { name: "OpenAI", angle: 0 },
  { name: "Claude", angle: 60 },
  { name: "Gemini", angle: 120 },
  { name: "Groq", angle: 180 },
  { name: "DeepSeek", angle: 240 },
  { name: "Mistral", angle: 300 },
];

export function RoutingNetwork() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  const cx = 200;
  const cy = 200;
  const r = 140;

  return (
    <div className="relative mx-auto aspect-square w-full max-w-md">
      <div className="absolute inset-0 animate-pulse-glow rounded-full bg-linear-to-br from-cyan/30 via-violet/20 to-transparent blur-3xl" />
      <svg viewBox="0 0 400 400" className="relative h-full w-full">
        <defs>
          <linearGradient id="beam" x1="0" x2="1">
            <stop offset="0" stopColor="oklch(0.85 0.16 200)" stopOpacity="0" />
            <stop offset="0.5" stopColor="oklch(0.85 0.16 200)" stopOpacity="0.9" />
            <stop offset="1" stopColor="oklch(0.7 0.22 290)" stopOpacity="0" />
          </linearGradient>
          <radialGradient id="core">
            <stop offset="0" stopColor="oklch(0.95 0.05 200)" />
            <stop offset="1" stopColor="oklch(0.5 0.2 260)" />
          </radialGradient>
        </defs>

        {/* concentric rings */}
        {[60, 100, 140, 180].map((rr) => (
          <circle key={rr} cx={cx} cy={cy} r={rr} fill="none" stroke="oklch(1 0 0 / 0.06)" />
        ))}

        {/* beams - render only after mounting to ensure same initial layout during SSR */}
        {mounted &&
          providers.map((p, i) => {
            const a = (p.angle * Math.PI) / 180;
            const x = cx + Math.cos(a) * r;
            const y = cy + Math.sin(a) * r;
            return (
              <g key={p.name}>
                <line
                  x1={cx}
                  y1={cy}
                  x2={Number(x.toFixed(4))}
                  y2={Number(y.toFixed(4))}
                  stroke="url(#beam)"
                  strokeWidth="1.5"
                  strokeDasharray="6 6"
                  style={{ animation: `beam-flow 3s linear infinite`, animationDelay: `${i * 0.2}s` }}
                />
              </g>
            );
          })}

        {/* center core */}
        <circle cx={cx} cy={cy} r="32" fill="url(#core)" opacity="0.9" />
        <circle cx={cx} cy={cy} r="42" fill="none" stroke="oklch(0.85 0.16 200 / 0.5)" strokeWidth="1">
          <animate attributeName="r" values="42;58;42" dur="3s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.6;0;0.6" dur="3s" repeatCount="indefinite" />
        </circle>
        <text x={cx} y={cy + 4} textAnchor="middle" className="fill-background font-display" fontSize="11" fontWeight="700">
          LEXARA
        </text>
      </svg>

      {/* provider nodes - render only after mounting to ensure same initial layout during SSR */}
      {mounted &&
        providers.map((p, i) => {
          const a = (p.angle * Math.PI) / 180;
          const leftPercent = 50 + Math.cos(a) * 42;
          const topPercent = 50 + Math.sin(a) * 42;
          return (
            <motion.div
              key={p.name}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 * i, duration: 0.5 }}
              className="glass absolute flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-mono"
              style={{
                left: `calc(${leftPercent.toFixed(4)}% - 40px)`,
                top: `calc(${topPercent.toFixed(4)}% - 14px)`,
              }}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-emerald shadow-[0_0_8px_oklch(0.78_0.17_165)]" />
              {p.name}
            </motion.div>
          );
        })}
    </div>
  );
}

