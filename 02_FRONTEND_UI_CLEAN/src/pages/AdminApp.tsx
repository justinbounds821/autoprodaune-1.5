import React, { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { Toaster as Sonner } from '@/components/ui/sonner';
import { TooltipProvider } from '@/components/ui/tooltip';
import AdminLayout from '../components/admin/AdminLayout';
import AdminLogin from '../components/admin/AdminLogin';
import Dashboard from './Dashboard';
import VideoManagement from './VideoManagement';
import AutomationControl from './AutomationControl';
import SocialMedia from './SocialMedia';
import FinancialDashboard from './FinancialDashboard';
import LeadManagement from './LeadManagement';
import NotificationSettings from './NotificationSettings';

const queryClient = new QueryClient();

const AdminApp: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    // Check if admin is already logged in
    return localStorage.getItem('adminAuth') === 'authenticated';
  });

  const handleLogin = () => {
    localStorage.setItem('adminAuth', 'authenticated');
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('adminAuth');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return (
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <AdminLogin onLogin={handleLogin} />
        </TooltipProvider>
      </QueryClientProvider>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <AdminLayout onLogout={handleLogout}>
          {/* IMPORTANT: rutele sunt RELATIVE la /admin/* */}
          <Routes>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="videos" element={<VideoManagement />} />
            <Route path="automation" element={<AutomationControl />} />
            <Route path="social" element={<SocialMedia />} />
            <Route path="notifications" element={<NotificationSettings />} />
            <Route path="financial" element={<FinancialDashboard />} />
            <Route path="leads" element={<LeadManagement />} />
            <Route path="*" element={<Navigate to="dashboard" replace />} />
          </Routes>
        </AdminLayout>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

// Admin-specific dashboard overview (separate from public dashboard)
const AdminDashboard = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">AutoPro Daune Admin</h1>
        <p className="text-muted-foreground">Complete automation system overview</p>
      </div>
      <Dashboard />
    </div>
  );
};

export default AdminApp;
