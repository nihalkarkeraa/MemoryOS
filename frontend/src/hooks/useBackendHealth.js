import { useState, useEffect, useRef } from "react";
import { checkHealth } from "@/services/api";

// Polls GET /health and reports real backend availability.
// status: "unknown" | "connected" | "unavailable"
export function useBackendHealth(intervalMs = 30000) {
  const [status, setStatus] = useState("unknown");
  const timerRef = useRef(null);

  useEffect(() => {
    let active = true;

    const run = async () => {
      const ok = await checkHealth();
      if (active) setStatus(ok ? "connected" : "unavailable");
    };

    run();
    timerRef.current = setInterval(run, intervalMs);

    return () => {
      active = false;
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [intervalMs]);

  return status;
}