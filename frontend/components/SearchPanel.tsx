"use client";

import { useState } from "react";
import { searchDocuments } from "@/lib/api";
import { SearchResponse } from "@/types";

export default function SearchPanel() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await searchDocuments(query, topK);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  function handleTopKChange(e: React.ChangeEvent<HTMLInputElement>) {
    const raw = parseInt(e.target.value, 10);
    setTopK(Number.isNaN(raw) ? topK : Math.min(20, Math.max(1, raw)));
  }

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 className="font-semibold text-slate-900 mb-1">Semantic Search</h3>
        <p className="text-sm text-slate-500 mb-5">
          Find relevant document chunks by meaning — no exact keyword match
          needed.
        </p>

        <form onSubmit={handleSearch} className="flex gap-3 flex-wrap">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your documents..."
            className="flex-1 min-w-0 border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <input
            type="number"
            min={1}
            max={20}
            value={topK}
            onChange={handleTopKChange}
            title="Top-K results (1–20)"
            className="w-20 border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-center text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={!query.trim() || loading}
            className="bg-indigo-600 text-white rounded-lg px-5 py-2.5 text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </form>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700 mt-4">
            {error}
          </div>
        )}
      </div>

      {!result && !loading && (
        <div className="bg-white border border-slate-200 rounded-xl p-12 shadow-sm text-center text-slate-400 text-sm">
          Enter a search query to find relevant document chunks
        </div>
      )}

      {loading && (
        <div className="bg-white border border-slate-200 rounded-xl p-12 shadow-sm flex items-center justify-center">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-slate-500">Searching...</p>
          </div>
        </div>
      )}

      {result && (
        <div>
          <p className="text-sm font-medium text-slate-600 mb-3">
            {result.results.length === 0
              ? "No results found"
              : `${result.results.length} result${result.results.length !== 1 ? "s" : ""} for "${result.query}"`}
          </p>

          {result.results.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-12 shadow-sm text-center text-slate-400 text-sm">
              No matching chunks found. Try uploading documents first.
            </div>
          ) : (
            <div className="space-y-3">
              {result.results.map((r, i) => (
                <div
                  key={`${r.document_id}-${r.chunk_index}`}
                  className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm"
                >
                  <div className="flex items-center gap-3 mb-3 flex-wrap">
                    <span className="text-xs font-medium text-slate-400 tabular-nums">
                      #{i + 1}
                    </span>
                    <span className="text-sm font-medium text-slate-900 truncate max-w-[240px]">
                      {r.original_filename}
                    </span>
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600">
                      {r.file_type.toUpperCase()}
                    </span>
                    <span className="text-xs text-slate-400">
                      chunk {r.chunk_index}
                    </span>
                    <div className="ml-auto flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-500 rounded-full"
                          style={{ width: `${Math.round(r.score * 100)}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-500 tabular-nums">
                        {(r.score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed line-clamp-3">
                    {r.chunk_text}
                  </p>
                  <div className="flex items-center gap-3 mt-3 pt-3 border-t border-slate-50">
                    <span className="text-xs text-slate-400">
                      {r.word_count} words
                    </span>
                    <span className="text-xs text-slate-400">
                      {r.character_count} chars
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
