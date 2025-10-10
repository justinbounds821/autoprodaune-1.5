import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import "./i18n";
import { ThemeProvider } from "./providers/theme-provider";

function ErrorBoundary({ children }: { children: React.ReactNode }) {
  const [err, setErr] = React.useState<Error | null>(null);
  React.useEffect(() => {
    const onErr = (e: ErrorEvent) => setErr(e.error ?? new Error(String(e.message)));
    window.addEventListener("error", onErr);
    window.addEventListener("unhandledrejection", (e) => setErr(new Error(String(e.reason))));
    return () => {
      window.removeEventListener("error", onErr);
      window.removeEventListener("unhandledrejection", onErr as any);
    };
  }, []);
  if (err) {
    return (
      <pre style={{ padding: 16, color: "#b91c1c", whiteSpace: "pre-wrap" }}>
        App crashed: {String(err.message)}
      </pre>
    );
  }
  return <>{children}</>;
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </ErrorBoundary>
  </StrictMode>
);
