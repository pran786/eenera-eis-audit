"use client";

import { motion } from "framer-motion";

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.4, ease: "easeOut" },
  }),
};

export default function ReportDisplay({ report, onReset }) {
  const r = report?.report || {};

  const workflowSteps = r.workflow_steps || [];
  const manualTasks = r.manual_tasks || [];
  const repeatedTasks = r.repeated_tasks || [];
  const bottlenecks = r.bottlenecks || [];
  const delays = r.delays || [];
  const inefficiencies = r.inefficiencies || [];
  const revenueLeakage = r.revenue_leakage || [];
  const costAnalysis = r.cost_analysis || {};
  const costExplanation = costAnalysis.cost_explanation || "";
  const timeLoss = r.time_loss_hours_per_day || 0;
  const hourlyRate = r.hourly_rate || 15;
  const markdownReport = r.markdown_report || "";
  const implPlan = r.implementation_plan || {};
  const phase1 = implPlan.phase_1 || [];
  const phase2 = implPlan.phase_2 || [];

  return (
    <div className="space-y-6">
      <div id="pdf-report-body" className="space-y-6 pb-4">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Audit Report</h2>
          <p className="text-sm text-gray-400 mt-1">
            {report.filename} · Job {report.job_id?.slice(0, 8)}…
          </p>
        </div>
        <button
          onClick={onReset}
          className="text-sm text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1.5 px-4 py-2 rounded-xl hover:bg-indigo-50 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
          </svg>
          New Audit
        </button>
      </motion.div>

      {/* Executive Summary Card */}
      <motion.div custom={0} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-5 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
          Executive Summary
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            label="Workflow Steps"
            value={workflowSteps.length}
            icon="📋"
          />
          <MetricCard
            label="Manual Tasks"
            value={manualTasks.length}
            icon="🖐️"
            accent={manualTasks.length > 0 ? "warning" : "default"}
          />
          <MetricCard
            label="Bottlenecks"
            value={bottlenecks.length}
            icon="⚠️"
            accent={bottlenecks.length > 0 ? "danger" : "default"}
          />
          <MetricCard
            label="Inefficiencies"
            value={inefficiencies.length}
            icon="🚨"
            accent={inefficiencies.length > 0 ? "danger" : "default"}
          />
        </div>

        {/* Cost hero */}
        {costAnalysis.monthly_cost > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="mt-6 p-5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white"
          >
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <p className="text-indigo-100 text-sm font-medium">Estimated Monthly Cost Impact</p>
                <p className="text-3xl font-bold mt-1">
                  £{costAnalysis.monthly_cost?.toLocaleString("en-GB", { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="text-right">
                <p className="text-indigo-100 text-sm">Time Lost Per Day</p>
                <p className="text-xl font-semibold">{timeLoss}h</p>
              </div>
              <div className="text-right">
                <p className="text-indigo-100 text-sm">Annual Projection</p>
                <p className="text-xl font-semibold">
                  £{costAnalysis.annual_cost?.toLocaleString("en-GB", { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Current Workflow Card */}
      {workflowSteps.length > 0 && (
        <motion.div custom={1} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
            Current Workflow
          </h3>
          <div className="space-y-2">
            {workflowSteps.map((step, i) => (
              <div
                key={i}
                className="flex gap-4 p-3 rounded-xl hover:bg-gray-50 transition-colors group"
              >
                <div className="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center text-xs font-bold shrink-0 group-hover:bg-indigo-100 transition-colors">
                  {i + 1}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800">{step.step}</p>
                  {step.description && (
                    <p className="text-xs text-gray-400 mt-0.5">{step.description}</p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Sub-sections */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-5">
            {manualTasks.length > 0 && (
              <TagList title="🖐️ Manual Tasks" items={manualTasks} color="amber" />
            )}
            {repeatedTasks.length > 0 && (
              <TagList title="🔁 Repeated Tasks" items={repeatedTasks} color="orange" />
            )}
            {bottlenecks.length > 0 && (
              <TagList title="⚠️ Bottlenecks" items={bottlenecks} color="red" />
            )}
            {delays.length > 0 && (
              <TagList title="⏳ Delays" items={delays} color="yellow" />
            )}
          </div>
        </motion.div>
      )}

      {/* Key Inefficiencies Card */}
      {inefficiencies.length > 0 && (
        <motion.div custom={2} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
            Key Inefficiencies & Solutions
          </h3>
          <div className="space-y-4">
            {inefficiencies.map((item, i) => {
              const isObj = typeof item === 'object' && item !== null;
              const issue = isObj ? item.issue : item;
              const rec = isObj ? item.recommendation : null;

              return (
                <div
                  key={i}
                  className="flex gap-4 p-4 rounded-xl bg-red-50/40 border border-red-100/50 flex-col sm:flex-row shadow-sm"
                >
                  <div className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-sm font-bold shrink-0 mt-0.5">
                    {i + 1}
                  </div>
                  <div className="flex-1">
                    <p className="text-[15px] font-medium text-gray-800 leading-snug">{issue}</p>
                    {rec && (
                      <div className="mt-3 p-3 bg-white/70 rounded-lg border border-red-50/50 flex gap-2 items-start">
                        <svg className="w-4 h-4 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        <div>
                          <p className="text-xs font-bold text-green-700 uppercase tracking-wide mb-0.5">Recommended Solution</p>
                          <p className="text-sm text-gray-600">{rec}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Revenue & Cost Leakage Card */}
      <motion.div custom={3} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-purple-500" />
          Revenue &amp; Cost Analysis
        </h3>

        <div className="grid grid-cols-3 gap-4 mb-5">
          <CostCard label="Daily" amount={costAnalysis.daily_cost} />
          <CostCard label="Monthly" amount={costAnalysis.monthly_cost} highlight />
          <CostCard label="Annual" amount={costAnalysis.annual_cost} />
        </div>

        {costExplanation ? (
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-gray-50 text-sm text-gray-600 border border-gray-100">
            <svg className="w-4 h-4 text-indigo-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{costExplanation}</span>
          </div>
        ) : (
          <div className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-gray-50 text-sm text-gray-500">
            <span>Based on</span>
            <span className="font-semibold text-gray-700">£{hourlyRate}/hr</span>
            <span>·</span>
            <span className="font-semibold text-gray-700">{timeLoss}h/day</span>
            <span>·</span>
            <span className="font-semibold text-gray-700">22 days/month</span>
          </div>
        )}

        {revenueLeakage.length > 0 && (
          <div className="mt-5">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Revenue Leakage Points
            </p>
            <div className="space-y-2">
              {revenueLeakage.map((item, i) => (
                <div key={i} className="flex gap-2 items-start text-sm text-gray-600">
                  <svg className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {item}
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.div>

      {/* Implementation Plan Card */}
      {(phase1.length > 0 || phase2.length > 0) && (
        <motion.div custom={4} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-5 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            Recommended Implementation Plan
          </h3>

          <div className="grid sm:grid-cols-2 gap-6">
            {phase1.length > 0 && (
              <div className="bg-emerald-50/50 rounded-xl p-5 border border-emerald-100/50 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-3 opacity-10">
                  <span className="text-6xl">1</span>
                </div>
                <h4 className="font-bold text-emerald-800 mb-4 flex items-center gap-2 relative z-10">
                  Phase 1 : Quick Wins
                </h4>
                <ul className="space-y-3 relative z-10">
                  {phase1.map((item, i) => (
                    <li key={i} className="flex gap-2.5 text-sm text-gray-700">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0 mt-1.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {phase2.length > 0 && (
              <div className="bg-blue-50/50 rounded-xl p-5 border border-blue-100/50 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-3 opacity-10">
                  <span className="text-6xl">2</span>
                </div>
                <h4 className="font-bold text-blue-800 mb-4 flex items-center gap-2 relative z-10">
                  Phase 2 : System Improvements
                </h4>
                <ul className="space-y-3 relative z-10">
                  {phase2.map((item, i) => (
                    <li key={i} className="flex gap-2.5 text-sm text-gray-700">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0 mt-1.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </motion.div>
      )}

      </div>

      {/* Download / Action */}
      <motion.div custom={5} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6 text-center">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center justify-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
          Next Steps
        </h3>
        <p className="text-sm text-gray-500 mb-5">
          Contact Eenera for a detailed automation roadmap and implementation support.
        </p>
        <div className="flex justify-center gap-3">
          {markdownReport && (
            <button
              onClick={async () => {
                const element = document.getElementById('pdf-report-body');
                const html2canvas = (await import('html2canvas-pro')).default;
                const { jsPDF } = await import('jspdf');
                
                try {
                  // html2canvas-pro handles Tailwind v4's oklch() and lab() colors without crashing
                  const canvas = await html2canvas(element, {
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#fafbfc'
                  });

                  const imgData = canvas.toDataURL('image/jpeg', 0.98);
                  
                  // Use a continuous PDF format based on exactly what was rendered
                  // This prevents beautiful glass cards from being awkwardly sliced in half
                  const pdf = new jsPDF({
                    orientation: 'portrait',
                    unit: 'px',
                    format: [canvas.width, canvas.height]
                  });

                  pdf.addImage(imgData, 'JPEG', 0, 0, canvas.width, canvas.height);
                  pdf.save(`eenera-audit-${report.job_id?.slice(0, 8)}.pdf`);
                } catch (e) {
                  console.error("PDF generation error:", e);
                  alert("There was an error generating the PDF. Please check the console.");
                }
              }}
              className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-200 hover:shadow-xl hover:shadow-indigo-300 hover:-translate-y-0.5 active:translate-y-0 transition-all"
            >
              Download PDF Report
            </button>
          )}
          <button
            onClick={onReset}
            className="px-6 py-2.5 rounded-xl text-sm font-medium border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
          >
            Run Another Audit
          </button>
        </div>
      </motion.div>
    </div>
  );
}

/* ── Sub-components ─────────────────────────────────────────────────── */

function MetricCard({ label, value, icon, accent = "default" }) {
  const accents = {
    default: "bg-gray-50 text-gray-900",
    warning: "bg-amber-50 text-amber-700",
    danger: "bg-red-50 text-red-700",
  };

  return (
    <div className={`p-4 rounded-xl text-center ${accents[accent]}`}>
      <span className="text-xl">{icon}</span>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}

function CostCard({ label, amount, highlight }) {
  const formatted = amount != null
    ? `£${amount.toLocaleString("en-GB", { minimumFractionDigits: 2 })}`
    : "—";

  return (
    <div
      className={`p-4 rounded-xl text-center transition-colors ${
        highlight
          ? "bg-indigo-50 border border-indigo-100"
          : "bg-gray-50"
      }`}
    >
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className={`text-lg font-bold ${highlight ? "text-indigo-700" : "text-gray-800"}`}>
        {formatted}
      </p>
    </div>
  );
}

function TagList({ title, items, color }) {
  const colors = {
    amber: "bg-amber-50 text-amber-700 border-amber-100",
    orange: "bg-orange-50 text-orange-700 border-orange-100",
    red: "bg-red-50 text-red-700 border-red-100",
    yellow: "bg-yellow-50 text-yellow-700 border-yellow-100",
  };

  return (
    <div>
      <p className="text-xs font-semibold text-gray-500 mb-2">{title}</p>
      <div className="flex flex-wrap gap-1.5">
        {items.map((item, i) => (
          <span
            key={i}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${colors[color] || colors.amber}`}
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}
