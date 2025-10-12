import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
// bridge: BEGIN vite server
export default defineConfig(({ mode }) => ({
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  server: {
    host: true,
    port: 3006,
    strictPort: false,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
        secure: false,
        // Remove rewrite to keep /api prefix
      },
    },
  },
  preview: { port: 4173 },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Vendor chunks
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react-vendor';
            }
            if (id.includes('@radix-ui')) {
              return 'ui-vendor';
            }
            if (id.includes('recharts') || id.includes('lucide-react')) {
              return 'chart-vendor';
            }
            if (id.includes('@tanstack')) {
              return 'query-vendor';
            }
            return 'vendor';
          }
          
          // Feature chunks by path
          if (id.includes('/src/pages/Dashboard')) {
            return 'dashboard';
          }
          if (id.includes('/src/pages/AdminApp') || id.includes('/src/components/admin')) {
            return 'admin';
          }
          if (id.includes('/src/pages/VideoManagement')) {
            return 'video';
          }
          if (id.includes('/src/pages/AutomationControl')) {
            return 'automation';
          }
          if (id.includes('/src/pages/FinancialDashboard')) {
            return 'financial';
          }
          if (id.includes('/src/pages/SocialMedia')) {
            return 'social';
          }
          if (id.includes('/src/pages/LeadManagement')) {
            return 'leads';
          }
          if (id.includes('/src/components/ai-insights')) {
            return 'ai-insights';
          }
          if (id.includes('/src/components/AdvancedAnalytics')) {
            return 'analytics';
          }
        },
      },
    },
    chunkSizeWarningLimit: 1000, // Increase limit to 1MB
  },
}));
// bridge: END vite server
