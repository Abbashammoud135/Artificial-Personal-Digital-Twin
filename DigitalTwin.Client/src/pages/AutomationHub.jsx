import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Mail, 
  Calendar, 
  Bell, 
  PenTool, 
  Award, 
  Inbox, 
  Send, 
  Plus, 
  Trash2, 
  FileEdit,
  Sparkles,
  Link,
  Loader
} from 'lucide-react';
import { api } from '../api';
import { showToast } from '../components/Toast';

export default function AutomationHub() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const initialTab = searchParams.get('tab') || 'emails';
  const [activeTab, setActiveTab] = useState(initialTab);

  // Sync state with URL search params
  useEffect(() => {
    setSearchParams({ tab: activeTab });
  }, [activeTab, setSearchParams]);

  // Google status
  const [googleConnected, setGoogleConnected] = useState(false);

  // Common loading indicators
  const [loading, setLoading] = useState(false);

  // ==========================================
  // EMAIL STATES
  // ==========================================
  const [emailTab, setEmailTab] = useState('inbox'); // inbox | compose | drafts | sent
  const [inboxEmails, setInboxEmails] = useState([]);
  const [inboxSummary, setInboxSummary] = useState('');
  
  // Compose form
  const [composeTo, setComposeTo] = useState('');
  const [composeTopic, setComposeTopic] = useState('');
  const [composeDetails, setComposeDetails] = useState('');
  const [composeStyle, setComposeStyle] = useState('');

  // Drafts & Edit Draft State
  const [drafts, setDrafts] = useState([]);
  const [editingDraft, setEditingDraft] = useState(null); // draft object when editing
  const [draftTo, setDraftTo] = useState('');
  const [draftSubject, setDraftSubject] = useState('');
  const [draftBody, setDraftBody] = useState('');

  // Sent emails
  const [sentEmails, setSentEmails] = useState([]);

  // ==========================================
  // CALENDAR STATES
  // ==========================================
  const [events, setEvents] = useState([]);
  const [showEventForm, setShowEventForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [eventTitle, setEventTitle] = useState('');
  const [eventStart, setEventStart] = useState('');
  const [eventEnd, setEventEnd] = useState('');
  const [eventDesc, setEventDesc] = useState('');

  // ==========================================
  // NOTIFICATIONS STATES
  // ==========================================
  const [alerts, setAlerts] = useState([]);
  const [newAlertMsg, setNewAlertMsg] = useState('');
  const [newAlertLevel, setNewAlertLevel] = useState('info');

  // ==========================================
  // STYLE PROFILE STATES
  // ==========================================
  const [styleTab, setStyleTab] = useState('manual'); // manual | generated
  const [styleProfiles, setStyleProfiles] = useState([]);
  const [manualStyle, setManualStyle] = useState({
    tone: 'neutral',
    signature: '',
    formatting: 'paragraphs',
    recurring_phrases: ''
  });
  const [styleGenerating, setStyleGenerating] = useState(false);

  // ==========================================
  // RECOMMENDATION STATES
  // ==========================================
  const [recommendations, setRecommendations] = useState([]);

  // Check google status
  const checkGoogle = async () => {
    try {
      const res = await api.action.google.status();
      setGoogleConnected(res.connected);
    } catch (e) {
      console.warn('Could not read google status', e);
    }
  };

  useEffect(() => {
    checkGoogle();
  }, []);

  // Fetch functions based on active tab
  useEffect(() => {
    if (activeTab === 'emails') {
      if (emailTab === 'inbox' && googleConnected) fetchInbox();
      else if (emailTab === 'drafts') fetchDrafts();
      else if (emailTab === 'sent') fetchSentLogs();
      fetchStyleProfiles(); // load profiles list for select input
    } else if (activeTab === 'calendar') {
      if (googleConnected) fetchEvents();
    } else if (activeTab === 'notifications') {
      fetchNotifications();
    } else if (activeTab === 'styles') {
      fetchStyleProfiles();
      fetchManualStyle();
    } else if (activeTab === 'recommendations') {
      fetchRecommendations();
    }
  }, [activeTab, emailTab, googleConnected]);

  // ==========================================
  // EMAIL ACTIONS
  // ==========================================
  const fetchInbox = async () => {
    setLoading(true);
    try {
      const res = await api.action.emails.inbox();
      setInboxEmails(res.emails || []);
      setInboxSummary(res.summary || null);
    } catch (err) {
      showToast('Could not fetch email inbox', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchDrafts = async () => {
    setLoading(true);
    try {
      const res = await api.action.emails.drafts();
      setDrafts(res.drafts || []);
    } catch (err) {
      showToast('Could not fetch drafts', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchSentLogs = async () => {
    setLoading(true);
    try {
      const res = await api.action.emails.sent();
      setSentEmails(res.sent_emails || []);
    } catch (err) {
      showToast('Could not load sent email history', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDraft = async (e) => {
    e.preventDefault();
    if (!composeTo || !composeTopic || !composeDetails) {
      showToast('Please fill in all draft properties', 'warning');
      return;
    }

    setLoading(true);
    try {
      await api.action.emails.draft(composeTo, composeTopic, composeDetails, composeStyle || undefined);
      showToast('AI draft generated and stored in MongoDB collection', 'success');
      setComposeTo('');
      setComposeTopic('');
      setComposeDetails('');
      setEmailTab('drafts');
    } catch (err) {
      showToast(err.message || 'Draft generation failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleEditDraftSelect = (draft) => {
    setEditingDraft(draft);
    setDraftTo(draft.to || '');
    setDraftSubject(draft.subject || '');
    setDraftBody(draft.body || '');
  };

  const handleUpdateDraft = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const draftId = editingDraft.draft_id || editingDraft._id || editingDraft.id;
      await api.action.emails.updateDraft(draftId, draftTo, draftSubject, draftBody);
      showToast('Draft updated successfully', 'success');
      setEditingDraft(null);
      fetchDrafts();
    } catch (err) {
      showToast('Failed to update draft', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDraft = async (draftId) => {
    if (!confirm('Are you sure you want to delete this draft?')) return;
    setLoading(true);
    try {
      await api.action.emails.deleteDraft(draftId);
      showToast('Draft deleted', 'success');
      fetchDrafts();
    } catch (err) {
      showToast('Failed to delete draft', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSendDraft = async (draft, enhance = false) => {
    setLoading(true);
    const draftId = draft.draft_id || draft._id || draft.id;
    try {
      if (enhance) {
        await api.action.emails.sendEnhanced(draft.to, draft.subject, draft.body, undefined, composeStyle || undefined);
        showToast('Draft enhanced & dispatched via Gmail API!', 'success');
      } else {
        await api.action.emails.send(draft.to, draft.subject, draft.body);
        showToast('Draft dispatched via Gmail API!', 'success');
      }
      // Delete draft after sending successfully
      await api.action.emails.deleteDraft(draftId);
      setEmailTab('sent');
    } catch (err) {
      showToast(err.message || 'Failed to dispatch email', 'error');
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // CALENDAR ACTIONS
  // ==========================================
  const fetchEvents = async () => {
    setLoading(true);
    try {
      // Load next 30 days
      const start = new Date().toISOString();
      const end = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();
      const res = await api.action.calendar.events(start, end);
      setEvents(res.events || []);
    } catch (err) {
      showToast('Could not load calendar events', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveEvent = async (e) => {
    e.preventDefault();
    if (!eventTitle || !eventStart || !eventEnd) {
      showToast('Title, start, and end times are required', 'warning');
      return;
    }

    setLoading(true);
    try {
      if (editingEvent) {
        const eventId = editingEvent._id || editingEvent.id;
        await api.action.calendar.updateEvent(eventId, {
          title: eventTitle,
          start: new Date(eventStart).toISOString(),
          end: new Date(eventEnd).toISOString(),
          description: eventDesc
        });
        showToast('Event updated in Google Calendar', 'success');
      } else {
        await api.action.calendar.createEvent(
          eventTitle,
          new Date(eventStart).toISOString(),
          new Date(eventEnd).toISOString(),
          eventDesc
        );
        showToast('Event scheduled in Google Calendar', 'success');
      }

      // Reset form
      setShowEventForm(false);
      setEditingEvent(null);
      setEventTitle('');
      setEventStart('');
      setEventEnd('');
      setEventDesc('');
      fetchEvents();
    } catch (err) {
      showToast(err.message || 'Failed to write calendar event', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleEditEventSelect = (evt) => {
    setEditingEvent(evt);
    setEventTitle(evt.title || evt.summary || '');
    
    // Map ISO to datetime-local inputs
    const mapISOToInput = (isoStr) => {
      if (!isoStr) return '';
      const date = new Date(isoStr);
      const tzOffset = date.getTimezoneOffset() * 60000;
      return new Date(date.getTime() - tzOffset).toISOString().slice(0, 16);
    };

    setEventStart(mapISOToInput(evt.start?.dateTime || evt.start));
    setEventEnd(mapISOToInput(evt.end?.dateTime || evt.end));
    setEventDesc(evt.description || '');
    setShowEventForm(true);
  };

  const handleDeleteEvent = async (eventId) => {
    if (!confirm('Permanently cancel this event?')) return;
    setLoading(true);
    try {
      await api.action.calendar.deleteEvent(eventId);
      showToast('Event cancelled successfully', 'success');
      fetchEvents();
    } catch (err) {
      showToast('Failed to delete calendar event', 'error');
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // NOTIFICATION ACTIONS
  // ==========================================
  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await api.action.notifications.list();
      setAlerts(res.notifications || []);
    } catch (err) {
      showToast('Could not fetch notifications', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAlert = async (e) => {
    e.preventDefault();
    if (!newAlertMsg.trim()) return;
    setLoading(true);
    try {
      await api.action.notifications.create(newAlertMsg, newAlertLevel);
      showToast('Alert dispatched', 'success');
      setNewAlertMsg('');
      fetchNotifications();
    } catch (err) {
      showToast('Failed to dispatch alert', 'error');
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // STYLE PROFILE ACTIONS
  // ==========================================
  const fetchStyleProfiles = async () => {
    try {
      const res = await api.action.style.profiles();
      console.log('Fetched style profiles:', res.profiles || []);
      setStyleProfiles(res.profiles || []);
    } catch (e) {
      console.warn('Could not read style profiles', e);
    }
  };

  const fetchManualStyle = async () => {
    try {
      const res = await api.action.style.getManual();
      if (res) {
        setManualStyle({
          tone: res.tone || 'neutral',
          signature: res.signature || '',
          formatting: res.formatting || 'paragraphs',
          recurring_phrases: res.recurring_phrases?.join(', ') || ''
        });
      }
    } catch (e) {
      console.warn('Could not read manual style profile', e);
    }
  };

  const handleSaveManualStyle = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const phrasesArray = manualStyle.recurring_phrases
        .split(',')
        .map(s => s.trim())
        .filter(Boolean);

      await api.action.style.saveManual({
        ...manualStyle,
        recurring_phrases: phrasesArray
      });
      showToast('Manual style template saved', 'success');
    } catch (err) {
      showToast('Could not save style profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateStyles = async () => {
    setStyleGenerating(true);
    showToast('LLM learning writing patterns from sent history...', 'info');
    try {
      const res = await api.action.style.generate();
      showToast(res.message || 'Style generation completed!', 'success');
      setStyleTab('generated');
      fetchStyleProfiles();
    } catch (err) {
      showToast(err.message || 'Style analyzer failed', 'error');
    } finally {
      setStyleGenerating(false);
    }
  };

  const handleDeleteStyleProfile = async (name) => {
    if (!confirm(`Delete style profile "${name}"?`)) return;
    setLoading(true);
    try {
      await api.action.style.deleteProfile(name);
      showToast('Style profile removed', 'success');
      fetchStyleProfiles();
    } catch (err) {
      showToast('Failed to delete profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // RECOMMENDATIONS ACTIONS
  // ==========================================
  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const res = await api.action.recommendations();
      // console.log('Fetched proactive recommendations:', res || []);
      setRecommendations(res.recommendations || []);
    } catch (err) {
      showToast('Could not retrieve recommendations', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteRecommendationIntent = async (rec) => {
    setLoading(true);
    showToast('Executing proactive intent...', 'info');
    try {
      console.log('Recommendation intent to execute:', rec);
      const label = `action: ${rec.action_type} payload: ${ JSON.stringify(rec.payload)}`;
      console.log('Executing recommendation intent:', label);
      await api.action.execute(label);
      setRecommendations(prev => prev.filter(r => r.id !== rec.id ));      
      showToast('Proactive action executed successfully!', 'success');

      // fetchRecommendations();
    } catch (err) {
      showToast(err.message || 'Execution failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Render Google Integration offline shield
  const renderGoogleAuthGuard = (featureName) => {
    if (googleConnected) return null;
    return (
      <div className="glass-card" style={{ 
        padding: '36px', 
        textAlign: 'center', 
        background: 'rgba(255, 140, 0, 0.03)', 
        border: '1px solid rgba(255, 140, 0, 0.2)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '16px'
      }}>
        <div style={{
          width: '50px', height: '50px', borderRadius: '50%', background: 'rgba(255, 140, 0, 0.08)',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <Link size={24} color="var(--warning)" />
        </div>
        <h3 style={{ fontSize: '18px', margin: 0 }}>Google Integration Unlinked</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '14px', maxWidth: '480px', margin: 0 }}>
          The {featureName} requires Google API permissions to sync with your personal inbox and calendars.
        </p>
        <button 
          onClick={() => navigate('/settings')}
          className="btn btn-primary" 
          style={{ width: 'fit-content' }}
        >
          Manage Integrations
        </button>
      </div>
    );
  };

  return (
    <div style={{ animation: 'fadeIn 0.3s ease-out', flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
      
      {/* Top Banner Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <span style={{ textTransform: 'uppercase', fontSize: '11px', letterSpacing: '0.1em', color: 'var(--primary)' }}>
            Automations & Pipelines
          </span>
          <h2 style={{ fontSize: '32px', margin: '4px 0 0 0' }}>Automation Hub</h2>
        </div>
      </div>

      {/* Main Tabs */}
      <div className="tabs-list" style={{ marginBottom: '24px' }}>
        <button onClick={() => setActiveTab('emails')} className={`tab-trigger ${activeTab === 'emails' ? 'active' : ''}`}>
          <Mail size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} /> Emails
        </button>
        <button onClick={() => setActiveTab('calendar')} className={`tab-trigger ${activeTab === 'calendar' ? 'active' : ''}`}>
          <Calendar size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} /> Calendar
        </button>
        <button onClick={() => setActiveTab('notifications')} className={`tab-trigger ${activeTab === 'notifications' ? 'active' : ''}`}>
          <Bell size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} /> Alerts
        </button>
        <button onClick={() => setActiveTab('styles')} className={`tab-trigger ${activeTab === 'styles' ? 'active' : ''}`}>
          <PenTool size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} /> Writing Styles
        </button>
        <button onClick={() => setActiveTab('recommendations')} className={`tab-trigger ${activeTab === 'recommendations' ? 'active' : ''}`}>
          <Sparkles size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} /> Recommendations
        </button>
      </div>

      {/* TAB: EMAILS */}
      {activeTab === 'emails' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Email sub-tab buttons */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <button onClick={() => setEmailTab('inbox')} className={`btn ${emailTab === 'inbox' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '8px 16px', fontSize: '12px' }}>Inbox Summaries</button>
            <button onClick={() => setEmailTab('compose')} className={`btn ${emailTab === 'compose' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '8px 16px', fontSize: '12px' }}>AI Compose</button>
            <button onClick={() => setEmailTab('drafts')} className={`btn ${emailTab === 'drafts' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '8px 16px', fontSize: '12px' }}>Drafts Directory ({drafts.length})</button>
            <button onClick={() => setEmailTab('sent')} className={`btn ${emailTab === 'sent' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '8px 16px', fontSize: '12px' }}>Sent logs</button>
          </div>

          {/* Subview: Inbox */}
          {emailTab === 'inbox' && (
            <>
              {renderGoogleAuthGuard('Email Inbox reader')}
              {googleConnected && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  {inboxSummary && (
                    <div className="glass-card" style={{ background: 'rgba(0, 212, 255, 0.02)', borderLeft: '3px solid var(--primary)' }}>
                      <h4 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--primary)' }}>AI Inbox Summary Digest</h4>
                      <div style={{ fontSize: '13px', lineHeight: 1.5, color: 'var(--text-primary)' }}>
                        {inboxSummary && (
                          <>
                            <p>Total Emails: {inboxSummary.count}</p>

                            <ul>
                              {inboxSummary.summary.map((email, idx) => (
                                <li key={idx}>
                                  {email.subject}
                                </li>
                              ))}
                            </ul>
                          </>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="glass-card">
                    <h3 style={{ fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Inbox size={16} /> Received Emails
                    </h3>

                    {inboxEmails.length === 0 ? (
                      <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)', fontSize: '13px' }}>
                        No new emails found in your synchronized Inbox.
                      </div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {inboxEmails.map((email, idx) => (
                          <div key={idx} style={{ padding: '14px', border: '1px solid var(--border)', borderRadius: '8px', background: 'rgba(255,255,255,0.01)' }}>
                            <div className="flex-between" style={{ marginBottom: '6px' }}>
                              <span style={{ fontSize: '13px', fontWeight: 600 }}>From: {email.from || email.sender}</span>
                              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{email.date}</span>
                            </div>
                            <h4 style={{ fontSize: '13px', fontWeight: 500, margin: '2px 0 6px 0' }}>{email.subject}</h4>
                            <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                              {email.snippet || email.body}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}

          {/* Subview: Compose Form */}
          {emailTab === 'compose' && (
            <div className="glass-card" style={{ maxWidth: '640px', margin: '0 auto', width: '100%' }}>
              <h3 style={{ fontSize: '18px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={18} color="var(--primary)" /> Draft Personalized Email via LLM
              </h3>

              <form onSubmit={handleCreateDraft} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <label htmlFor="comp-to">Recipient Email</label>
                  <input id="comp-to" type="email" placeholder="doctor@clinical.org" value={composeTo} onChange={(e) => setComposeTo(e.target.value)} required />
                </div>
                <div>
                  <label htmlFor="comp-subject">Subject Topic</label>
                  <input id="comp-subject" type="text" placeholder="Inquiry about latest thyroid blood panels" value={composeTopic} onChange={(e) => setComposeTopic(e.target.value)} required />
                </div>
                <div>
                  <label htmlFor="comp-style">Writing Style profile</label>
                  <select id="comp-style" value={composeStyle} onChange={(e) => setComposeStyle(e.target.value)}>
                    <option value="">Default AI Style</option>
                    {styleProfiles.map((prof) => (
                      <option key={prof.style_name} value={prof.style_name}>{prof.style_name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="comp-details">Context Details & Message Bulletpoints</label>
                  <textarea id="comp-details" placeholder="Explain that I received the thyroid report yesterday. Ask if medication doses should decrease..." value={composeDetails} onChange={(e) => setComposeDetails(e.target.value)} style={{ minHeight: '120px' }} required />
                </div>
                <button type="submit" className="btn btn-primary">Generate AI Draft</button>
              </form>
            </div>
          )}

          {/* Subview: Drafts Directory */}
          {emailTab === 'drafts' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              
              {/* If editing, show form */}
              {editingDraft && (
                <div className="glass-card" style={{ border: '1px solid var(--primary)', background: 'rgba(0, 212, 255, 0.01)' }}>
                  <div className="flex-between" style={{ marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '16px' }}>Modify Saved Email Draft</h3>
                    <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '11px' }} onClick={() => setEditingDraft(null)}>Cancel</button>
                  </div>
                  <form onSubmit={handleUpdateDraft} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div>
                      <label>To</label>
                      <input type="text" value={draftTo} onChange={(e) => setDraftTo(e.target.value)} />
                    </div>
                    <div>
                      <label>Subject</label>
                      <input type="text" value={draftSubject} onChange={(e) => setDraftSubject(e.target.value)} />
                    </div>
                    <div>
                      <label>Email Body</label>
                      <textarea value={draftBody} onChange={(e) => setDraftBody(e.target.value)} style={{ minHeight: '150px' }} />
                    </div>
                    <button type="submit" className="btn btn-primary" style={{ width: 'fit-content' }}>Save Changes</button>
                  </form>
                </div>
              )}

              <div className="glass-card">
                <h3 style={{ fontSize: '16px', marginBottom: '16px' }}>Local Draft Queue</h3>
                {drafts.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)', fontSize: '13px' }}>
                    No drafts pending. Generate one in the AI Compose tab.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {drafts.map((d) => {
                      const dId = d.draft_id || d._id || d.id;
                      return (
                        <div key={dId} className="glass-card" style={{ padding: '16px', background: 'rgba(255,255,255,0.01)' }}>
                          <div className="flex-between" style={{ marginBottom: '10px' }}>
                            <div>
                              <span style={{ fontSize: '13px', fontWeight: 600 }}>To: {d.to}</span>
                              <h4 style={{ fontSize: '14px', margin: '2px 0 0 0' }}>Subject: {d.subject}</h4>
                            </div>
                            <div className="gap-12">
                              <button onClick={() => handleEditDraftSelect(d)} style={{ background: 'transparent', border: 'none', color: 'var(--primary)', cursor: 'pointer' }} title="Edit"><FileEdit size={16} /></button>
                              <button onClick={() => handleDeleteDraft(dId)} style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer' }} title="Delete"><Trash2 size={16} /></button>
                            </div>
                          </div>
                          
                          <p style={{ 
                            fontSize: '12px', 
                            color: 'var(--text-muted)', 
                            background: 'rgba(5, 13, 26, 0.4)', 
                            padding: '10px', 
                            borderRadius: '6px', 
                            border: '1px solid var(--border)',
                            whiteSpace: 'pre-wrap',
                            maxHeight: '120px',
                            overflowY: 'auto'
                          }}>
                            {d.body}
                          </p>

                          {googleConnected ? (
                            <div className="gap-12" style={{ marginTop: '12px', justifyContent: 'flex-end' }}>
                              <button onClick={() => handleSendDraft(d, false)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                                Send Directly
                              </button>
                              <button onClick={() => handleSendDraft(d, true)} className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                                Send Enhanced (LLM Style)
                              </button>
                            </div>
                          ) : (
                            <div style={{ fontSize: '11px', color: 'var(--warning)', marginTop: '8px', textAlign: 'right' }}>
                              Connect Google in Settings to send this draft.
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Subview: Sent logs */}
          {emailTab === 'sent' && (
            <div className="glass-card">
              <h3 style={{ fontSize: '16px', marginBottom: '16px' }}>Sent Communications Log</h3>
              {sentEmails.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)', fontSize: '13px' }}>
                  No recorded emails sent via the twin system yet.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {sentEmails.map((email, idx) => (
                    <div key={idx} style={{ padding: '14px', border: '1px solid var(--border)', borderRadius: '8px', background: 'rgba(255,255,255,0.01)' }}>
                      <div className="flex-between" style={{ marginBottom: '6px' }}>
                        <span style={{ fontSize: '13px', fontWeight: 600 }}>Sent To: {email.to}</span>
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{new Date(email.sent_at || email.date || Date.now()).toLocaleDateString()}</span>
                      </div>
                      <h4 style={{ fontSize: '13px', margin: '2px 0 6px 0' }}>{email.subject}</h4>
                      <p style={{ fontSize: '12px', color: 'var(--text-muted)', whiteSpace: 'pre-wrap', maxHeight: '100px', overflowY: 'auto' }}>
                        {email.body}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </div>
      )}

      {/* TAB: CALENDAR */}
      {activeTab === 'calendar' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {renderGoogleAuthGuard('Google Calendar planner')}

          {googleConnected && (
            <div className="grid-2-1">
              
              {/* Event Timeline */}
              <div className="glass-card">
                <div className="flex-between" style={{ marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Calendar size={18} /> Schedule Timeline (Next 30 Days)
                  </h3>
                  {!showEventForm && (
                    <button 
                      onClick={() => {
                        setEditingEvent(null);
                        setEventTitle('');
                        setEventStart('');
                        setEventEnd('');
                        setEventDesc('');
                        setShowEventForm(true);
                      }} 
                      className="btn btn-primary" 
                      style={{ padding: '6px 12px', fontSize: '12px' }}
                    >
                      <Plus size={14} /> Schedule Event
                    </button>
                  )}
                </div>

                {events.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)', fontSize: '13px' }}>
                    No events scheduled in this range.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {events.map((evt) => {
                      const eId = evt._id || evt.id;
                      return (
                        <div key={eId} style={{ padding: '14px', border: '1px solid var(--border)', borderRadius: '8px', background: 'rgba(255,255,255,0.01)' }}>
                          <div className="flex-between">
                            <div>
                              <h4 style={{ fontSize: '14px', fontWeight: 600 }}>{evt.title || evt.summary}</h4>
                              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                                {new Date(evt.start?.dateTime || evt.start).toLocaleString()} - {new Date(evt.end?.dateTime || evt.end).toLocaleString()}
                              </span>
                            </div>

                            <div className="gap-12">
                              <button onClick={() => handleEditEventSelect(evt)} style={{ background: 'transparent', border: 'none', color: 'var(--primary)', cursor: 'pointer' }}><FileEdit size={15} /></button>
                              <button onClick={() => handleDeleteEvent(eId)} style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}><Trash2 size={15} /></button>
                            </div>
                          </div>
                          {evt.description && (
                            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px', marginBottom: 0 }}>
                              {evt.description}
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Event Editor Form */}
              <div>
                {showEventForm && (
                  <div className="glass-card" style={{ border: '1px solid var(--primary)', animation: 'fadeIn 0.2s ease-out' }}>
                    <div className="flex-between" style={{ marginBottom: '16px' }}>
                      <h3 style={{ fontSize: '16px' }}>{editingEvent ? 'Reschedule Event' : 'Schedule Event'}</h3>
                      <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '11px' }} onClick={() => setShowEventForm(false)}>Cancel</button>
                    </div>

                    <form onSubmit={handleSaveEvent} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                      <div>
                        <label>Title</label>
                        <input type="text" placeholder="Dentist appointment" value={eventTitle} onChange={(e) => setEventTitle(e.target.value)} required />
                      </div>
                      <div>
                        <label>Start DateTime</label>
                        <input type="datetime-local" value={eventStart} onChange={(e) => setEventStart(e.target.value)} required />
                      </div>
                      <div>
                        <label>End DateTime</label>
                        <input type="datetime-local" value={eventEnd} onChange={(e) => setEventEnd(e.target.value)} required />
                      </div>
                      <div>
                        <label>Description (Optional)</label>
                        <textarea placeholder="Root canal follow up" value={eventDesc} onChange={(e) => setEventDesc(e.target.value)} style={{ minHeight: '80px' }} />
                      </div>
                      <button type="submit" className="btn btn-primary">{editingEvent ? 'Update' : 'Schedule'}</button>
                    </form>
                  </div>
                )}
              </div>

            </div>
          )}
        </div>
      )}

      {/* TAB: NOTIFICATIONS */}
      {activeTab === 'notifications' && (
        <div className="grid-2-1">
          {/* Notifications List */}
          <div className="glass-card">
            <h3 style={{ fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Bell size={18} /> Active System Notifications & Reminders
            </h3>

            {alerts.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)', fontSize: '13px' }}>
                No active system alerts.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {alerts.map((a) => {
                  let lBadge = 'badge-info';
                  if (a.level === 'critical') lBadge = 'badge-danger';
                  else if (a.level === 'warning') lBadge = 'badge-warning';

                  return (
                    <div key={a._id || a.id} style={{ padding: '14px', border: '1px solid var(--border)', borderRadius: '8px', background: 'rgba(255,255,255,0.01)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <p style={{ fontSize: '13px', color: 'var(--text-primary)', margin: 0 }}>{a.message}</p>
                        <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                          {a.created_at ? new Date(a.created_at).toLocaleString() : 'System alert'}
                        </span>
                      </div>
                      <span className={`badge ${lBadge}`}>{a.level}</span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Trigger Alert Form */}
          <div className="glass-card">
            <h3 style={{ fontSize: '16px', marginBottom: '16px' }}>Dispatch Custom Reminder</h3>
            <form onSubmit={handleCreateAlert} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label>Message Content</label>
                <textarea placeholder="e.g. Remember to take Vitamin D after lunch..." value={newAlertMsg} onChange={(e) => setNewAlertMsg(e.target.value)} required />
              </div>
              <div>
                <label>Threat Level</label>
                <select value={newAlertLevel} onChange={(e) => setNewAlertLevel(e.target.value)}>
                  <option value="info">Info (Blue)</option>
                  <option value="warning">Warning (Orange)</option>
                  <option value="critical">Critical (Red)</option>
                </select>
              </div>
              <button type="submit" className="btn btn-primary">Dispatch Alert</button>
            </form>
          </div>
        </div>
      )}

      {/* TAB: WRITING STYLES */}
      {activeTab === 'styles' && (
        <div className="grid-2-1">
          
          {/* Style list & generator */}
          <div className="glass-card">
            <div className="flex-between" style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <PenTool size={18} /> LLM Writing Style Profiles
              </h3>
              
              <button 
                onClick={handleGenerateStyles} 
                disabled={styleGenerating} 
                className="btn btn-primary"
                style={{ padding: '6px 12px', fontSize: '12px' }}
              >
                {styleGenerating ? (
                  <>
                    <Loader size={12} className="spinning" /> Analyzing...
                  </>
                ) : 'Auto-Learn from Sent'}
              </button>
            </div>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
              <button onClick={() => setStyleTab('manual')} className={`btn ${styleTab === 'manual' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '6px 12px', fontSize: '11px' }}>Manual Rules</button>
              <button onClick={() => setStyleTab('generated')} className={`btn ${styleTab === 'generated' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '6px 12px', fontSize: '11px' }}>Learned Profiles ({styleProfiles.length})</button>
            </div>

            {styleTab === 'manual' && (
              <form onSubmit={handleSaveManualStyle} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div>
                  <label>Tone</label>
                  <input type="text" placeholder="e.g. professional, formal, concise" value={manualStyle.tone} onChange={(e) => setManualStyle({ ...manualStyle, tone: e.target.value })} required />
                </div>
                <div>
                  <label>Signature Text</label>
                  <input type="text" placeholder="Best regards, John" value={manualStyle.signature} onChange={(e) => setManualStyle({ ...manualStyle, signature: e.target.value })} />
                </div>
                <div>
                  <label>Formatting Preferences</label>
                  <input type="text" placeholder="e.g. short paragraphs, bulletpoints" value={manualStyle.formatting} onChange={(e) => setManualStyle({ ...manualStyle, formatting: e.target.value })} />
                </div>
                <div>
                  <label>Recurring phrases (Comma Separated)</label>
                  <input type="text" placeholder="As per our discussions, Please find attached" value={manualStyle.recurring_phrases} onChange={(e) => setManualStyle({ ...manualStyle, recurring_phrases: e.target.value })} />
                </div>
                <button type="submit" className="btn btn-primary" style={{ width: 'fit-content' }}>Save Manual Template</button>
              </form>
            )}

            {styleTab === 'generated' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {styleProfiles.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)', fontSize: '13px' }}>
                    No AI-generated profiles exist. Click 'Auto-Learn' to build models from sent communications.
                  </div>
                ) : (
                  styleProfiles.map((p, idx) => (
                    <div key={idx} className="glass-card" style={{ padding: '16px', background: 'rgba(255,255,255,0.01)' }}>
                      <div className="flex-between" style={{ marginBottom: '8px' }}>
                        <h4 style={{ fontSize: '14px', color: 'var(--primary)' }}>{p.style_name || 'AI Style Profile'}</h4>
                        <button 
                          onClick={() => handleDeleteStyleProfile(p.style_name)} 
                          style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                      
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', fontSize: '11px', marginBottom: '8px' }}>
                        <span className="badge badge-info">Tone: {p.tone}</span>
                        <span className="badge badge-info">Format: {p.formatting}</span>
                      </div>

                      {p.signature && (
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                          <strong>Signature:</strong> "{p.signature}"
                        </div>
                      )}

                      {p.recurring_phrases && p.recurring_phrases.length > 0 && (
                        <div style={{ marginTop: '8px' }}>
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Recurring expressions:</span>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                            {p.recurring_phrases.map((phrase, pi) => (
                              <span key={pi} style={{ fontSize: '10px', background: 'rgba(255,255,255,0.04)', padding: '2px 6px', borderRadius: '4px' }}>
                                {phrase}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB: RECOMMENDATIONS */}
      {activeTab === 'recommendations' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: '16px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Award size={18} color="var(--primary)" /> Proactive Twin Recommendations
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '20px' }}>
              Proactively evaluated by checking biological trends against schedule. Click "Execute" to let the agent perform tasks.
            </p>

            {recommendations.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)', fontSize: '13px' }}>
                All systems optimal. No recommendation templates flagged.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {recommendations.map((rec) => (
                  <div key={rec.id || rec._id} className="glass-card" style={{ padding: '18px', borderLeft: '3px solid var(--secondary)', background: 'rgba(123, 97, 255, 0.01)' }}>
                    <div className="flex-between" style={{ marginBottom: '8px' }}>
                      <h4 style={{ fontSize: '15px' }}>{rec.title}</h4>
                      <span className="badge badge-info">{rec.action_type || 'system_action'}</span>
                    </div>

                    <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '14px' }}>
                      <strong>Reasoning:</strong> {rec.reason}
                    </p>

                    {rec.payload && (
                      <div style={{
                        background: 'rgba(5, 13, 26, 0.4)',
                        padding: '10px',
                        border: '1px solid var(--border)',
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontFamily: 'var(--mono)',
                        overflowX: 'auto',
                        marginBottom: '14px'
                      }}>
                        <pre style={{ margin: 0 }}>{JSON.stringify(rec.payload, null, 2)}</pre>
                      </div>
                    )}

                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <button 
                        onClick={() => handleExecuteRecommendationIntent(rec)} 
                        className="btn btn-primary"
                        style={{ padding: '6px 14px', fontSize: '12px', display: 'flex', gap: '6px' }}
                      >
                        <Sparkles size={12} /> Execute Recommendation
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
        <style>
            {`
              #comp-style {
                background-color: #111827;
                color: #ffffff;
                border: 1px solid #374151;
              }

              #comp-style option {
                background-color: #111827;
                color: #ffffff;
              }

              #comp-style option:checked {
                background-color: #2563eb;
                color: white;
              }
            `}
          </style>
    </div>
  );
}
