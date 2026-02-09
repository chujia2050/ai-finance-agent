"use client";

import { useState, useEffect } from "react";
import { Bot, BarChart3, Upload, Database, ChevronRight } from "lucide-react";
import FileUpload from "@/components/FileUpload";
import Dashboard from "@/components/Dashboard";
import ChatInterface from "@/components/ChatInterface";
import { getDatasets } from "@/lib/api";
import type { Dataset, UploadResponse } from "@/types";

type Tab = "dashboard" | "chat";

export default function Home() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [activeDataset, setActiveDataset] = useState<{ id: number; name: string } | null>(null);
  const [tab, setTab] = useState<Tab>("dashboard");
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    getDatasets()
      .then((data) => setDatasets(data as Dataset[]))
      .catch(() => {});
  }, []);

  const handleUpload = (data: UploadResponse) => {
    setActiveDataset({ id: data.dataset_id, name: data.name });
    setShowUpload(false);
    setTab("dashboard");
    getDatasets()
      .then((d) => setDatasets(d as Dataset[]))
      .catch(() => {});
  };

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-[var(--card)] border-r border-[var(--card-border)] flex flex-col">
        <div className="p-4 border-b border-[var(--card-border)]">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-sm">AI Finance Agent</h1>
              <p className="text-xs text-gray-500">Powered by LangChain</p>
            </div>
          </div>
        </div>

        <div className="p-3">
          <button
            onClick={() => setShowUpload(true)}
            className="w-full flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
          >
            <Upload className="w-4 h-4" />
            Upload Data
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          <p className="text-xs text-gray-500 uppercase tracking-wide px-2 mb-2">Datasets</p>
          {datasets.length === 0 && (
            <p className="text-xs text-gray-600 px-2">No datasets yet. Upload a file to get started.</p>
          )}
          {datasets.map((ds) => (
            <button
              key={ds.id}
              onClick={() => {
                setActiveDataset({ id: ds.id, name: ds.name });
                setShowUpload(false);
                setTab("dashboard");
              }}
              className={`w-full text-left flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                activeDataset?.id === ds.id
                  ? "bg-blue-600/20 text-blue-400"
                  : "hover:bg-gray-800 text-gray-300"
              }`}
            >
              <Database className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">{ds.name}</span>
              <ChevronRight className="w-3 h-3 ml-auto flex-shrink-0 opacity-50" />
            </button>
          ))}
        </div>

        <div className="p-3 border-t border-[var(--card-border)] text-xs text-gray-600">
          FastAPI + LangChain + Next.js
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen">
        {/* Top bar with tabs */}
        {activeDataset && (
          <div className="border-b border-[var(--card-border)] px-6 flex items-center gap-1">
            <button
              onClick={() => setTab("dashboard")}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === "dashboard"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              <span className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Dashboard
              </span>
            </button>
            <button
              onClick={() => setTab("chat")}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === "chat"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              <span className="flex items-center gap-2">
                <Bot className="w-4 h-4" />
                AI Agent Chat
              </span>
            </button>
          </div>
        )}

        <div className="flex-1 p-6 overflow-y-auto">
          {showUpload ? (
            <div className="max-w-xl mx-auto mt-12">
              <h2 className="text-2xl font-bold mb-2">Upload Financial Data</h2>
              <p className="text-gray-400 mb-6">
                Upload a CSV or Excel file containing financial statements,
                income statements, or balance sheet data.
              </p>
              <FileUpload onUploadSuccess={handleUpload} />
            </div>
          ) : activeDataset ? (
            tab === "dashboard" ? (
              <Dashboard datasetId={activeDataset.id} datasetName={activeDataset.name} />
            ) : (
              <div className="h-[calc(100vh-8rem)]">
                <ChatInterface datasetId={activeDataset.id} datasetName={activeDataset.name} />
              </div>
            )
          ) : (
            /* Landing */
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 bg-blue-600/20 rounded-2xl flex items-center justify-center mb-6">
                <Bot className="w-10 h-10 text-blue-400" />
              </div>
              <h2 className="text-3xl font-bold mb-3">AI Finance Agent</h2>
              <p className="text-gray-400 max-w-md mb-8">
                Upload your financial data and let an autonomous AI agent analyze it.
                Compute ratios, detect trends, find anomalies, and get insights through natural language.
              </p>
              <button
                onClick={() => setShowUpload(true)}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                <Upload className="w-5 h-5" />
                Get Started
              </button>
              <div className="grid grid-cols-3 gap-8 mt-16 max-w-2xl">
                {[
                  { icon: BarChart3, title: "Financial Analysis", desc: "Auto-compute ratios, margins, and key metrics" },
                  { icon: Bot, title: "AI Agent Chat", desc: "Ask questions in natural language about your data" },
                  { title: "Anomaly Detection", desc: "Statistical detection of outliers and red flags", icon: () => <span className="text-lg">!</span> },
                ].map((f, i) => (
                  <div key={i} className="text-center">
                    <div className="w-12 h-12 bg-gray-800 rounded-xl flex items-center justify-center mx-auto mb-3">
                      {typeof f.icon === "function" ? <f.icon /> : <f.icon className="w-6 h-6 text-gray-400" />}
                    </div>
                    <h3 className="font-medium text-sm">{f.title}</h3>
                    <p className="text-xs text-gray-500 mt-1">{f.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
