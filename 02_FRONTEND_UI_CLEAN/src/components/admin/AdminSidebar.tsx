import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  BarChart3,
  Video,
  Settings,
  Share2,
  DollarSign,
  Users,
  Building2,
  Brain
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  {
    name: 'Overview',
    href: '/admin/dashboard',
    icon: BarChart3,
    description: 'System overview and metrics'
  },
  {
    name: 'Videos',
    href: '/admin/videos',
    icon: Video,
    description: 'Video generation and management'
  },
  {
    name: 'AI Insights',
    href: '/admin/insights',
    icon: Brain,
    description: 'AI-powered video insights and search'
  },
  {
    name: 'Automation',
    href: '/admin/automation',
    icon: Settings,
    description: 'Automation control and scheduling'
  },
  {
    name: 'Social',
    href: '/admin/social',
    icon: Share2,
    description: 'Social media management'
  },
  {
    name: 'Financial',
    href: '/admin/financial',
    icon: DollarSign,
    description: 'Revenue and financial dashboard'
  },
  {
    name: 'Leads',
    href: '/admin/leads',
    icon: Users,
    description: 'Lead management and tracking'
  }
];

const AdminSidebar: React.FC = () => {
  const location = useLocation();

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 text-white">
      {/* Logo/Brand */}
      <div className="flex items-center justify-center h-16 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Building2 className="w-8 h-8 text-blue-500" />
          <div>
            <h1 className="text-xl font-bold">AutoPro</h1>
            <p className="text-xs text-gray-400">Admin Panel</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="mt-8 px-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;

            return (
              <li key={item.name}>
                <NavLink
                  to={item.href}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-lg transition-colors hover:bg-gray-700 group',
                      isActive
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'text-gray-300 hover:text-white'
                    )
                  }
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-gray-400 group-hover:text-gray-300 truncate">
                      {item.description}
                    </div>
                  </div>
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* System Status */}
      <div className="absolute bottom-4 left-4 right-4">
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="text-xs">
              <div className="text-gray-400">System Status</div>
              <div className="flex items-center gap-2 mt-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-400 font-medium">Online</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminSidebar;