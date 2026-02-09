"use client";

import { useState, useCallback } from "react";
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle } from "lucide-react";
import { uploadFile } from "@/lib/api";
import type { UploadResponse } from "@/types";

interface FileUploadProps {
  onUploadSuccess: (data: UploadResponse) => void;
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleFile = useCallback(
    async (file: File) => {
      setError(null);
      setSuccess(false);

      const ext = file.name.split(".").pop()?.toLowerCase();
      if (!["csv", "xlsx", "xls"].includes(ext || "")) {
        setError("Please upload a CSV or Excel file.");
        return;
      }

      setUploading(true);
      try {
        const data = await uploadFile(file);
        setSuccess(true);
        onUploadSuccess(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setUploading(false);
      }
    },
    [onUploadSuccess]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`
        border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200
        ${dragging
          ? "border-blue-500 bg-blue-500/10"
          : "border-gray-700 hover:border-gray-500"
        }
      `}
    >
      <div className="flex flex-col items-center gap-3">
        {success ? (
          <CheckCircle className="w-12 h-12 text-emerald-500" />
        ) : error ? (
          <AlertCircle className="w-12 h-12 text-red-500" />
        ) : (
          <FileSpreadsheet className="w-12 h-12 text-gray-400" />
        )}

        <div>
          <p className="text-lg font-medium">
            {uploading
              ? "Uploading..."
              : success
              ? "Upload successful!"
              : "Drop your financial data here"}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            CSV or Excel files with financial statements
          </p>
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        {!uploading && !success && (
          <label className="mt-2 cursor-pointer">
            <span className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors inline-flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Browse Files
            </span>
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFile(file);
              }}
            />
          </label>
        )}
      </div>
    </div>
  );
}
