"use client";

import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import type { AnalysisResponse } from "@/types";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

function fmt(value: number): string {
  if (Math.abs(value) >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  if (Math.abs(value) >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

const ttStyle = { background: "#1e293b", border: "1px solid #334155", borderRadius: "8px", fontSize: "13px" };

export default function FinancialCharts({ analysis }: { analysis: AnalysisResponse }) {
  const periodData = Object.entries(analysis.summary.total_by_period).map(([period, total]) => ({ period, total }));
  const topTrends = analysis.trends.slice(0, 5);
  const periods = analysis.summary.periods;
  const trendLineData = periods.map((p) => {
    const point: Record<string, string | number> = { period: p };
    topTrends.forEach((t) => { point[t.line_item] = t.values_by_period[p] || 0; });
    return point;
  });
  const ratioEntries = Object.entries(analysis.ratios).filter(([k]) => k !== "period");
  const compData = analysis.period_comparison.items?.slice(0, 10).map((item) => ({
    name: item.line_item.length > 20 ? item.line_item.slice(0, 20) + "..." : item.line_item,
    [analysis.period_comparison.period_1]: item.period_1_value,
    [analysis.period_comparison.period_2]: item.period_2_value,
  }));

  return (
    <div className="space-y-6">
      {/* Period Totals */}
      <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] p-6">
        <h3 className="text-lg font-semibold mb-4">Totals by Period</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={periodData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="period" stroke="#64748b" fontSize={12} />
            <YAxis stroke="#64748b" fontSize={12} tickFormatter={fmt} />
            <Tooltip contentStyle={ttStyle} formatter={(v: number) => [fmt(v), "Total"]} />
            <Bar dataKey="total" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Trend Lines */}
      {topTrends.length > 0 && (
        <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] p-6">
          <h3 className="text-lg font-semibold mb-4">Top Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendLineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="period" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} tickFormatter={fmt} />
              <Tooltip contentStyle={ttStyle} formatter={(v: number) => fmt(v)} />
              {topTrends.map((t, i) => (
                <Line key={t.line_item} type="monotone" dataKey={t.line_item} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={{ r: 4 }} />
              ))}
            </LineChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-4 mt-3">
            {topTrends.map((t, i) => (
              <div key={t.line_item} className="flex items-center gap-2 text-xs">
                <div className="w-3 h-3 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                <span className="text-gray-400">{t.line_item}</span>
                <span className={t.direction === "increasing" ? "text-emerald-400" : t.direction === "decreasing" ? "text-red-400" : "text-gray-400"}>
                  {t.avg_change_pct > 0 ? "+" : ""}{t.avg_change_pct}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Financial Ratios */}
      {ratioEntries.length > 0 && (
        <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] p-6">
          <h3 className="text-lg font-semibold mb-4">Key Financial Ratios</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {ratioEntries.map(([key, value]) => {
              const label = key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
              const isPct = key.includes("margin") || key.includes("return");
              return (
                <div key={key} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                  <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
                  <p className="text-2xl font-bold mt-1 text-blue-400">
                    {typeof value === "number" ? value.toFixed(2) : value}{isPct ? "%" : "x"}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Period Comparison */}
      {compData && compData.length > 0 && (
        <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] p-6">
          <h3 className="text-lg font-semibold mb-4">
            Period Comparison: {analysis.period_comparison.period_1} vs {analysis.period_comparison.period_2}
          </h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={compData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" stroke="#64748b" fontSize={12} tickFormatter={fmt} />
              <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={11} width={150} />
              <Tooltip contentStyle={ttStyle} formatter={(v: number) => fmt(v)} />
              <Bar dataKey={analysis.period_comparison.period_1} fill="#64748b" radius={[0, 4, 4, 0]} />
              <Bar dataKey={analysis.period_comparison.period_2} fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Anomalies */}
      {analysis.anomalies.length > 0 && (
        <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] p-6">
          <h3 className="text-lg font-semibold mb-4">Detected Anomalies</h3>
          <div className="space-y-3">
            {analysis.anomalies.map((a, i) => (
              <div key={i} className={`rounded-lg p-4 border ${a.severity === "high" ? "border-red-500/30 bg-red-500/10" : "border-yellow-500/30 bg-yellow-500/10"}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs font-bold uppercase px-2 py-0.5 rounded ${a.severity === "high" ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400"}`}>{a.severity}</span>
                  <span className="text-sm font-medium">{a.line_item}</span>
                  <span className="text-xs text-gray-400 ml-auto">{a.period}</span>
                </div>
                <p className="text-sm text-gray-300">{a.description}</p>
                <p className="text-xs text-gray-500 mt-1">Amount: {fmt(a.amount)} | Mean: {fmt(a.mean)} | Z-Score: {a.z_score}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
