"use client";

import { useState, useEffect } from "react";
import { BarChart3, TrendingUp, AlertTriangle, Calculator, Database, Loader2 } from "lucide-react";
import { getAnalysis } from "@/lib/api";
import type { AnalysisResponse } from "@/types";
import FinancialCharts from "./FinancialCharts";

export default function Dashboard({ datasetId, datasetName }: { datasetId: number; datasetName: string }) {
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getAnalysis(datasetId)
      .then((data) => setAnalysis(data as AnalysisResponse))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [datasetId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
        <span className="ml-3 text-gray-400">Running financial analysis...</span>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="text-center py-20 text-red-400">
        <AlertTriangle className="w-12 h-12 mx-auto mb-3" />
        <p>Failed to load analysis: {error}</p>
      </div>
    );
  }

  const stats = [
    { label: "Periods", value: analysis.summary.periods.length, icon: Database, color: "text-blue-400" },
    { label: "Line Items", value: analysis.summary.line_item_count, icon: BarChart3, color: "text-emerald-400" },
    { label: "Ratios Computed", value: Object.keys(analysis.ratios).filter((k) => k !== "period").length, icon: Calculator, color: "text-yellow-400" },
    { label: "Trends Tracked", value: analysis.trends.length, icon: TrendingUp, color: "text-purple-400" },
    { label: "Anomalies Found", value: analysis.anomalies.length, icon: AlertTriangle, color: "text-red-400" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">{datasetName}</h2>
        <p className="text-gray-400 text-sm mt-1">
          {analysis.summary.periods.length} periods | {analysis.summary.line_item_count} line items
          {analysis.summary.categories.length > 0 && ` | Categories: ${analysis.summary.categories.join(", ")}`}
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {stats.map((s) => (
          <div key={s.label} className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] p-4">
            <div className="flex items-center gap-2 mb-2">
              <s.icon className={`w-4 h-4 ${s.color}`} />
              <span className="text-xs text-gray-400">{s.label}</span>
            </div>
            <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      <FinancialCharts analysis={analysis} />
    </div>
  );
}
