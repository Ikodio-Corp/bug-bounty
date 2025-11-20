'use client';

import { useMobile } from '@/hooks/useMobile';

interface MobileKeyboardShortcut {
  key: string;
  description: string;
  action: () => void;
}

interface MobileKeyboardProps {
  shortcuts: MobileKeyboardShortcut[];
}

export default function MobileKeyboard({ shortcuts }: MobileKeyboardProps) {
  const { isMobile } = useMobile();

  if (!isMobile) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800 p-2 flex overflow-x-auto gap-2 z-40">
      {shortcuts.map((shortcut, index) => (
        <button
          key={index}
          onClick={shortcut.action}
          className="
            flex-shrink-0 px-4 py-2 bg-gray-800 hover:bg-gray-700 
            rounded text-white text-sm font-medium
            min-w-[60px] text-center
            active:bg-gray-600 transition-colors
          "
          title={shortcut.description}
        >
          {shortcut.key}
        </button>
      ))}
    </div>
  );
}
