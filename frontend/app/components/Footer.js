"use client";

export default function Footer() {
  return (
    <footer className="py-8 px-6 text-center border-t border-gray-100">
      <p className="text-sm text-gray-400">
        © {new Date().getFullYear()} Eenera · AI Workflow Audit System
      </p>
    </footer>
  );
}
