"use client";

import React, { useEffect, useRef } from "react";

interface Ray {
  angle: number;
  width: number;
  speed: number;
  maxOpacity: number;
  length: number;
  color: string;
}

export default function LightRays() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    // Volumetric rays configuration
    const rayCount = 6;
    const rays: Ray[] = [];

    const colors = [
      "rgba(147, 51, 234, ", // Purple
      "rgba(59, 130, 246, ", // Blue
      "rgba(6, 182, 212, ",  // Cyan
    ];

    for (let i = 0; i < rayCount; i++) {
      rays.push({
        angle: (Math.PI / rayCount) * i + Math.random() * 0.3,
        width: Math.random() * 0.15 + 0.05, // width in radians
        speed: (Math.random() * 0.04 + 0.02) * (Math.random() > 0.5 ? 1 : -1) * 0.05,
        maxOpacity: Math.random() * 0.06 + 0.03,
        length: Math.max(width, height) * 1.5,
        color: colors[i % colors.length],
      });
    }

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      rays.forEach((ray) => {
        ray.length = Math.max(width, height) * 1.5;
      });
    };

    window.addEventListener("resize", handleResize);

    // Source of rays (top center)
    const sourceX = width / 2;
    const sourceY = -50;

    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw volumetric rays
      const time = Date.now() * 0.0002;
      
      rays.forEach((ray) => {
        // Update ray angle (oscillating)
        const currentAngle = ray.angle + Math.sin(time * ray.speed * 10) * 0.2;
        const currentWidth = ray.width + Math.sin(time + ray.speed) * 0.02;
        const currentOpacity = ray.maxOpacity * (0.8 + Math.sin(time * 2 + ray.angle) * 0.2);

        // Path of ray (cone)
        const leftAngle = currentAngle - currentWidth / 2;
        const rightAngle = currentAngle + currentWidth / 2;

        const x1 = sourceX + Math.cos(leftAngle) * ray.length;
        const y1 = sourceY + Math.sin(leftAngle) * ray.length;
        const x2 = sourceX + Math.cos(rightAngle) * ray.length;
        const y2 = sourceY + Math.sin(rightAngle) * ray.length;

        const grad = ctx.createRadialGradient(
          sourceX, sourceY, 0,
          sourceX, sourceY, ray.length * 0.8
        );
        grad.addColorStop(0, `${ray.color}${currentOpacity})`);
        grad.addColorStop(0.3, `${ray.color}${currentOpacity * 0.6})`);
        grad.addColorStop(1, "rgba(0, 0, 0, 0)");

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.moveTo(sourceX, sourceY);
        ctx.lineTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.closePath();
        ctx.fill();
      });

      // Ambient top-center light source glow
      const sourceGrad = ctx.createRadialGradient(
        sourceX, sourceY, 0,
        sourceX, sourceY, Math.min(width, height) * 0.5
      );
      sourceGrad.addColorStop(0, "rgba(99, 102, 241, 0.06)");
      sourceGrad.addColorStop(0.5, "rgba(168, 85, 247, 0.02)");
      sourceGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = sourceGrad;
      ctx.fillRect(0, 0, width, height);

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none z-0"
    />
  );
}
