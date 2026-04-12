"use client";

import { motion } from "framer-motion";

export default function Navbar() {
  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="w-full py-5 px-6 md:px-12 flex items-center justify-between"
    >
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
          <span className="text-white font-bold text-sm">E</span>
        </div>
        <span className="text-xl font-bold tracking-tight text-gray-900">
          Eenera
        </span>
      </div>

      <div className="flex items-center gap-6">
        <span className="text-sm text-gray-500 hidden sm:block">
          AI Workflow Audit
        </span>
        <div className="h-5 w-px bg-gray-200 hidden sm:block" />
        <span className="text-xs font-medium text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-full">
          Beta
        </span>
      </div>
    </motion.nav>
  );
}
