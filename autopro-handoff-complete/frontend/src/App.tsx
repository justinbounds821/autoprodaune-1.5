import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { lazy, Suspense, useEffect } from "react";
import { toast } from "sonner";
import api from "./services/autoproApi";

// lazy pages
const Index = lazy(() => import("./pages/Index"));
const Landing = lazy(() => import("./pages/Landing"));
const Community = lazy(() => import("./pages/Community"));
const Referral = lazy(() => import("./pages/Referral"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const GrowthDashboard = lazy(() => import("./pages/GrowthDashboard"));
const TrackPage = lazy(() => import("./pages/TrackPage"));
const NotFound = lazy(() => import("./pages/NotFound"));
const AdminApp = lazy(() => import("./pages/AdminApp"));

const queryClient = new QueryClient();
const Fallback = <div className="p-4 text-sm text-muted-foreground">Loading…</div>;

function HealthPing() {
  useEffect(() => {
    (async () => {
      try {
        await api.healthCheck();
      } catch (e: any) {
        toast.error("Backend indisponibil", {
          description: `Verifică http://127.0.0.1:8000/health • ${e?.message ?? ""}`,
        });
      }
    })();
  }, []);
  return null;
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <HealthPing />
        <Suspense fallback={Fallback}>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/index" element={<Index />} />
            <Route path="/community" element={<Community />} />
            <Route path="/referral" element={<Referral />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/growth" element={<GrowthDashboard />} />
            <Route path="/track/:leadId" element={<TrackPage />} />
            {/* Admin */}
            <Route path="/admin/*" element={<AdminApp />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
