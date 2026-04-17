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

        {/* 1. Estimated Impact Card (Hero) */}
        {costAnalysis.monthly_cost > 0 && (
          <motion.div
            custom={0}
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            className="p-8 rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-xl shadow-indigo-200"
          >
            <h3 className="text-indigo-100 text-sm font-semibold uppercase tracking-widest mb-6 border-b border-white/20 pb-2">Estimated Impact</h3>
            <div className="flex flex-col sm:flex-row items-center justify-between gap-8">
              <div>
                <p className="text-indigo-200 text-sm font-medium uppercase tracking-wider mb-1">Cost Impact</p>
                <p className="text-4xl md:text-5xl font-extrabold mb-2 tracking-tight">
                  £{costAnalysis.monthly_cost?.toLocaleString("en-GB", { minimumFractionDigits: 2 })}
                  <span className="text-xl md:text-2xl font-semibold text-indigo-200 ml-2">/ month</span>
                </p>
                {costExplanation && <p className="text-sm text-indigo-100 mt-3 bg-white/10 px-4 py-2 rounded-lg">{costExplanation}</p>}
                {!costExplanation && (
                  <p className="text-sm text-indigo-100 mt-2">
                    Based on £{hourlyRate}/hr · {timeLoss}h/day · 22 days/month
                  </p>
                )}
              </div>
              <div className="flex gap-10 text-right shrink-0">
                <div>
                  <p className="text-indigo-200 text-sm font-medium uppercase tracking-wider mb-1">Time Wasted</p>
                  <p className="text-3xl font-bold">{timeLoss}h <span className="text-lg font-normal text-indigo-200">/ day</span></p>
                </div>
                <div>
                  <p className="text-indigo-200 text-sm font-medium uppercase tracking-wider mb-1">Annual Impact</p>
                  <p className="text-3xl font-bold">£{costAnalysis.annual_cost?.toLocaleString("en-GB", { minimumFractionDigits: 0 })}</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* 2. Overview */}
        <motion.div custom={1} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6 border-t-4 border-t-blue-500">
          <h3 className="text-sm font-bold text-gray-800 uppercase tracking-wider mb-6 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            Overview
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <MetricCard label="Workflow Steps" value={workflowSteps.length} icon="📋" />
            <MetricCard label="Manual Tasks" value={manualTasks.length} icon="🖐️" accent={manualTasks.length > 0 ? "warning" : "default"} />
            <MetricCard label="Bottlenecks" value={bottlenecks.length} icon="⚠️" accent={bottlenecks.length > 0 ? "danger" : "default"} />
            <MetricCard label="Inefficiencies" value={inefficiencies.length} icon="🚨" accent={inefficiencies.length > 0 ? "danger" : "default"} />
          </div>

          {workflowSteps.length > 0 && (
            <div>
              <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Analyzed Process Steps</p>
              <div className="space-y-2">
                {workflowSteps.map((step, i) => (
                  <div key={i} className="flex gap-4 p-3 rounded-xl bg-gray-50 border border-gray-100">
                    <div className="w-7 h-7 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold shrink-0">
                      {i + 1}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-800">{step.step}</p>
                      {step.description && <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{step.description}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        {/* Middle Two Columns */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* 3. Key Inefficiencies */}
          {inefficiencies.length > 0 && (
            <motion.div custom={2} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6 border-t-4 border-t-red-500">
              <h3 className="text-sm font-bold text-gray-800 uppercase tracking-wider mb-5 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500" />
                Key Inefficiencies
              </h3>
              <div className="space-y-3">
                {inefficiencies.map((item, i) => {
                  const issue = typeof item === 'object' ? item.issue : item;
                  return (
                    <div key={i} className="flex gap-3 p-3.5 rounded-xl bg-red-50/50 border border-red-100 text-sm text-gray-700 shadow-sm">
                      <span className="font-bold text-red-500 shrink-0">{i + 1}.</span>
                      <span className="leading-snug">{issue}</span>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}

          {/* 4. Operational Risks */}
          {(bottlenecks.length > 0 || delays.length > 0 || revenueLeakage.length > 0) && (
            <motion.div custom={3} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6 border-t-4 border-t-orange-500">
              <h3 className="text-sm font-bold text-gray-800 uppercase tracking-wider mb-5 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-orange-500" />
                Operational Risks
              </h3>
              <div className="space-y-5">
                {revenueLeakage.length > 0 && (
                  <div>
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-1.5"><span className="text-orange-500">❖</span> Revenue Leakage</p>
                    <ul className="space-y-2 ml-5">
                      {revenueLeakage.map((l, i) => <li key={i} className="text-sm text-gray-600 list-disc">{l}</li>)}
                    </ul>
                  </div>
                )}
                {bottlenecks.length > 0 && (
                  <div>
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-1.5"><span className="text-orange-500">❖</span> Bottlenecks</p>
                    <ul className="space-y-2 ml-5">
                      {bottlenecks.map((b, i) => <li key={i} className="text-sm text-gray-600 list-disc">{b}</li>)}
                    </ul>
                  </div>
                )}
                {delays.length > 0 && (
                  <div>
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-1.5"><span className="text-orange-500">❖</span> Delays</p>
                    <ul className="space-y-2 ml-5">
                      {delays.map((d, i) => <li key={i} className="text-sm text-gray-600 list-disc">{d}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </div>

        {/* 5. Recommendations */}
        <motion.div custom={4} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6 border-t-4 border-t-emerald-500">
          <h3 className="text-sm font-bold text-gray-800 uppercase tracking-wider mb-6 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            Recommendations
          </h3>
          
          <div className="space-y-8">
            {inefficiencies.some(i => typeof i === 'object' && i.recommendation) && (
              <div>
                <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-4">Direct Solutions</p>
                <div className="grid sm:grid-cols-2 gap-4">
                  {inefficiencies.filter(i => typeof i === 'object' && i.recommendation).map((item, i) => (
                    <div key={i} className="bg-emerald-50/40 p-4 rounded-xl border border-emerald-100 flex gap-3 shadow-sm">
                      <div className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0 mt-0.5">
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <span className="text-[14px] text-gray-800 font-medium leading-snug">{item.recommendation}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {(phase1.length > 0 || phase2.length > 0) && (
              <div className="pt-2">
                <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-4">Implementation Plan</p>
                <div className="grid sm:grid-cols-2 gap-6">
                  {phase1.length > 0 && (
                    <div className="bg-[#f0fdf4] rounded-xl p-5 border border-emerald-200 shadow-sm relative overflow-hidden">
                      <div className="absolute top-0 right-0 p-3 opacity-10">
                        <span className="text-7xl font-black">1</span>
                      </div>
                      <h4 className="font-extrabold text-emerald-800 mb-4 text-sm flex items-center gap-2 uppercase tracking-wide relative z-10">
                        Phase 1 : Quick Wins
                      </h4>
                      <ul className="space-y-3 relative z-10">
                        {phase1.map((item, i) => (
                          <li key={i} className="flex gap-3 text-sm text-gray-700 font-medium">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0 mt-1.5" />
                            <span className="leading-snug">{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {phase2.length > 0 && (
                    <div className="bg-[#eff6ff] rounded-xl p-5 border border-blue-200 shadow-sm relative overflow-hidden">
                      <div className="absolute top-0 right-0 p-3 opacity-10">
                        <span className="text-7xl font-black">2</span>
                      </div>
                      <h4 className="font-extrabold text-blue-800 mb-4 text-sm flex items-center gap-2 uppercase tracking-wide relative z-10">
                        Phase 2 : System Improvements
                      </h4>
                      <ul className="space-y-3 relative z-10">
                        {phase2.map((item, i) => (
                          <li key={i} className="flex gap-3 text-sm text-gray-700 font-medium">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0 mt-1.5" />
                            <span className="leading-snug">{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* 6. Automation Opportunities */}
        {(manualTasks.length > 0 || repeatedTasks.length > 0) && (
          <motion.div custom={5} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-6 border-t-4 border-t-purple-500">
            <h3 className="text-sm font-bold text-gray-800 uppercase tracking-wider mb-3 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-500" />
              Automation Opportunities
            </h3>
            <p className="text-sm text-gray-500 mb-6">These tasks currently require human intervention but are highly suitable for AI or software automation.</p>
            <div className="grid sm:grid-cols-2 gap-6">
              {manualTasks.length > 0 && (
                <div>
                  <p className="text-xs font-bold text-purple-600 uppercase tracking-wide mb-3">Manual Tasks</p>
                  <div className="flex flex-wrap gap-2">
                    {manualTasks.map((t, i) => <span key={i} className="px-3 py-1.5 bg-purple-50 text-purple-800 text-xs font-bold rounded-lg border border-purple-200 shadow-sm">{t}</span>)}
                  </div>
                </div>
              )}
              {repeatedTasks.length > 0 && (
                <div>
                  <p className="text-xs font-bold text-indigo-600 uppercase tracking-wide mb-3">Repeated Actions</p>
                  <div className="flex flex-wrap gap-2">
                    {repeatedTasks.map((t, i) => <span key={i} className="px-3 py-1.5 bg-indigo-50 text-indigo-800 text-xs font-bold rounded-lg border border-indigo-200 shadow-sm">{t}</span>)}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}

      </div>

      {/* Download / Action CTA */}
      <motion.div custom={6} variants={cardVariants} initial="hidden" animate="visible" className="glass-card p-10 text-center bg-gray-50 border border-gray-200 mt-8">
        <h3 className="text-2xl font-extrabold text-gray-900 mb-3 tracking-tight">Ready to transform your operations?</h3>
        <p className="text-base text-gray-500 mb-8 max-w-lg mx-auto">
          Our team can help you implement these recommendations and automate your workflows in weeks, not months.
        </p>
        <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
          <button
            onClick={() => window.open("mailto:hello@eenera.com", "_blank")}
            className="px-8 py-3.5 rounded-xl text-[15px] font-extrabold border-2 border-indigo-600 bg-indigo-50 text-indigo-700 hover:bg-indigo-600 hover:text-white transition-all shadow-sm w-full sm:w-auto"
          >
            Request full assessment / support
          </button>
          {markdownReport && (
            <button
              onClick={async () => {
                const element = document.getElementById('pdf-report-body');
                const html2canvas = (await import('html2canvas-pro')).default;
                const { jsPDF } = await import('jspdf');
                
                try {
                  const canvas = await html2canvas(element, { scale: 2, useCORS: true, backgroundColor: '#fafbfc' });
                  const imgData = canvas.toDataURL('image/jpeg', 0.98);
                  const pdf = new jsPDF({ orientation: 'portrait', unit: 'px', format: [canvas.width, canvas.height] });
                  pdf.addImage(imgData, 'JPEG', 0, 0, canvas.width, canvas.height);
                  pdf.save(`eenera-${report.job_id?.slice(0, 8)}.pdf`);
                } catch (e) {
                  console.error(e);
                  alert("There was an error generating the PDF. Please check the console.");
                }
              }}
              className="px-8 py-3.5 rounded-xl text-[15px] font-extrabold bg-gray-900 text-white shadow-lg hover:shadow-xl hover:bg-black hover:-translate-y-0.5 active:translate-y-0 transition-all w-full sm:w-auto flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download PDF Report
            </button>
          )}
        </div>
        <p className="mt-8 text-sm">
          <button onClick={onReset} className="text-gray-400 hover:text-gray-600 font-medium transition-colors border-b border-dashed border-gray-300">
            Run Another Audit
          </button>
        </p>
      </motion.div>
    </div>
  );
}

/* ── Sub-components ─────────────────────────────────────────────────── */

function MetricCard({ label, value, icon, accent = "default" }) {
  const accents = {
    default: "bg-white text-gray-900 border-gray-100",
    warning: "bg-amber-50 text-amber-800 border-amber-100",
    danger: "bg-red-50 text-red-800 border-red-100",
  };

  return (
    <div className={`p-4 rounded-xl text-center border shadow-sm ${accents[accent]}`}>
      <span className="text-2xl">{icon}</span>
      <p className="text-3xl font-extrabold mt-2 tracking-tight">{value}</p>
      <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mt-1">{label}</p>
    </div>
  );
}
