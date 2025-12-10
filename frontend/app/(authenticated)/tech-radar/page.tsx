'use client';

import { useState, useEffect } from 'react';
import { Radar, Zap, FlaskConical, Search, PauseCircle, Sparkles } from 'lucide-react';

const categories = [
  { name: 'ADOPT', color: 'from-green-400 to-emerald-500', icon: Zap, desc: 'Proven technologies ready for production' },
  { name: 'TRIAL', color: 'from-blue-400 to-cyan-500', icon: FlaskConical, desc: 'Worth pursuing in pilot projects' },
  { name: 'ASSESS', color: 'from-amber-400 to-orange-500', icon: Search, desc: 'Promising technologies to explore' },
  { name: 'HOLD', color: 'from-red-400 to-rose-500', icon: PauseCircle, desc: 'Proceed with caution' },
];

export default function TechRadarPage() {
  const [glitchText, setGlitchText] = useState('TECH RADAR');
  const [scanLine, setScanLine] = useState(0);

  useEffect(() => {
    const glitchChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    const interval = setInterval(() => {
      if (Math.random() > 0.95) {
        const text = 'TECH RADAR'.split('').map(char =>
          Math.random() > 0.7 ? glitchChars[Math.floor(Math.random() * glitchChars.length)] : char
        ).join('');
        setGlitchText(text);
        setTimeout(() => setGlitchText('TECH RADAR'), 100);
      }
    }, 150);

    const scanInterval = setInterval(() => {
      setScanLine(prev => (prev + 1) % 100);
    }, 50);

    return () => {
      clearInterval(interval);
      clearInterval(scanInterval);
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 relative overflow-hidden">
      {/* Retro CRT scanlines overlay */}
      <div className="absolute inset-0 pointer-events-none z-10">
        <div className="absolute inset-0 bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(0,0,0,0.1)_2px,rgba(0,0,0,0.1)_4px)]" />
        <div
          className="absolute left-0 right-0 h-1 bg-gradient-to-b from-cyan-400/20 to-transparent"
          style={{ top: `${scanLine}%` }}
        />
      </div>

      {/* Animated grid background */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />

      {/* Glowing orb in background */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" />

      <div className="relative z-20 p-4 lg:p-8 max-w-6xl mx-auto">
        {/* Header with retro styling */}
        <div className="text-center mb-16 pt-8">
          <div className="inline-flex items-center gap-4 mb-6">
            <div className="relative">
              <Radar className="h-16 w-16 text-cyan-400 animate-spin" style={{ animationDuration: '8s' }} />
              <div className="absolute inset-0 h-16 w-16 border-2 border-cyan-400/50 rounded-full animate-ping" />
            </div>
          </div>

          <h1 className="text-6xl font-mono font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 mb-4 tracking-wider">
            {glitchText}
          </h1>

          <div className="flex items-center justify-center gap-3 mb-8">
            <div className="h-px w-16 bg-gradient-to-r from-transparent to-cyan-400" />
            <span className="text-cyan-400 font-mono text-sm tracking-widest uppercase flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Coming Soon
              <Sparkles className="h-4 w-4" />
            </span>
            <div className="h-px w-16 bg-gradient-to-l from-transparent to-cyan-400" />
          </div>

          <p className="text-slate-400 text-lg max-w-2xl mx-auto font-light">
            A technology tracking system to monitor and evaluate the tools and frameworks
            powering our AI agent ecosystem.
          </p>
        </div>

        {/* Feature preview cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-16">
          {categories.map((cat, i) => {
            const Icon = cat.icon;
            return (
              <div
                key={cat.name}
                className="group relative bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6 hover:border-cyan-500/50 transition-all duration-300"
                style={{ animationDelay: `${i * 150}ms` }}
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${cat.color} opacity-0 group-hover:opacity-5 rounded-xl transition-opacity`} />
                <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${cat.color} mb-4`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="font-mono font-bold text-white mb-2 tracking-wide">{cat.name}</h3>
                <p className="text-slate-500 text-sm">{cat.desc}</p>
              </div>
            );
          })}
        </div>

        {/* Coming soon terminal */}
        <div className="max-w-2xl mx-auto">
          <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden shadow-2xl shadow-cyan-500/10">
            <div className="flex items-center gap-2 px-4 py-3 bg-slate-900 border-b border-slate-800">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="ml-4 text-slate-500 font-mono text-sm">tech-radar.exe</span>
            </div>
            <div className="p-6 font-mono text-sm">
              <div className="text-green-400 mb-2">$ initializing tech_radar_module...</div>
              <div className="text-slate-500 mb-2">[████████████████████████████████] 100%</div>
              <div className="text-cyan-400 mb-2">✓ Database schema configured</div>
              <div className="text-cyan-400 mb-2">✓ 4-category grid layout ready</div>
              <div className="text-cyan-400 mb-2">✓ Tool tracking endpoints prepared</div>
              <div className="text-yellow-400 mb-4">⚡ Awaiting deployment...</div>
              <div className="text-slate-400">
                <span className="text-purple-400">features</span> = [
                <br />
                <span className="ml-4 text-green-400">&quot;Interactive radar visualization&quot;</span>,
                <br />
                <span className="ml-4 text-green-400">&quot;Technology lifecycle tracking&quot;</span>,
                <br />
                <span className="ml-4 text-green-400">&quot;Team adoption metrics&quot;</span>,
                <br />
                <span className="ml-4 text-green-400">&quot;External resource links&quot;</span>
                <br />
                ]
              </div>
              <div className="mt-4 flex items-center text-slate-400">
                <span className="text-cyan-400 mr-2">$</span>
                <span className="animate-pulse">_</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer decoration */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 text-slate-600 font-mono text-xs">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
            SYSTEM STATUS: DEVELOPMENT IN PROGRESS
          </div>
        </div>
      </div>
    </div>
  );
}
