"use client";

import { useRef, useState } from "react";
import { uploadDocument } from "@/lib/api";
import { UploadResponse } from "@/types";

const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"];
const ACCEPT = ".pdf,.docx,.txt,.md";

export default function UploadPanel() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function selectFile(f: File) {
    const ext = "." + (f.name.split(".").pop() ?? "").toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setError(
        `Unsupported file type "${ext}". Allowed: ${ALLOWED_EXTENSIONS.join(", ")}`
      );
      return;
    }
    setFile(f);
    setError(null);
    setResult(null);
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) selectFile(f);
  }

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await uploadDocument(file);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  const dropZoneClass = dragOver
    ? "border-indigo-400 bg-indigo-50"
    : "border-slate-200 hover:border-slate-300 hover:bg-slate-50";

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Upload form */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 className="font-semibold text-slate-900 mb-1">Upload Document</h3>
        <p className="text-sm text-slate-500 mb-5">
          Supported: PDF (text-native), DOCX, TXT, Markdown
        </p>

        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors mb-4 ${dropZoneClass}`}
          onClick={() => inputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
        >
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPT}
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) selectFile(f);
            }}
          />
          {file ? (
            <div>
              <p className="text-sm font-medium text-slate-900">{file.name}</p>
              <p className="text-xs text-slate-500 mt-1">
                {(file.size / 1024).toFixed(1)} KB
              </p>
              <button
                className="text-xs text-indigo-600 hover:text-indigo-700 mt-2 underline"
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                  setResult(null);
                  setError(null);
                }}
              >
                Remove
              </button>
            </div>
          ) : (
            <div>
              <p className="text-sm text-slate-500">
                Click to select or drag a file here
              </p>
              <p className="text-xs text-slate-400 mt-1">
                PDF · DOCX · TXT · MD
              </p>
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700 mb-4">
            {error}
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="w-full bg-indigo-600 text-white rounded-lg px-4 py-2.5 text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Uploading..." : "Upload Document"}
        </button>
      </div>

      {/* Result */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 className="font-semibold text-slate-900 mb-4">Upload Result</h3>

        {!result && !loading && (
          <div className="flex items-center justify-center h-48 text-slate-400 text-sm">
            Upload a document to see results here
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center h-48">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-sm text-slate-500">Processing document...</p>
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-4">
            <div className="flex gap-2 flex-wrap">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  result.extraction_status === "success"
                    ? "bg-green-100 text-green-700"
                    : "bg-amber-100 text-amber-700"
                }`}
              >
                {result.extraction_status === "success"
                  ? "Extracted"
                  : "Extraction failed"}
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                {result.file_type.toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {[
                {
                  label: "Text length",
                  value: result.text_length.toLocaleString() + " chars",
                },
                { label: "Chunks", value: String(result.chunk_count) },
                { label: "Embeddings", value: String(result.embedding_count) },
                {
                  label: "Vectors stored",
                  value: String(result.stored_vector_count),
                },
              ].map((stat) => (
                <div key={stat.label} className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500">{stat.label}</p>
                  <p className="text-sm font-semibold text-slate-900 mt-0.5">
                    {stat.value}
                  </p>
                </div>
              ))}
            </div>

            <div className="text-xs text-slate-500 bg-slate-50 rounded-lg px-3 py-2">
              {result.message}
            </div>

            {result.text_preview && (
              <div>
                <p className="text-xs font-medium text-slate-500 mb-1.5">
                  Text preview
                </p>
                <p className="text-xs text-slate-600 bg-slate-50 rounded-lg p-3 leading-relaxed line-clamp-4">
                  {result.text_preview}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
