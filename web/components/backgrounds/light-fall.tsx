"use client";

import React, { useEffect, useRef } from "react";

interface LightStream {
  x: number;
  y: number;
  length: number;
  speed: number;
  opacity: number;
  width: number;
  color: string;
}

export default function LightFall() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    // Color choices matching the futuristic theme
    const colors = [
      "rgba(147, 51, 234, ",  // Purple
      "rgba(59, 130, 246, ",  // Blue
      "rgba(16, 185, 129, ",  // Emerald
      "rgba(6, 182, 212, ",   // Cyan
      "rgba(244, 63, 94, "    // Rose
    ];

    const streams: LightStream[] = [];
    const streamCount = Math.floor((width / 1920) * 80) + 20;

    const createStream = (isInitial = false): LightStream => {
      const x = Math.random() * width;
      const y = isInitial ? Math.random() * height : -200;
      const length = Math.random() * 150 + 80;
      const speed = Math.random() * 3 + 1.5;
      const opacity = Math.random() * 0.4 + 0.1;
      const widthStream = Math.random() * 1.5 + 0.5;
      const color = colors[Math.floor(Math.random() * colors.length)];

      return { x, y, length, speed, opacity, width: widthStream, color };
    };

    // Initialize streams
    for (let i = 0; i < streamCount; i++) {
      streams.push(createStream(true));
    }

    // Light spots for soft ambient glow
    const glowSpots = [
      { x: width * 0.2, y: height * 0.3, radius: width * 0.35, color: "rgba(147, 51, 234, 0.04)" },
      { x: width * 0.8, y: height * 0.7, radius: width * 0.4, color: "rgba(59, 130, 246, 0.03)" },
      { x: width * 0.5, y: height * 0.5, radius: width * 0.3, color: "rgba(6, 182, 212, 0.03)" }
    ];

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      
      // Update glow spots on resize
      glowSpots[0].radius = width * 0.35;
      glowSpots[1].radius = width * 0.4;
      glowSpots[2].radius = width * 0.3;
    };

    window.addEventListener("resize", handleResize);

    const animate = () => {
      // Create a dark backdrop base with absolute transparency so globals.css background shows
      ctx.clearRect(0, 0, width, height);

      // Draw soft ambient glow spots (moving slightly)
      const time = Date.now() * 0.0005;
      glowSpots.forEach((spot, idx) => {
        const oscX = Math.sin(time + idx) * 30;
        const oscY = Math.cos(time - idx) * 30;
        const grad = ctx.createRadialGradient(
          spot.x + oscX, spot.y + oscY, 0,
          spot.x + oscX, spot.y + oscY, spot.radius
        );
        grad.addColorStop(0, spot.color);
        grad.addColorStop(1, "rgba(0, 0, 0, 0)");
        
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, width, height);
      });

      // Draw flowing streams
      streams.forEach((stream, idx) => {
        stream.y += stream.speed;

        // Draw the stream trail
        const gradient = ctx.createLinearGradient(
          stream.x,
          stream.y,
          stream.x,
          stream.y + stream.length
        );
        gradient.addColorStop(0, "rgba(255, 255, 255, 0)");
        gradient.addColorStop(0.7, `${stream.color}${stream.opacity})`);
        gradient.addColorStop(1, "rgba(255, 255, 255, 0)");

        ctx.strokeStyle = gradient;
        ctx.lineWidth = stream.width;
        ctx.beginPath();
        ctx.moveTo(stream.x, stream.y);
        ctx.lineTo(stream.x, stream.y + stream.length);
        ctx.stroke();

        // Add a tiny glowing tip
        ctx.fillStyle = `rgba(255, 255, 255, ${stream.opacity * 1.5})`;
        ctx.beginPath();
        ctx.arc(stream.x, stream.y + stream.length * 0.85, stream.width * 1.2, 0, Math.PI * 2);
        ctx.fill();

        // Reset if offscreen
        if (stream.y > height) {
          streams[idx] = createStream(false);
        }
      });

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
