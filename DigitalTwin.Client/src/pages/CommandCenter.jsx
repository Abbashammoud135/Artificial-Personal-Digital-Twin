import { useState, useEffect, useRef } from 'react';
import { Terminal, Send, History, Calendar, Mail, Bell, Sparkles, AlertCircle } from 'lucide-react';
import { api } from '../api';
import AIPulse from '../components/AIPulse';
import { showToast } from '../components/Toast';

export default function CommandCenter() {
  const [query, setQuery] = useState('');
  const [isActive, setIsActive] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [latestResult, setLatestResult] = useState(null);
  const [history, setHistory] = useState([]);
  const textareaRef = useRef(null);

  useEffect(() => {
    // Load history from localStorage
    const saved = localStorage.getItem('dt_command_history');
    if (saved) {
      setHistory(JSON.parse(saved));
    }
  }, []);

  const saveHistory = (newEntry) => {
    const updated = [newEntry, ...history].slice(0, 10);
    setHistory(updated);
    localStorage.setItem('dt_command_history', JSON.stringify(updated));
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('dt_command_history');
    showToast('Command history cleared', 'success');
  };

  const handleExecute = async (commandString) => {
    if (!commandString.trim()) return;

    setIsThinking(true);
    setLatestResult(null);

    try {
      const res = await api.action.execute(commandString);
      const entry = {
        query: commandString,
        timestamp: new Date().toISOString(),
        result: res
      };
      console.log('Command execution result:',entry);
      setLatestResult(res);
      saveHistory(entry);
      showToast('Command executed', 'success');
    } catch (err) {
      showToast(err.message || 'Execution error', 'error');
    } finally {
      setIsThinking(false);
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    handleExecute(query);
    setQuery('');
  };

  const handleQuickAction = (actionText) => {
    setQuery(actionText);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const getIntentIcon = (type) => {
    switch (type) {
      case 'create_calendar_event':
      case 'calendar': 
      case 'create_event':
        return <Calendar size={18} color="var(--primary)" />;
      case 'draft_email':
      case 'email':
      case 'send_email':
        return <Mail size={18} color="var(--success)" />;
      case 'create_notification':
      case 'notification':
        return <Bell size={18} color="var(--warning)" />;
      default:
        return <Sparkles size={18} color="var(--secondary)" />;
    }
  };

  const getIntentBadge = (type) => {
    switch (type) {
      case 'create_calendar_event':
      case 'create_event':
        return '📅 Calendar Event';
      case 'draft_email':
        return '📧 Email Draft';
      case 'send_email':
        return '📧 Email Sent';
      case 'create_notification':
        return '🔔 Notification';
      default:
        return '🧠 AI Action';
    }
  };

  const chips = [
    'List my inbox',
    'What are my events today?',
    'Draft email to my doctor',
    'Reschedule the shopping to tomorrow at 2 PM',
    'Get proactive recommendations'
  ];

  return (
    <div style={{ animation: 'fadeIn 0.3s ease-out', flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
      
      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <span style={{ textTransform: 'uppercase', fontSize: '11px', letterSpacing: '0.1em', color: 'var(--primary)' }}>
          Co-processing Unit
        </span>
        <h2 style={{ fontSize: '32px', margin: '4px 0 0 0' }}>AI Command Center</h2>
      </div>

      {/* Main NL prompt wrapper */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '40px 0 20px 0' }}>
        <form onSubmit={onSubmit} style={{ width: '100%', maxWidth: '720px' }}>
          
          <AIPulse isActive={isActive || query.length > 0} isThinking={isThinking}>
            <div style={{
              background: 'rgba(3, 8, 17, 0.9)',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              padding: '6px 12px',
              border: '1px solid var(--border)'
            }}>
              <textarea
                ref={textareaRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => setIsActive(true)}
                onBlur={() => setIsActive(false)}
                placeholder="Tell your twin what to do... e.g. 'Schedule gym tomorrow 7am' or 'Draft email to Dr. Smith about my results'"
                style={{
                  flexGrow: 1,
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  boxShadow: 'none',
                  resize: 'none',
                  padding: '12px 8px',
                  height: '60px',
                  fontSize: '15px'
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    onSubmit(e);
                  }
                }}
              />
              <button
                type="submit"
                disabled={isThinking || !query.trim()}
                className="btn btn-primary"
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  minWidth: '45px',
                  height: '45px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: 'none'
                }}
              >
                <Send size={16} />
              </button>
            </div>
          </AIPulse>
        </form>

        {/* Quick action chips */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
          justifyContent: 'center',
          maxWidth: '720px',
          marginTop: '16px'
        }}>
          {chips.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleQuickAction(chip)}
              style={{
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border)',
                borderRadius: '20px',
                padding: '6px 14px',
                fontSize: '12px',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.target.style.color = 'var(--primary)';
                e.target.style.borderColor = 'rgba(0, 212, 255, 0.3)';
                e.target.style.background = 'rgba(0, 212, 255, 0.04)';
              }}
              onMouseLeave={(e) => {
                e.target.style.color = 'var(--text-muted)';
                e.target.style.borderColor = 'var(--border)';
                e.target.style.background = 'rgba(255,255,255,0.02)';
              }}
            >
              {chip}
            </button>
          ))}
        </div>
      </div>

      {/* Latest Execution output card */}
      {latestResult && (
        <div style={{ width: '100%', maxWidth: '720px', margin: '20px auto 40px auto', animation: 'fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)' }}>
          <div className="glass-card" style={{ borderLeft: '3px solid var(--primary)' }}>
            <div className="flex-between" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '12px', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {getIntentIcon(latestResult.intent?.type)}
                <h4 style={{ fontSize: '15px' }}>Action Response</h4>
              </div>
              <span className="badge badge-info">
                {getIntentBadge(latestResult.intent?.type)}
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {latestResult.intent && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', background: 'rgba(255,255,255,0.01)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Parsed Intent Details</span>
                  <pre style={{ margin: 0, fontFamily: 'var(--mono)', fontSize: '12px', overflowX: 'auto' }}>
                    {JSON.stringify(latestResult.intent, null, 2)}
                  </pre>
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', padding: '0 4px' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Execution Payload Result</span>
                <pre style={{ 
                  margin: 0, 
                  fontFamily: 'var(--mono)', 
                  fontSize: '12px', 
                  whiteSpace: 'pre-wrap',
                  maxHeight: '300px',
                  overflowY: 'auto',
                  background: 'rgba(3,8,17,0.3)',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid var(--border)'
                }}>
                  {JSON.stringify(latestResult.result || latestResult, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* History log drawer */}
      <div className="glass-card" style={{ marginTop: 'auto', padding: '20px' }}>
        <div className="flex-between" style={{ marginBottom: '16px' }}>
          <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <History size={16} color="var(--text-muted)" />
            Command History Log
          </h3>
          {history.length > 0 && (
            <button 
              onClick={clearHistory}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--danger)',
                fontSize: '12px',
                cursor: 'pointer',
                fontWeight: 500
              }}
            >
              Clear Log
            </button>
          )}
        </div>

        {history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)', fontSize: '13px' }}>
            Your command history is stored locally in this terminal. No queries executed yet.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '300px', overflowY: 'auto' }}>
            {history.map((h, idx) => (
              <div 
                key={idx} 
                onClick={() => {
                  setLatestResult(h.result);
                  showToast('Loaded query results', 'info');
                }}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: 'rgba(255,255,255,0.01)',
                  border: '1px solid var(--border)',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'background 0.2s',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.01)'}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', overflow: 'hidden' }}>
                  <Terminal size={14} color="var(--primary)" />
                  <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    "{h.query}"
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>
                  <span className="badge badge-info" style={{ fontSize: '10px' }}>
                    {h.result?.intent?.type || 'query'}
                  </span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
