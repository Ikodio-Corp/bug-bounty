'use client';

import { motion } from 'framer-motion';
import { Bug, Shield, Lock, Unlock, AlertTriangle } from 'lucide-react';

const icons = [
  { Icon: Bug, x: 20, y: 30, delay: 0 },
  { Icon: Shield, x: 80, y: 50, delay: 0.2 },
  { Icon: Lock, x: 50, y: 80, delay: 0.4 },
  { Icon: AlertTriangle, x: 10, y: 70, delay: 0.6 },
  { Icon: Unlock, x: 90, y: 20, delay: 0.8 },
];

export function FloatingElements() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {icons.map(({ Icon, x, y, delay }, index) => (
        <motion.div
          key={index}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ 
            scale: 1, 
            opacity: 0.3,
            y: [0, -20, 0],
            rotate: [0, 10, -10, 0]
          }}
          transition={{
            scale: { duration: 0.5, delay },
            opacity: { duration: 0.5, delay },
            y: { duration: 3, repeat: Infinity, delay: delay * 2 },
            rotate: { duration: 4, repeat: Infinity, delay: delay * 1.5 }
          }}
          style={{
            position: 'absolute',
            left: `${x}%`,
            top: `${y}%`,
          }}
          className="text-white"
        >
          <Icon size={32} />
        </motion.div>
      ))}
    </div>
  );
}
