"use client";

import React from "react";

export function LightFall() {
  // Pure CSS aurora + falling light streams. Performant, dark-optimized.
  const streams = Array.from({ length: 14 });
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {/* Base radial aurora */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(60% 50% at 20% 10%, oklch(0.45 0.2 250 / 0.35), transparent 60%), radial-gradient(50% 60% at 85% 20%, oklch(0.55 0.22 290 / 0.3), transparent 60%), radial-gradient(80% 60% at 50% 110%, oklch(0.5 0.2 200 / 0.28), transparent 60%)",
        }}
      />
      {/* Grid */}
      <div className="absolute inset-0 bg-grid opacity-40 [mask-image:radial-gradient(ellipse_at_center,black_30%,transparent_75%)]" />

      {/* Falling light streams */}
      <div className="absolute -inset-x-20 -top-40 -bottom-20">
        {streams.map((_, i) => {
          const left = (i / streams.length) * 100;
          const delay = (i * 0.7) % 6;
          const dur = 8 + (i % 5) * 1.4;
          const hue = i % 3 === 0 ? 200 : i % 3 === 1 ? 250 : 290;
          return (
            <span
              key={i}
              className="absolute top-0 block"
              style={{
                left: `${left}%`,
                width: 2,
                height: "120%",
                background: `linear-gradient(to bottom, transparent, oklch(0.85 0.18 ${hue} / 0.85), transparent)`,
                filter: "blur(1px)",
                animation: `light-fall ${dur}s linear ${delay}s infinite`,
                opacity: 0,
              }}
            />
          );
        })}
      </div>

      {/* Soft top glow */}
      <div
        className="absolute inset-x-0 top-0 h-72"
        style={{
          background:
            "linear-gradient(to bottom, oklch(0.7 0.2 230 / 0.18), transparent)",
        }}
      />
      {/* Vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,oklch(0.05_0.02_260)_95%)]" />
    </div>
  );
}
