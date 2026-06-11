import { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Terminal, 
  HeartPulse, 
  Cpu, 
  Settings as SettingsIcon, 
  LogOut, 
  ChevronLeft, 
  ChevronRight, 
  Layers,
  Link,
  Link2Off
} from 'lucide-react';
import { api } from '../api';
import { showToast } from './Toast';

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [googleConnected, setGoogleConnected] = useState(false);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Get user from local storage
    const currentUser = api.auth.getCurrentUser();
    setUser(currentUser);

    // Fetch Google integration status
    const checkGoogle = async () => {
      try {
        if (currentUser) {
          const res = await api.action.google.status();
          setGoogleConnected(res.connected);
        }
      } catch (err) {
        console.error('Failed to get Google status', err);
      }
    };

    checkGoogle();
    
    // Subscribe to Google connection state changes
    const handleGoogleUpdate = () => checkGoogle();
    window.addEventListener('google-auth-change', handleGoogleUpdate);
    return () => window.removeEventListener('google-auth-change', handleGoogleUpdate);
  }, []);

  const handleLogout = () => {
    api.auth.logout();
    showToast('Logged out successfully', 'success');
    navigate('/login');
  };

  const navItems = [
    { to: '/', name: 'Dashboard', icon: LayoutDashboard },
    { to: '/command', name: 'Command Center', icon: Terminal },
    { to: '/health', name: 'Health Intel', icon: HeartPulse },
    { to: '/automate', name: 'Automation Hub', icon: Cpu },
    { to: '/settings', name: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      {/* Brand Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: isCollapsed ? 'center' : 'space-between',
        marginBottom: '32px',
        padding: '0 8px'
      }}>
        {!isCollapsed && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers color="var(--primary)" size={24} style={{ filter: 'drop-shadow(0 0 6px var(--primary))' }} />
            <span style={{ 
              fontFamily: 'var(--font-display)', 
              fontWeight: 700, 
              fontSize: '18px',
              background: 'linear-gradient(to right, var(--primary), var(--secondary))',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '-0.03em'
            }}>
              Digital Twin AI
            </span>
          </div>
        )}
        {isCollapsed && (
          <Layers color="var(--primary)" size={24} style={{ filter: 'drop-shadow(0 0 6px var(--primary))' }} />
        )}
        
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            marginLeft: isCollapsed ? '0' : '8px'
          }}
        >
          {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Nav Links */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px', flexGrow: 1 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: 500,
                color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                background: isActive ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
                border: isActive ? '1px solid rgba(0, 212, 255, 0.15)' : '1px solid transparent',
                transition: 'all 0.2s ease',
                justifyContent: isCollapsed ? 'center' : 'flex-start',
                position: 'relative'
              })}
              title={isCollapsed ? item.name : ''}
            >
              <Icon size={18} />
              {!isCollapsed && <span>{item.name}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* Google Integration Badge */}
      <div style={{
        margin: '16px 0',
        padding: '12px 8px',
        background: 'rgba(255,255,255,0.02)',
        borderRadius: '8px',
        border: '1px solid var(--border)',
        display: isCollapsed ? 'none' : 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {googleConnected ? (
            <>
              <Link size={14} color="var(--success)" />
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Google Account</span>
            </>
          ) : (
            <>
              <Link2Off size={14} color="var(--warning)" />
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>No Google Sync</span>
            </>
          )}
        </div>
        <span style={{ 
          fontSize: '9px',
          fontWeight: 600,
          color: googleConnected ? 'var(--success)' : 'var(--warning)',
          textTransform: 'uppercase'
        }}>
          {googleConnected ? 'Active' : 'Offline'}
        </span>
      </div>

      {/* User Info & Logout */}
      <div style={{
        borderTop: '1px solid var(--border)',
        paddingTop: '16px',
        display: 'flex',
        flexDirection: isCollapsed ? 'column' : 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
        width: '100%'
      }}>
        {!isCollapsed && user && (
          <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', flexGrow: 1 }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {user.email}
            </span>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Twin Active
            </span>
          </div>
        )}

        <button
          onClick={handleLogout}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--danger)',
            cursor: 'pointer',
            padding: '8px',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'background 0.2s',
          }}
          title="Sign Out"
        >
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  );
}
