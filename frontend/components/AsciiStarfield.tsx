'use client';

import { useEffect, useRef, useCallback } from 'react';

interface Star {
  x: number;
  y: number;
  z: number;
  char: string;
  opacity: number;
}

const ASCII_CHARS = ['*', '.', '+', '·', '°', '×', ':', '○', '◦', '∙', '⋅', '•'];
const TECH_CHARS = ['0', '1', '<', '>', '/', '\\', '{', '}', '[', ']', '|', '-', '=', '_'];

interface AsciiStarfieldProps {
  starCount?: number;
  speed?: number;
  color?: string;
  glowColor?: string;
  showTechChars?: boolean;
  opacity?: number;
}

export function AsciiStarfield({
  starCount = 200,
  speed = 0.5,
  color = '#00ff88',
  glowColor = '#00ff8844',
  showTechChars = true,
  opacity = 0.6,
}: AsciiStarfieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const starsRef = useRef<Star[]>([]);
  const animationRef = useRef<number>();
  const mouseRef = useRef({ x: 0, y: 0 });

  const getRandomChar = useCallback(() => {
    const chars = showTechChars
      ? [...ASCII_CHARS, ...TECH_CHARS]
      : ASCII_CHARS;
    return chars[Math.floor(Math.random() * chars.length)];
  }, [showTechChars]);

  const initStars = useCallback((width: number, height: number) => {
    const stars: Star[] = [];
    for (let i = 0; i < starCount; i++) {
      stars.push({
        x: Math.random() * width - width / 2,
        y: Math.random() * height - height / 2,
        z: Math.random() * 1000,
        char: getRandomChar(),
        opacity: Math.random() * 0.5 + 0.5,
      });
    }
    starsRef.current = stars;
  }, [starCount, getRandomChar]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initStars(canvas.width, canvas.height);
    };

    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = {
        x: (e.clientX / window.innerWidth - 0.5) * 2,
        y: (e.clientY / window.innerHeight - 0.5) * 2,
      };
    };

    resize();
    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', handleMouseMove);

    const animate = () => {
      if (!ctx || !canvas) return;

      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      starsRef.current.forEach((star) => {
        star.z -= speed * 2;

        if (star.z <= 0) {
          star.x = Math.random() * canvas.width - centerX;
          star.y = Math.random() * canvas.height - centerY;
          star.z = 1000;
          star.char = getRandomChar();
          star.opacity = Math.random() * 0.5 + 0.5;
        }

        const perspective = 300 / star.z;
        const screenX = star.x * perspective + centerX + mouseRef.current.x * 50;
        const screenY = star.y * perspective + centerY + mouseRef.current.y * 50;

        if (screenX < 0 || screenX > canvas.width || screenY < 0 || screenY > canvas.height) {
          return;
        }

        const size = Math.max(8, 24 * perspective);
        const alphaBase = Math.min(1, (1000 - star.z) / 1000);
        const alpha = alphaBase * star.opacity * opacity;

        ctx.shadowBlur = 8;
        ctx.shadowColor = glowColor;

        ctx.font = `${size}px "Fira Code", "JetBrains Mono", "Consolas", monospace`;
        ctx.fillStyle = color;
        ctx.globalAlpha = alpha;
        ctx.fillText(star.char, screenX, screenY);

        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1;
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouseMove);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [speed, color, glowColor, opacity, initStars, getRandomChar]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
    />
  );
}
