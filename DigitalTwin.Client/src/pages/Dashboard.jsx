import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  HeartPulse, 
  Calendar, 
  Bell, 
  Mail, 
  Cpu, 
  Terminal, 
  ArrowRight,
  Database,
  RefreshCw
} from 'lucide-react';
import { api } from '../api';
import { showToast } from '../components/Toast';

export default function Dashboard() {
  const navigate = useNavigate();
  const [healthData, setHealthData] = useState(null);
  const [calendarEvents, setCalendarEvents] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [draftCount, setDraftCount] = useState(0);
  const [loading, setLoading] = useState(true);

  // AI Shortcut state
  const [command, setCommand] = useState('');
  const [commandResult, setCommandResult] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [userFullName, setUserFullName] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const fullName = await api.auth.getUserFullName();
      setUserFullName(fullName);
      localStorage.setItem("userFullName", fullName);
      console.log('Fetched user full name from API:', fullName);

    } catch (e) {
      console.warn('Failed to load user full name:', e);
      setUserFullName('');
    }
    try {
      // Fetch health stats
      try {
        const healthStats = await api.healthDocs.dashboard();
        console.log('Loaded health dashboard stats:', healthStats);
        setHealthData(healthStats);
      } catch (e) {
        console.warn('Could not load health dashboard stats:', e);
      }

      // Fetch calendar events
      try {
        const start = new Date().toISOString();
      // const end = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();
        const cal = await api.action.calendar.events(start);
        setCalendarEvents(cal.events ? cal.events.slice(0, 3) : []);
      } catch (e) {
        console.warn('Could not load calendar events (often due to Google unlinked):', e);
      }

      // Fetch notifications
      try {
        const notifs = await api.action.notifications.list();
        setNotifications(notifs.notifications ? notifs.notifications.slice(0, 3) : []);
      } catch (e) {
        console.warn('Could not load notifications:', e);
      }

      // Fetch drafts
      try {
        const drafts = await api.action.emails.drafts();
        setDraftCount(drafts.drafts ? drafts.drafts.length : 0);
      } catch (e) {
        console.warn('Could not load drafts:', e);
      }

    } catch (err) {
      showToast('Error loading some dashboard widgets', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCommandSubmit = async (e) => {
    e.preventDefault();
    if (!command.trim()) return;

    setExecuting(true);
    setCommandResult(null);
    try {
      const res = await api.action.execute(command);
      setCommandResult(res);
      showToast('Command executed successfully', 'success');
      
      // Save query history locally
      const storedHistory = JSON.parse(localStorage.getItem('dt_command_history') || '[]');
      const newEntry = {
        query: command,
        timestamp: new Date().toISOString(),
        result: res
      };
      localStorage.setItem('dt_command_history', JSON.stringify([newEntry, ...storedHistory].slice(0, 10)));

      setCommand('');
      // Refresh dashboard info
      fetchData();
    } catch (err) {
      showToast(err.message || 'Execution error', 'error');
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div style={{ animation: 'fadeIn 0.3s ease-out', flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
      {/* Top Banner Greeting */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <span style={{ textTransform: 'uppercase', fontSize: '11px', letterSpacing: '0.1em', color: 'var(--primary)' }}>
            {userFullName}'s Digital Twin status
          </span>
          <h2 style={{ fontSize: '32px', margin: '4px 0 0 0' }}>Mission Control</h2>
        </div>
        <button 
          onClick={fetchData} 
          disabled={loading} 
          className="btn btn-secondary" 
          style={{ padding: '8px 12px', display: 'flex', gap: '6px' }}
        >
          <RefreshCw size={14} className={loading ? 'spinning' : ''} />
          Sync
        </button>
      </div>

      {/* Main Pulse / Orb Greeting Section */}
      <div className="glass-card" style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '36px',
        marginBottom: '28px',
        background: 'radial-gradient(circle at center, rgba(123, 97, 255, 0.05) 0%, rgba(255,255,255,0.02) 100%)',
        textAlign: 'center'
      }}>
        <div className="ai-orb-container">
          <div className="ai-orb" />
        </div>
        
        <h1 style={{ 
          fontSize: '28px', 
          fontWeight: 700, 
          letterSpacing: '-0.02em', 
          marginBottom: '8px',
          fontFamily: 'var(--font-display)' 
        }}>
          Your Digital Twin is Active
        </h1>
        <p style={{ color: 'var(--text-muted)', maxWidth: '480px', fontSize: '14px', marginBottom: '0' }}>
          Monitoring life events, parsing email communications, and evaluating bio-metrics recursively.
        </p>
      </div>

      {/* Grid widgets */}
      <div className="grid-3" style={{ marginBottom: '24px' }}>
        
        {/* Widget: Health Snapshot */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '180px' }}>
          <div>
            <div className="flex-between" style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <HeartPulse size={18} color="var(--danger)" />
                Health Snapshot
              </h3>
              <span className="badge badge-info">Agent Active</span>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', margin: '8px 0' }}>
              <div className="flex-between">
                <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Abnormalities</span>
                <span style={{ fontSize: '16px', fontWeight: 'bold', color: healthData?.anomaly_count > 0 ? 'var(--warning)' : 'var(--success)' }}>
                  {healthData?.anomaly_count ?? 0} Detected
                </span>
              </div>
              <div className="flex-between">
                <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Reports Analysed</span>
                <span style={{ fontSize: '14px', fontWeight: '600' }}>
                  {healthData?.analyzed_reports ?? 0} Documents
                </span>
              </div>
            </div>
          </div>
          
          <button 
            onClick={() => navigate('/health')}
            className="btn btn-secondary" 
            style={{ padding: '8px 12px', fontSize: '12px', width: '100%', marginTop: '16px', display: 'flex', justifyContent: 'center', gap: '6px' }}
          >
            Open Health Panel <ArrowRight size={14} />
          </button>
        </div>

        {/* Widget: Calendar events */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '180px' }}>
          <div>
            <div className="flex-between" style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Calendar size={18} color="var(--primary)" />
                Schedule
              </h3>
              <span className="badge badge-success">Synced</span>
            </div>
            
            {calendarEvents.length === 0 ? (
              <div style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '12px 0' }}>
                No upcoming events found. Connect google accounts or check calendar.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {calendarEvents.map((evt) => (
                  <div key={evt._id || evt.id} style={{ display: 'flex', flexDirection: 'column', padding: '6px 8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', borderLeft: '2px solid var(--primary)' }}>
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {evt.title || evt.summary}
                    </span>
                    <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                      {new Date(evt.start?.dateTime || evt.start).toLocaleString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <button 
            onClick={() => navigate('/automate?tab=calendar')}
            className="btn btn-secondary" 
            style={{ padding: '8px 12px', fontSize: '12px', width: '100%', marginTop: '16px', display: 'flex', justifyContent: 'center', gap: '6px' }}
          >
            Manage Events <ArrowRight size={14} />
          </button>
        </div>

        {/* Widget: Unread Notifications */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '180px' }}>
          <div>
            <div className="flex-between" style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Bell size={18} color="var(--secondary)" />
                AI Alerts
              </h3>
              {notifications.length > 0 && (
                <span className="badge badge-danger" style={{ textShadow: 'none' }}>
                  {notifications.length} Alerts
                </span>
              )}
            </div>

            {notifications.length === 0 ? (
              <div style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '12px 0' }}>
                No pending critical warnings or system notifications.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {notifications.map((n) => (
                  <div key={n.id || n._id} style={{ display: 'flex', gap: '6px', fontSize: '12px', padding: '6px', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border)', borderRadius: '6px' }}>
                    <span style={{ 
                      width: '6px', 
                      height: '6px', 
                      borderRadius: '50%', 
                      background: n.level === 'critical' ? 'var(--danger)' : n.level === 'warning' ? 'var(--warning)' : 'var(--primary)',
                      alignSelf: 'center'
                    }} />
                    <span style={{ flexGrow: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {n.message}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button 
            onClick={() => navigate('/automate?tab=notifications')}
            className="btn btn-secondary" 
            style={{ padding: '8px 12px', fontSize: '12px', width: '100%', marginTop: '16px', display: 'flex', justifyContent: 'center', gap: '6px' }}
          >
            Alert Center <ArrowRight size={14} />
          </button>
        </div>

      </div>

      {/* Lower Row: AI Shortcut & Stats */}
      <div className="grid-2-1" style={{ flexGrow: 1 }}>
        
        {/* AI Command Box Shortcut */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '18px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Terminal size={20} color="var(--primary)" />
              Direct Action Input
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '20px' }}>
              Dispatch a prompt to the Action Agent. Creates emails drafts, logs events, or schedules details immediately.
            </p>

            <form onSubmit={handleCommandSubmit} style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
              <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="e.g. 'Draft email to doctor' or 'Schedule gym tomorrow at 9am'"
                style={{ flexGrow: 1 }}
                disabled={executing}
              />
              <button 
                type="submit" 
                className="btn btn-primary" 
                disabled={executing || !command.trim()}
                style={{ padding: '0 20px' }}
              >
                {executing ? 'Parsing...' : 'Run'}
              </button>
            </form>

            {commandResult && (
              <div className="glass-card" style={{ 
                padding: '16px', 
                background: 'rgba(0, 212, 255, 0.02)', 
                border: '1px solid rgba(0, 212, 255, 0.15)',
                animation: 'fadeIn 0.2s ease-out'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--primary)' }}>
                    Intent parsed: {commandResult.intent?.type || 'query'}
                  </span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Action Complete</span>
                </div>
                <pre style={{ 
                  fontFamily: 'var(--mono)', 
                  fontSize: '11px', 
                  color: 'var(--text-primary)', 
                  margin: 0, 
                  whiteSpace: 'pre-wrap',
                  maxHeight: '120px',
                  overflowY: 'auto'
                }}>
                  {JSON.stringify(commandResult.result || commandResult, null, 2)}
                </pre>
              </div>
            )}
          </div>

          <button 
            onClick={() => navigate('/command')}
            className="btn btn-secondary" 
            style={{ width: 'fit-content', padding: '8px 16px', fontSize: '12px', display: 'flex', gap: '6px', marginTop: '16px' }}
          >
            Open Advanced Interface <Terminal size={14} />
          </button>
        </div>

        {/* Database & Email Draft summary */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '20px' }}>
            <div style={{
              width: '45px', height: '45px', borderRadius: '10px', background: 'rgba(0, 245, 160, 0.08)',
              border: '1px solid rgba(0, 245, 160, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Mail color="var(--success)" size={20} />
            </div>
            <div>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Email Draft Queue</span>
              <h4 style={{ fontSize: '20px', margin: '2px 0 0 0' }}>{draftCount} Drafts Pending</h4>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Database size={14} />
              Connected Clusters
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div className="flex-between" style={{ fontSize: '13px' }}>
                <span>SQL Server (Users / Profiles)</span>
                <span style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--success)' }} />
                  Linked
                </span>
              </div>
              <div className="flex-between" style={{ fontSize: '13px' }}>
                <span>MongoDB (Medical / Actions)</span>
                <span style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--success)' }} />
                  Linked
                </span>
              </div>
              <div className="flex-between" style={{ fontSize: '13px' }}>
                <span>Redis (Cache Sessions)</span>
                <span style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--success)' }} />
                  Linked
                </span>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
