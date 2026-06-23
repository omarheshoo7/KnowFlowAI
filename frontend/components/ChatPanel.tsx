"use client";

import { useState } from "react";
import { chatWithDocuments } from "@/lib/api";
import { ChatResponse } from "@/types";

export default function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await chatWithDocuments(question, topK);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat request failed");
    } finally {
      setLoading(false);
    }
  }

  function handleTopKChange(e: React.ChangeEvent<HTMLInputElement>) {
    const raw = parseInt(e.target.value, 10);
    setTopK(Number.isNaN(raw) ? topK : Math.min(20, Math.max(1, raw)));
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Input form */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 className="font-semibold text-slate-900 mb-1">Ask a Question</h3>
        <p className="text-sm text-slate-500 mb-5">
          Get a grounded AI answer with citations from your uploaded documents.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1.5">
              Question
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What is the refund policy?"
              rows={4}
              className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1.5">
              Top-K chunks (1–20)
            </label>
            <input
              type="number"
              min={1}
              max={20}
              value={topK}
              onChange={handleTopKChange}
              className="w-24 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={!question.trim() || loading}
            className="w-full bg-indigo-600 text-white rounded-lg px-4 py-2.5 text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Thinking..." : "Ask Question"}
          </button>
        </form>
      </div>

      {/* Answer */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 className="font-semibold text-slate-900 mb-4">Answer</h3>

        {!result && !loading && (
          <div className="flex items-center justify-center h-52 text-slate-400 text-sm">
            Ask a question to see the AI answer here
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center h-52">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-sm text-slate-500">Generating answer...</p>
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-xs text-slate-500">
                {result.retrieval_count} chunk
                {result.retrieval_count !== 1 ? "s" : ""} retrieved
              </span>
              {result.citations.length > 0 && (
                <div className="flex gap-1.5 flex-wrap">
                  {result.citations.map((c) => (
                    <span
                      key={c}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-indigo-100 text-indigo-700"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="text-sm text-slate-700 leading-relaxed bg-slate-50 rounded-lg p-4">
              {result.answer}
            </div>

            {result.sources.length > 0 && (
              <div>
                <p className="text-xs font-medium text-slate-500 mb-2">
                  Sources
                </p>
                <div className="space-y-2">
                  {result.sources.map((src) => (
                    <div
                      key={src.source_id}
                      className="border border-slate-100 rounded-lg p-3"
                    >
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-bold bg-indigo-100 text-indigo-700">
                          {src.source_id}
                        </span>
                        <span className="text-xs font-medium text-slate-700 truncate max-w-[160px]">
                          {src.original_filename}
                        </span>
                        <span className="text-xs text-slate-400">
                          chunk {src.chunk_index}
                        </span>
                        <span className="ml-auto text-xs text-slate-400">
                          {(src.score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
                        {src.chunk_text_preview}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
