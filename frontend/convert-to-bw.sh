#!/bin/bash

# Script to convert all colors to black and white in the frontend

echo "Converting all colors to black and white..."

# Find all TSX files
find app components -name "*.tsx" -type f | while read file; do
  echo "Processing: $file"
  
  # Backup original file
  cp "$file" "$file.backup"
  
  # Replace all color gradients with grayscale
  sed -i '' 's/from-purple-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-purple-[0-9]\+/to-gray-900/g' "$file"
  sed -i '' 's/via-purple-[0-9]\+/via-gray-800/g' "$file"
  
  sed -i '' 's/from-blue-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-blue-[0-9]\+/to-gray-900/g' "$file"
  sed -i '' 's/via-blue-[0-9]\+/via-gray-800/g' "$file"
  
  sed -i '' 's/from-green-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-green-[0-9]\+/to-gray-900/g' "$file"
  sed -i '' 's/via-green-[0-9]\+/via-gray-800/g' "$file"
  
  sed -i '' 's/from-red-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-red-[0-9]\+/to-gray-900/g' "$file"
  sed -i '' 's/via-red-[0-9]\+/via-gray-800/g' "$file"
  
  sed -i '' 's/from-yellow-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-yellow-[0-9]\+/to-gray-900/g' "$file"
  
  sed -i '' 's/from-pink-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-pink-[0-9]\+/to-gray-900/g' "$file"
  
  sed -i '' 's/from-indigo-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-indigo-[0-9]\+/to-gray-900/g' "$file"
  sed -i '' 's/via-indigo-[0-9]\+/via-gray-800/g' "$file"
  
  sed -i '' 's/from-orange-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-orange-[0-9]\+/to-gray-900/g' "$file"
  sed -i '' 's/via-orange-[0-9]\+/via-gray-800/g' "$file"
  
  sed -i '' 's/from-teal-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-teal-[0-9]\+/to-gray-900/g' "$file"
  
  sed -i '' 's/from-cyan-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-cyan-[0-9]\+/to-gray-900/g' "$file"
  sed -i '' 's/via-cyan-[0-9]\+/via-gray-800/g' "$file"
  
  sed -i '' 's/from-emerald-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-emerald-[0-9]\+/to-gray-900/g' "$file"
  
  sed -i '' 's/from-amber-[0-9]\+/from-gray-700/g' "$file"
  sed -i '' 's/to-amber-[0-9]\+/to-gray-900/g' "$file"
  
  # Replace bg- colors
  sed -i '' 's/bg-purple-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-blue-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-green-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-red-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-yellow-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-pink-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-indigo-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-orange-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-teal-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-cyan-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-emerald-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-amber-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-lime-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-rose-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-fuchsia-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-violet-[0-9]\+/bg-gray-800/g' "$file"
  sed -i '' 's/bg-sky-[0-9]\+/bg-gray-800/g' "$file"
  
  # Replace text- colors
  sed -i '' 's/text-purple-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-blue-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-green-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-red-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-yellow-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-pink-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-indigo-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-orange-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-teal-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-cyan-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-emerald-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-amber-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-lime-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-rose-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-fuchsia-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-violet-[0-9]\+/text-gray-300/g' "$file"
  sed -i '' 's/text-sky-[0-9]\+/text-gray-300/g' "$file"
  
  # Replace border- colors
  sed -i '' 's/border-purple-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-blue-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-green-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-red-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-yellow-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-pink-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-indigo-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-orange-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-teal-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-cyan-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-emerald-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-amber-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-lime-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-rose-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-fuchsia-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-violet-[0-9]\+/border-gray-700/g' "$file"
  sed -i '' 's/border-sky-[0-9]\+/border-gray-700/g' "$file"
  
  # Replace hover states
  sed -i '' 's/hover:bg-purple-[0-9]\+/hover:bg-gray-700/g' "$file"
  sed -i '' 's/hover:bg-blue-[0-9]\+/hover:bg-gray-700/g' "$file"
  sed -i '' 's/hover:bg-green-[0-9]\+/hover:bg-gray-700/g' "$file"
  sed -i '' 's/hover:bg-red-[0-9]\+/hover:bg-gray-700/g' "$file"
  sed -i '' 's/hover:bg-yellow-[0-9]\+/hover:bg-gray-700/g' "$file"
  sed -i '' 's/hover:bg-cyan-[0-9]\+/hover:bg-gray-700/g' "$file"
  sed -i '' 's/hover:bg-orange-[0-9]\+/hover:bg-gray-700/g' "$file"
  sed -i '' 's/hover:bg-amber-[0-9]\+/hover:bg-gray-700/g' "$file"
  
  sed -i '' 's/hover:text-purple-[0-9]\+/hover:text-white/g' "$file"
  sed -i '' 's/hover:text-blue-[0-9]\+/hover:text-white/g' "$file"
  sed -i '' 's/hover:text-cyan-[0-9]\+/hover:text-white/g' "$file"
  
  sed -i '' 's/hover:border-purple-[0-9]\+/hover:border-gray-600/g' "$file"
  sed -i '' 's/hover:border-blue-[0-9]\+/hover:border-gray-600/g' "$file"
  sed -i '' 's/hover:border-cyan-[0-9]\+/hover:border-gray-600/g' "$file"
  sed -i '' 's/hover:border-green-[0-9]\+/hover:border-gray-600/g' "$file"
  sed -i '' 's/hover:border-red-[0-9]\+/hover:border-gray-600/g' "$file"
  
  # Replace shadow colors
  sed -i '' 's/shadow-purple-[0-9]\+/shadow-gray-900/g' "$file"
  sed -i '' 's/shadow-blue-[0-9]\+/shadow-gray-900/g' "$file"
  sed -i '' 's/shadow-cyan-[0-9]\+/shadow-gray-900/g' "$file"
  sed -i '' 's/shadow-green-[0-9]\+/shadow-gray-900/g' "$file"
  sed -i '' 's/shadow-red-[0-9]\+/shadow-gray-900/g' "$file"
  sed -i '' 's/shadow-amber-[0-9]\+/shadow-gray-900/g' "$file"
  
  # Replace ring colors
  sed -i '' 's/ring-cyan-[0-9]\+/ring-gray-700/g' "$file"
  sed -i '' 's/ring-blue-[0-9]\+/ring-gray-700/g' "$file"
  
  # Remove emojis and symbols (common patterns)
  sed -i '' 's/[⭐🎯🚀💰🔥✨🎉🏆👥📊💡🛡️⚡🌟💎🎨🔒🌐📱💻🎮🏅⚙️📈🎁💬📝🔔🎤🎯🎬🎧🎪]/★/g' "$file"
  
done

echo "Done! Backup files created with .backup extension"
echo "Run 'find app components -name \"*.backup\" -delete' to remove backups after verification"
