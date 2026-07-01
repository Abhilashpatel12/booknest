import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Book, Library, Users, LogOut, Home, Bell } from 'lucide-react';
import { useWebSocket } from '../context/WebSocketContext';

export default function Layout() {
  const { user, logout } = useAuth();
  const { isConnected } = useWebSocket();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: Home },
    { name: 'My Books', path: '/books', icon: Book },
    { name: 'Shelves', path: '/shelves', icon: Library },
    { name: 'Borrowed', path: '/borrowed', icon: Users },
  ];

  return (
    <div className="layout-wrapper">
      {/* Sidebar */}
      <div className="layout-sidebar">
        <div style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ background: 'var(--primary)', padding: '8px', borderRadius: '8px', display: 'flex' }}>
            <Book size={24} color="var(--bg-color)" />
          </div>
          <span style={{ fontSize: '20px', fontWeight: '700', letterSpacing: '-0.5px' }}>BookNest</span>
        </div>
        
        <nav style={{ flex: 1, padding: '12px' }}>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link 
                key={item.path} 
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-md)',
                  color: isActive ? 'white' : 'var(--text-muted)',
                  background: isActive ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
                  textDecoration: 'none',
                  fontWeight: isActive ? '500' : '400',
                  marginBottom: '4px',
                  transition: 'var(--transition)'
                }}
                onMouseOver={(e) => { if (!isActive) e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)' }}
                onMouseOut={(e) => { if (!isActive) e.currentTarget.style.background = 'transparent' }}
              >
                <Icon size={20} color={isActive ? 'var(--primary)' : 'currentColor'} />
                {item.name}
              </Link>
            );
          })}
        </nav>
        
        <div style={{ padding: '24px', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: 'var(--text-muted)' }}>
              <div style={{ 
                width: '8px', height: '8px', borderRadius: '50%', 
                background: isConnected ? 'var(--success)' : 'var(--danger)' 
              }} />
              {isConnected ? 'Live' : 'Disconnected'}
            </div>
          </div>
          <div style={{ fontSize: '14px', fontWeight: '500', marginBottom: '12px' }}>{user?.name}</div>
          <button 
            onClick={handleLogout} 
            className="btn" 
            style={{ width: '100%', justifyContent: 'flex-start', color: 'var(--danger)', background: 'rgba(239, 68, 68, 0.1)' }}
          >
            <LogOut size={16} /> Sign out
          </button>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="layout-main">
        <div className="layout-scroll-area">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
