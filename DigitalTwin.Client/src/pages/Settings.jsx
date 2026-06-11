import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Link, 
  Link2Off, 
  Trash2, 
  LogOut, 
  Globe, 
  ShieldAlert, 
  User, 
  HelpCircle,
  Database
} from 'lucide-react';
import { api } from '../api';
import { showToast } from '../components/Toast';

export default function Settings() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [googleConnected, setGoogleConnected] = useState(false);
  const [googleInfo, setGoogleInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchSettingsData = async () => {
    setLoading(true);
    try {
      const currentUser = api.auth.getCurrentUser();
      setUser(currentUser);

      const res = await api.action.google.status();
      setGoogleConnected(res.connected);
      setGoogleInfo(res);
    } catch (err) {
      console.warn('Failed to load Google link status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettingsData();
  }, []);

  const handleGoogleConnect = async () => {
    try {
      showToast('Initiating Google secure authentication...', 'info');
      const res = await api.action.google.connect(window.location.href);
      if (res.authorization_url) {
        // Redirect user to authorization URL
        window.location.href = res.authorization_url;
      } else {
        throw new Error('Google authorization URL not returned');
      }
    } catch (err) {
      showToast(err.message || 'Connection initiation failed', 'error');
    }
  };

  const handleGoogleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect Google services? This will disable inbox summaries and calendar scheduling.')) return;
    try {
      await api.action.google.disconnect();
      showToast('Google account disconnected successfully', 'success');
      window.dispatchEvent(new CustomEvent('google-auth-change'));
      fetchSettingsData();
    } catch (err) {
      showToast('Failed to disconnect Google account', 'error');
    }
  };

  const handleClearHistory = () => {
    if (!confirm('Clear all local AI command history logs permanently?')) return;
    localStorage.removeItem('dt_command_history');
    showToast('AI command logs cleared', 'success');
  };

  const handleLogout = () => {
    api.auth.logout();
    showToast('Logged out successfully', 'success');
    navigate('/login');
  };
  
  useEffect(() => {
  console.log('=== Settings State ===');
  console.log('user:', user);
  console.log('googleConnected:', googleConnected);
  console.log('googleInfo:', googleInfo);
  console.log('loading:', loading);
}, [user, googleConnected, googleInfo, loading]);

  return (
    <div style={{ animation: 'fadeIn 0.3s ease-out', flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
      
      {/* Top Banner Title */}
      <div style={{ marginBottom: '24px' }}>
        <span style={{ textTransform: 'uppercase', fontSize: '11px', letterSpacing: '0.1em', color: 'var(--primary)' }}>
          Environment Config
        </span>
        <h2 style={{ fontSize: '32px', margin: '4px 0 0 0' }}>Settings & Integrations</h2>
      </div>

      <div className="grid-2">
        
        {/* Google OAuth binding panel */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '18px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Globe size={20} color="var(--primary)" />
              Google Services Integration
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '24px' }}>
              Bind Google Gmail and Calendar OAuth permissions. Enables the Action Agent to coordinate emails and schedule meetings.
            </p>

            <div style={{ 
              background: 'rgba(255,255,255,0.01)',
              border: '1px solid var(--border)',
              borderRadius: '10px',
              padding: '16px 20px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {googleConnected ? (
                  <div style={{
                    width: '40px', height: '40px', borderRadius: '50%', background: 'rgba(0, 245, 160, 0.08)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <Link size={20} color="var(--success)" />
                  </div>
                ) : (
                  <div style={{
                    width: '40px', height: '40px', borderRadius: '50%', background: 'rgba(255, 140, 0, 0.08)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <Link2Off size={20} color="var(--warning)" />
                  </div>
                )}
                <div>
                  <span style={{ fontSize: '14px', fontWeight: 600 }}>Google Account Connection</span>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {googleConnected 
                      ? `Connected ${googleInfo?.is_mock ? '(Sandbox Mode)' : ''}` 
                      : 'Not Synced'}
                  </div>
                </div>
              </div>

              <span className={`badge ${googleConnected ? 'badge-success' : 'badge-warning'}`}>
                {googleConnected ? 'Linked' : 'Offline'}
              </span>
            </div>

            {googleConnected && googleInfo?.connected_at && (
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                🔑 Synced at: {new Date(googleInfo.connected_at).toLocaleString()}
              </div>
            )}
          </div>

          <div>
            {googleConnected ? (
              <button 
                onClick={handleGoogleDisconnect} 
                className="btn btn-danger"
                style={{ width: '100%' }}
              >
                Disconnect Google Account
              </button>
            ) : (
              <button 
                onClick={handleGoogleConnect} 
                className="btn btn-primary"
                style={{ width: '100%' }}
              >
                Authenticate with Google
              </button>
            )}
          </div>
        </div>

        {/* Account metadata panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <div className="glass-card">
            <h3 style={{ fontSize: '18px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <User size={18} color="var(--secondary)" />
              Account Identity Profile
            </h3>

            {user ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div className="flex-between" style={{ fontSize: '13px', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Secure User ID</span>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: '11px' }}>{user.user_id}</span>
                </div>
                <div className="flex-between" style={{ fontSize: '13px', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Registration Email</span>
                  <span>{user.email}</span>
                </div>
                <div className="flex-between" style={{ fontSize: '13px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Access Role</span>
                  <span className="badge badge-info">{user.role}</span>
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>No user credentials mapped.</div>
            )}

            <button 
              onClick={handleLogout} 
              className="btn btn-danger"
              style={{ width: '100%', marginTop: '20px', display: 'flex', justifyContent: 'center', gap: '8px' }}
            >
              <LogOut size={16} /> Sign Out from Twin
            </button>
          </div>

          <div className="glass-card">
            <h3 style={{ fontSize: '18px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Database size={18} color="var(--warning)" />
              Cache & Database Cleanup
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '16px' }}>
              Remove local storage browser caches and command records. Does not wipe MongoDB.
            </p>

            <button 
              onClick={handleClearHistory} 
              className="btn btn-secondary"
              style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '8px' }}
            >
              <Trash2 size={16} color="var(--danger)" /> Clear AI Command History
            </button>
          </div>

        </div>

      </div>

    </div>
  );
}
