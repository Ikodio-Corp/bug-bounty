'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const codeLines = [
  { text: '> Scanning target: example.com', delay: 0 },
  { text: '> Running SQL injection tests... OK', delay: 1000 },
  { text: '> Checking XSS vulnerabilities... FOUND!', delay: 2000, warning: true },
  { text: '> Analyzing authentication flow... OK', delay: 3000 },
  { text: '> [ERROR] Critical vulnerability detected!', delay: 4000, error: true },
  { text: '> CVE-2024-XXXX: Remote Code Execution', delay: 5000, error: true },
  { text: '> Severity: HIGH | CVSS: 9.8', delay: 6000, error: true },
];

export function CodeTerminal() {
  const [visibleLines, setVisibleLines] = useState<number>(0);

  useEffect(() => {
    const timers = codeLines.map((line, index) => 
      setTimeout(() => setVisibleLines(index + 1), line.delay)
    );

    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.8, delay: 0.4 }}
      className="relative bg-gray-900 rounded-lg p-6 shadow-2xl border border-gray-800 overflow-hidden"
    >
      {/* Terminal Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-3 h-3 rounded-full bg-red-500" />
        <div className="w-3 h-3 rounded-full bg-yellow-500" />
        <div className="w-3 h-3 rounded-full bg-green-500" />
        <span className="ml-2 text-gray-400 text-sm font-mono">ikodio-scanner</span>
      </div>

      {/* Terminal Content */}
      <div className="font-mono text-sm space-y-2">
        {codeLines.slice(0, visibleLines).map((line, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className={`${
              line.error 
                ? 'text-white font-bold' 
                : line.warning 
                ? 'text-gray-300' 
                : 'text-white'
            }`}
          >
            {line.text}
          </motion.div>
        ))}
        {visibleLines < codeLines.length && (
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ duration: 0.8, repeat: Infinity }}
            className="inline-block w-2 h-4 bg-white ml-1"
          />
        )}
      </div>
    </motion.div>
  );
}
