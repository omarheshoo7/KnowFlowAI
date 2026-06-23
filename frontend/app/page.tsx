"use client";

import { useState } from "react";
import ApiStatus from "@/components/ApiStatus";
import ChatPanel from "@/components/ChatPanel";
import SearchPanel from "@/components/SearchPanel";
import UploadPanel from "@/components/UploadPanel";

type Tab = "upload" | "chat" | "search";

const TABS: { id: Tab; label: string }[] = [
  { id: "upload", label: "Upload" },
  { id: "chat", label: "Chat" },
  { id: "search", label: "Search" },
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<Tab>("upload");

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="text-white text-sm font-bold">K</span>
            </div>
            <div>
              <h1 className="font-semibold text-slate-900 text-sm leading-none">
                KnowFlow AI
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Document Intelligence Platform
              </p>
            </div>
          </div>
          <ApiStatus />
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-slate-900">Dashboard</h2>
          <p className="text-slate-500 mt-1">
            Upload documents, ask questions, and search your knowledge base.
          </p>
        </div>

        <div className="flex gap-1 bg-slate-100 p-1 rounded-lg w-fit mb-6">
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`px-5 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === id
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {activeTab === "upload" && <UploadPanel />}
        {activeTab === "chat" && <ChatPanel />}
        {activeTab === "search" && <SearchPanel />}
      </main>
    </div>
  );
}
