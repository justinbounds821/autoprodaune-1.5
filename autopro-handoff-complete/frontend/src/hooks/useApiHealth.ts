// bridge: BEGIN health hook
import { useEffect, useState } from "react";
import { ping } from "../lib/api";

export function useApiHealth(pollMs = 10000) {
  const [ok, setOk] = useState<boolean | null>(null);
  const [last, setLast] = useState<string>("");

  useEffect(() => {
    let t: any;
    const run = async () => {
      try {
        const r = await ping();
        setOk(true);
        setLast(new Date().toLocaleTimeString());
      } catch {
        setOk(false);
      }
      t = setTimeout(run, pollMs);
    };
    run();
    return () => clearTimeout(t);
  }, [pollMs]);

  return { ok, last };
}
// bridge: END health hook