"use client";

import React from "react";

export function LightRays() {
  const rays = Array.from({ length: 18 });
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(60% 80% at 50% -10%, oklch(0.5 0.22 250 / 0.45), transparent 60%), radial-gradient(50% 60% at 80% 100%, oklch(0.5 0.2 290 / 0.25), transparent 60%)",
        }}
      />
      <div className="absolute left-1/2 top-[-20%] h-[140%] w-[140%] -translate-x-1/2 origin-top">
        {rays.map((_, i) => {
          const angle = (i / rays.length) * 60 - 30;
          const dur = 10 + (i % 5) * 2;
          return (
            <span
              key={i}
              className="absolute left-1/2 top-0 block origin-top"
              style={{
                transform: `translateX(-50%) rotate(${angle}deg)`,
                width: 2,
                height: "100%",
                background:
                  "linear-gradient(to bottom, oklch(0.9 0.15 220 / 0.55), transparent 70%)",
                filter: "blur(2px)",
                animation: `pulse-glow ${dur}s ease-in-out ${i * 0.3}s infinite`,
              }}
            />
          );
        })}
      </div>
      <div className="absolute inset-0 bg-grid opacity-25 [mask-image:radial-gradient(ellipse_at_center,black_20%,transparent_75%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_45%,oklch(0.05_0.02_260)_100%)]" />
    </div>
  );
}
