"use client";

import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api";
import { HealthResponse } from "@/types";

type Status = "loading" | "online" | "offline";

export default function ApiStatus() {
  const [status, setStatus] = useState<Status>("loading");
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    checkHealth()
      .then((data) => {
        setHealth(data);
        setStatus("online");
      })
      .catch(() => setStatus("offline"));
  }, []);

  const dotClass =
    status === "loading"
      ? "bg-slate-300 animate-pulse"
      : status === "online"
        ? "bg-green-500"
        : "bg-red-500";

  const label =
    status === "loading"
      ? "Checking backend..."
      : status === "online"
        ? `Backend online · v${health?.version}`
        : "Backend offline";

  return (
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${dotClass}`} />
      <span className="text-sm text-slate-500">{label}</span>
    </div>
  );
}
