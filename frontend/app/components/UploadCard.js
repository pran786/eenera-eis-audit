"use client";

import { useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

const ALLOWED_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

const ALLOWED_EXTENSIONS = [".pdf", ".docx"];

export default function UploadCard({ onUpload, error, loading }) {
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState(null);
  const [hourlyRate, setHourlyRate] = useState("");
  const inputRef = useRef(null);

  const isValidFile = (f) => {
    if (ALLOWED_TYPES.includes(f.type)) return true;
    const ext = f.name.toLowerCase().slice(f.name.lastIndexOf("."));
    return ALLOWED_EXTENSIONS.includes(ext);
  };

  const handleFile = useCallback((f) => {
    if (f && isValidFile(f)) {
      setFile(f);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    handleFile(f);
  }, [handleFile]);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleSubmit = () => {
    if (file && onUpload) {
      onUpload(file, hourlyRate || null);
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="glass-card p-8"
    >
      {/* Error banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6 p-4 bg-red-50 border border-red-100 rounded-xl text-red-700 text-sm flex items-start gap-3"
          >
            <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => inputRef.current?.click()}
        className={`upload-zone p-12 text-center cursor-pointer transition-all duration-300 ${
          dragOver ? "drag-over" : ""
        } ${file ? "border-indigo-300 bg-indigo-50/50" : ""}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => handleFile(e.target.files?.[0])}
          className="hidden"
        />

        <AnimatePresence mode="wait">
          {!file ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-indigo-50 flex items-center justify-center">
                <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
              </div>
              <p className="text-gray-700 font-medium mb-1">
                Upload a workflow, SOP, or describe a process
              </p>
              <p className="text-sm text-gray-400">PDF or DOCX · Max 50MB</p>
            </motion.div>
          ) : (
            <motion.div
              key="file"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center gap-4"
            >
              <div className="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center">
                <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
              </div>
              <div className="text-left">
                <p className="text-gray-800 font-medium text-sm">{file.name}</p>
                <p className="text-xs text-gray-400">{formatSize(file.size)}</p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                }}
                className="ml-2 p-1 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Hourly rate input */}
      <div className="mt-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <label className="text-xs font-medium text-gray-500 mb-1.5 block">
            Hourly Rate (£) — Optional
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">£</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={hourlyRate}
              onChange={(e) => setHourlyRate(e.target.value)}
              placeholder="15.00"
              className="w-full pl-8 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-300 focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 transition-all"
            />
          </div>
        </div>

        <div className="flex items-end">
          <button
            onClick={handleSubmit}
            disabled={!file || loading}
            className={`w-full sm:w-auto px-8 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
              file && !loading
                ? "bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-200 hover:shadow-xl hover:shadow-indigo-300 hover:-translate-y-0.5 active:translate-y-0"
                : "bg-gray-100 text-gray-400 cursor-not-allowed"
            }`}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Uploading…
              </span>
            ) : (
              "Generate Audit Report"
            )}
          </button>
        </div>
      </div>
    </motion.div>
  );
}
