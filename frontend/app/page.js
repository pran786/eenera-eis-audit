"use client";

import { useState } from "react";
import Hero from "./components/Hero";
import UploadCard from "./components/UploadCard";
import ProcessingState from "./components/ProcessingState";
import ReportDisplay from "./components/ReportDisplay";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

const STEPS = [
  "Extracting document",
  "Analyzing workflow",
  "Detecting inefficiencies",
  "Calculating cost impact",
  "Generating report",
];

export default function Home() {
  const [stage, setStage] = useState("idle"); // idle | uploading | processing | done | error
  const [currentStep, setCurrentStep] = useState(0);
  const [report, setReport] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [error, setError] = useState(null);

  // ── Upload handler ──────────────────────────────────────────────────
  const handleUpload = async (file, hourlyRate) => {
    setStage("uploading");
    setError(null);
    setReport(null);
    setCurrentStep(0);

    try {
      // Upload file
      const formData = new FormData();
      formData.append("file", file);
      if (hourlyRate) formData.append("hourly_rate", hourlyRate);

      const uploadRes = await fetch(`${API_BASE}/api/v1/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!uploadRes.ok) {
        const errData = await uploadRes.json();
        throw new Error(errData.detail || "Upload failed");
      }

      const { job_id } = await uploadRes.json();
      setJobId(job_id);
      setStage("processing");

      // Simulate step progression while polling
      const stepInterval = setInterval(() => {
        setCurrentStep((prev) => Math.min(prev + 1, STEPS.length - 1));
      }, 1800);

      // Poll for completion
      let attempts = 0;
      const maxAttempts = 60;

      while (attempts < maxAttempts) {
        await new Promise((r) => setTimeout(r, 2000));
        attempts++;

        const statusRes = await fetch(`${API_BASE}/api/v1/status/${job_id}`);
        const statusData = await statusRes.json();

        if (statusData.status === "completed") {
          clearInterval(stepInterval);
          setCurrentStep(STEPS.length - 1);

          // Fetch full report
          const reportRes = await fetch(`${API_BASE}/api/v1/report/${job_id}`);
          const reportData = await reportRes.json();

          // Finish the last step animation
          await new Promise((r) => setTimeout(r, 800));

          setReport(reportData);
          setStage("done");
          return;
        }

        if (statusData.status === "failed") {
          clearInterval(stepInterval);
          throw new Error(statusData.error || "Analysis failed");
        }
      }

      clearInterval(stepInterval);
      throw new Error("Analysis timed out");
    } catch (err) {
      setError(err.message);
      setStage("error");
    }
  };

  const handleReset = () => {
    setStage("idle");
    setReport(null);
    setJobId(null);
    setError(null);
    setCurrentStep(0);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1">
        <Hero />

        <section className="max-w-3xl mx-auto px-6 pb-24 -mt-8">
          {/* Upload (idle or error state) */}
          {(stage === "idle" || stage === "error") && (
            <UploadCard
              onUpload={handleUpload}
              error={error}
              loading={stage === "uploading"}
            />
          )}

          {/* Uploading state */}
          {stage === "uploading" && (
            <UploadCard
              onUpload={handleUpload}
              error={null}
              loading={true}
            />
          )}

          {/* Processing state */}
          {stage === "processing" && (
            <ProcessingState steps={STEPS} currentStep={currentStep} />
          )}

          {/* Report */}
          {stage === "done" && report && (
            <ReportDisplay report={report} onReset={handleReset} />
          )}
        </section>
      </main>

      <Footer />
    </div>
  );
}
