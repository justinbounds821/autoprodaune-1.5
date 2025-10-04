import React from 'react';
import { Link } from 'react-router-dom';
import { Phone, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import autopro_logo from '@/assets/autopro-logo.png';

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <img 
              src={autopro_logo} 
              alt="AutoPro Daune Logo" 
              className="h-10 w-auto"
            />
            <div>
              <h1 className="text-xl font-bold text-primary">AutoPro Daune</h1>
              <p className="text-xs text-muted-foreground">Expert în evaluări auto</p>
            </div>
          </Link>

          {/* Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link 
              to="/" 
              className="text-foreground hover:text-primary transition-colors"
            >
              Acasă
            </Link>
            <Link 
              to="/track/demo" 
              className="text-foreground hover:text-primary transition-colors"
            >
              Urmărește Status
            </Link>
            <div className="flex items-center space-x-2 text-sm">
              <Phone className="w-4 h-4 text-primary" />
              <a 
                href="tel:+40747694114" 
                className="text-primary font-medium hover:text-primary-dark"
              >
                0747.694.114
              </a>
            </div>
          </div>

          {/* Admin Access */}
          <Link to="/dashboard">
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;