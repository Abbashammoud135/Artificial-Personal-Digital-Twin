import { useState, useEffect } from 'react';
import { 
  HeartPulse, 
  Upload, 
  FileText, 
  Send, 
  TrendingUp, 
  Clipboard, 
  Activity, 
  User, 
  FileCheck,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { api } from '../api';
import TrendChart from '../components/TrendChart';
import { showToast } from '../components/Toast';

export default function HealthIntelligence() {
  const [activeTab, setActiveTab] = useState('diagnostics'); // diagnostics | chat | trends | profile
  
  // Dashboard summary stats
  const [stats, setStats] = useState({ anomaly_count: 0, analyzed_reports: 0, total_reports: 0 });

  // Upload/Analyze States
  const [uploadNote, setUploadNote] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisStatus, setAnalysisStatus] = useState(''); // 'extracting' | 'analyzing' | 'done' | ''
  const [latestAnalysis, setLatestAnalysis] = useState(null);

  // Chat States
  const [chatQuestion, setChatQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'agent', text: 'Hello! I am your AI Health Agent. Ask me anything about your uploaded medical records or profile.' }
  ]);
  const [chatLoading, setChatLoading] = useState(false);

  // Trends States
  const [trends, setTrends] = useState({});

  // Reports Directory States
  const [reports, setReports] = useState([]);
  const [expandedReportId, setExpandedReportId] = useState(null);
  const [userFullName, setUserFullName] = useState('');

  // Health Profile Form States
  const [profile, setProfile] = useState({
  height: "",
  weight: "",
  sleep_hours: "",
  gender: "other",
  blood_type: "O+",
  chronic_conditions: "",
  lifestyle: "",
  stress_level: 5,
  birthdate: ""
});
  const [profileSaving, setProfileSaving] = useState(false);

  // Calculate BMI
  const calculateBMI = () => {
    if (!profile.height || !profile.weight) return 0;
    const heightInMeters = profile.height / 100;
    return (profile.weight / (heightInMeters * heightInMeters)).toFixed(1);
  };

  const loadHealthData = async () => {
    try {
      const statsRes = await api.healthDocs.dashboard();
      setStats(statsRes);
    } catch (e) {
      console.warn('Dashboard stats load error', e);
    }

    try {
      const reportsRes = await api.healthDocs.reports();
      setReports(reportsRes || []);
    } catch (e) {
      console.warn('Reports load error', e);
    }

    try {
      const trendsRes = await api.healthDocs.trends();
      console.log('Loaded trends data:', trendsRes);
      setTrends(trendsRes.trends || {});
    } catch (e) {
      console.warn('Trends load error', e);
    }

    try {
      const profileRes = await api.healthProfile.get();
      console.log('Loaded health profile:', profileRes);
      if (profileRes) {
        setProfile({
          birthdate: profileRes.birthdate ? profileRes.birthdate.split('T')[0] : '',
          gender: profileRes.gender || 'other',
          height: profileRes.height || 170,
          weight: profileRes.weight || 70,
          blood_type: profileRes.blood_type || 'O+',
          chronic_conditions: profileRes.chronic_conditions || '',
          lifestyle: profileRes.lifestyle || '',
          stress_level: profileRes.stress_level || 5,
          sleep_hours: profileRes.sleep_hours || 7
        });
      }
    } catch (e) {
      console.warn('Profile load error', e);
    }
    try {
      const fullName = localStorage.getItem("userFullName");
      console.log('Loaded user full name from localStorage:', fullName);
      setUserFullName(fullName);
    } catch (e) {
      console.warn('Failed to load user full name:', e);
      setUserFullName('');
    }
  };

  useEffect(() => {
    loadHealthData();
  }, []);

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile && !uploadNote.trim()) {
      showToast('Please attach a PDF report or type a health note', 'warning');
      return;
    }

    setAnalysisStatus('extracting');
    try {
      // 1. Upload the doc
      showToast('Uploading medical data...', 'info');
      // await api.healthDocs.upload(selectedFile, uploadNote);

      // 2. Run analysis
      setAnalysisStatus('analyzing');
      const analysisRes = await api.healthDocs.analyze(selectedFile, uploadNote);
      setLatestAnalysis(analysisRes);
      setAnalysisStatus('done');
      showToast('Analysis completed successfully!', 'success');
      
      // Clear input and reload directory
      setUploadNote('');
      setSelectedFile(null);
      const fileInput = document.getElementById('medical-file-input');
      if (fileInput) fileInput.value = '';
      
      loadHealthData();
    } catch (err) {
      showToast(err.message || 'Analysis failed', 'error');
      setAnalysisStatus('');
    }
  };

  const handleChatSend = async (e) => {
    e.preventDefault();
    if (!chatQuestion.trim()) return;

    const userMessage = chatQuestion;
    setChatHistory(prev => [...prev, { role: 'user', text: userMessage }]);
    setChatQuestion('');
    setChatLoading(true);

    try {
      const res = await api.healthDocs.ask(userMessage);
      setChatHistory(prev => [...prev, { role: 'agent', text: res.answer || res.response || res }]);
    } catch (err) {
      showToast(err.message || 'Could not fetch answer', 'error');
      setChatHistory(prev => [...prev, { role: 'agent', text: 'Error: Could not retrieve response from health agent.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleProfileSave = async (e) => {
    e.preventDefault();
    setProfileSaving(true);

    const formattedProfile = {
  ...profile,
  height: Number(profile.height) || 0,
  weight: Number(profile.weight) || 0,
  sleep_hours: Number(profile.sleep_hours) || 0,
  stress_level: Number(profile.stress_level) || 0,
  chronic_conditions: profile.chronic_conditions
};

console.log('Saving profile with data:', formattedProfile);

    try {
      // Check if we need to call PUT or POST. PUT is standard update.
      await api.healthProfile.update(formattedProfile);
      showToast('Health profile updated', 'success');
      loadHealthData();
    } catch (err) {
      // Fallback: try create if update fails
      try {
        await api.healthProfile.create(formattedProfile);
        showToast('Health profile initialized', 'success');
        loadHealthData();
      } catch (e2) {
        showToast(err.message || 'Failed to save health profile', 'error');
      }
    } finally {
      setProfileSaving(false);
    }
  };
const getReportName = (fileUrl) => {
  const match = fileUrl?.match(/_([^\\]+)\.pdf$/i);
  return match ? match[1] : "Doctor Note";
};
  // Helper for Circular progress SVG Dials
  const renderRiskDial = (label, scoreString, accentColor) => {
    // Risks are often strings "low", "medium", "high" or floats. If string, map to numerical values for display
    let val = 0.2;
    if (typeof scoreString === 'string') {
      const lower = scoreString.toLowerCase();
      if (lower.includes('high') || lower.includes('severe')) val = 0.95;
      else if (lower.includes('mod') || lower.includes('med')) val = 0.6;
      else if (lower.includes('low') || lower.includes('mild')) val = 0.3;
    } else if (typeof scoreString === 'number') {
      val = scoreString;
    }

    const radius = 30;
    const strokeWidth = 5;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (val * circumference);

    return (
      <div className="risk-dial-container" style={{ gap: '8px' }}>
        <div className="risk-dial">
          <svg style={{ transform: 'rotate(-90deg)', width: '80px', height: '80px' }}>
            <circle
              cx="40"
              cy="40"
              r={radius}
              stroke="rgba(255,255,255,0.03)"
              strokeWidth={strokeWidth}
              fill="transparent"
            />
            <circle
              cx="40"
              cy="40"
              r={radius}
              stroke={accentColor}
              strokeWidth={strokeWidth}
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 0.8s ease' }}
            />
          </svg>
          <div className="risk-dial-label" style={{ color: accentColor }}>
            {scoreString ? scoreString.toUpperCase().slice(0, 4) : 'N/A'}
          </div>
        </div>
        <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)' }}>{label}</span>
      </div>
    );
  };

  return (
    <div style={{ animation: 'fadeIn 0.3s ease-out', flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
      
      {/* Top Banner Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <span style={{ textTransform: 'uppercase', fontSize: '11px', letterSpacing: '0.1em', color: 'var(--primary)' }}>
            Biometrics & Diagnostics
          </span>
          <h2 style={{ fontSize: '32px', margin: '4px 0 0 0' }}>Health Intelligence</h2>
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="tabs-list" style={{ marginBottom: '24px' }}>
        <button 
          onClick={() => setActiveTab('diagnostics')} 
          className={`tab-trigger ${activeTab === 'diagnostics' ? 'active' : ''}`}
        >
          <Activity size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
          Diagnostics & Upload
        </button>
        <button 
          onClick={() => setActiveTab('chat')} 
          className={`tab-trigger ${activeTab === 'chat' ? 'active' : ''}`}
        >
          <HeartPulse size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
          Health Agent Chat
        </button>
        <button 
          onClick={() => setActiveTab('trends')} 
          className={`tab-trigger ${activeTab === 'trends' ? 'active' : ''}`}
        >
          <TrendingUp size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
          Lab Trends
        </button>
        <button 
          onClick={() => setActiveTab('profile')} 
          className={`tab-trigger ${activeTab === 'profile' ? 'active' : ''}`}
        >
          <User size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
          Health Profile
        </button>
      </div>

      {/* Tab: Diagnostics & Upload */}
      {activeTab === 'diagnostics' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <div className="grid-2">
            
            {/* Upload form */}
            <div className="glass-card">
              <h3 style={{ fontSize: '18px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Upload size={18} color="var(--primary)" />
                Upload Laboratory Records
              </h3>
              
              <form onSubmit={handleUploadSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{
                  border: '1px dashed var(--border)',
                  borderRadius: '10px',
                  padding: '24px',
                  textAlign: 'center',
                  background: 'rgba(255,255,255,0.01)',
                  cursor: 'pointer',
                  position: 'relative'
                }}
                onDragOver={(e) => e.preventDefault()}
                onClick={() => document.getElementById('medical-file-input').click()}
                >
                  <input
                    id="medical-file-input"
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setSelectedFile(e.target.files[0])}
                    style={{ display: 'none' }}
                  />
                  <FileText size={36} color={selectedFile ? 'var(--primary)' : 'var(--text-muted)'} style={{ marginBottom: '8px' }} />
                  {selectedFile ? (
                    <div>
                      <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>{selectedFile.name}</span>
                      <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Click to replace PDF</p>
                    </div>
                  ) : (
                    <div>
                      <span style={{ fontSize: '14px', fontWeight: 600 }}>Select PDF Medical Document</span>
                      <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Drag and drop or browse files</p>
                    </div>
                  )}
                </div>

                <div>
                  <label htmlFor="upload-note">Or paste clinical summary details / symptoms</label>
                  <textarea
                    id="upload-note"
                    value={uploadNote}
                    onChange={(e) => setUploadNote(e.target.value)}
                    placeholder="e.g. Patient complains of fatigue. Iron levels low..."
                    style={{ minHeight: '100px' }}
                  />
                </div>

                <button 
                  type="submit" 
                  className="btn btn-primary" 
                  disabled={!!analysisStatus && analysisStatus !== 'done'}
                >
                  {analysisStatus === 'extracting' ? 'Extracting Data...' :
                   analysisStatus === 'analyzing' ? 'Analyzing via RAG Agent...' :
                   'Upload & Run Diagnostics'}
                </button>
              </form>
            </div>

            {/* Analysis Progress / Latest Results */}
            <div className="glass-card">
              <h3 style={{ fontSize: '18px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity size={18} color="var(--secondary)" />
                Diagnostic Risk Matrix
              </h3>

              {analysisStatus === 'extracting' || analysisStatus === 'analyzing' ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '80%' }}>
                  <div className="ai-pulse-wrapper active thinking" style={{ width: '80px', height: '80px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Activity size={32} color="var(--primary)" />
                  </div>
                  <span style={{ marginTop: '16px', fontSize: '14px', fontWeight: 'bold' }}>
                    {analysisStatus === 'extracting' ? 'Extracting text layouts...' : 'LLM Medical evaluation running...'}
                  </span>
                </div>
              ) : latestAnalysis ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', height: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-around', background: 'rgba(255,255,255,0.01)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                    {renderRiskDial('Cardiovascular', latestAnalysis.analysis.analysis.cardiovascular_risk||'0', 'var(--primary)')}
                    {renderRiskDial('Metabolic', latestAnalysis.analysis.analysis.metabolic_risk||'0', 'var(--secondary)')}
                    {renderRiskDial('Anomaly Count',  String(latestAnalysis.analysis.analysis.key_abnormalities.length)||'0', 'var(--warning)')}
                  </div>

                  <div>
                    <h4 style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '6px' }}>Summary Insights</h4>
                    <p style={{ fontSize: '13px', color: 'var(--text-primary)', background: 'rgba(255,255,255,0.01)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                      {latestAnalysis.analysis.analysis.summary}
                      {latestAnalysis.analysis.analysis.recommendations && latestAnalysis.analysis.analysis.recommendations.length > 0 && (
                        <div style={{ marginTop: '12px' }}>
                          <h4 style={{ fontSize: '13px', color: 'var(--success)', marginBottom: '6px' }}>✅ Recommendations</h4>
                          <ul style={{ paddingLeft: '20px', fontSize: '13px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            {latestAnalysis.analysis.analysis.recommendations.map((rec, idx) => (
                              <li key={idx} style={{ color: 'var(--text-primary)' }}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                     
                    </p>
                  </div>

                  {latestAnalysis.analysis.analysis.key_abnormalities && latestAnalysis.analysis.analysis.key_abnormalities.length > 0 && (
                    <div>
                      <h4 style={{ fontSize: '14px', color: 'var(--warning)', marginBottom: '6px' }}>⚠️ Key Abnormalities</h4>
                      <ul style={{ paddingLeft: '20px', fontSize: '13px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        {latestAnalysis.analysis.analysis.key_abnormalities.map((abn, idx) => (
                          <li key={idx} style={{ color: 'var(--text-primary)' }}>{abn}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '80%', color: 'var(--text-muted)' }}>
                  <Clipboard size={40} style={{ marginBottom: '12px' }} />
                  <span style={{ fontSize: '13px' }}>Upload a report to see diagnostic analysis results.</span>
                </div>
              )}
            </div>

          </div>

          {/* Directory: All Reports */}
          <div className="glass-card">
            <h3 style={{ fontSize: '18px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileCheck size={18} color="var(--success)" />
              Clinical Report Archive
            </h3>

            {reports.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)', fontSize: '13px' }}>
                No records uploaded yet. Select files or paste clinical text summaries above.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {reports.map((rep) => {
                  // console.log('Report item:', rep);
                  const isExpanded = expandedReportId === rep.file_id || expandedReportId === rep.id;
                  const repId = rep.file_id || rep.id;
                  
                  return (
                    <div key={repId} style={{ border: '1px solid var(--border)', borderRadius: '10px', background: 'rgba(255,255,255,0.01)', overflow: 'hidden' }}>
                      <div 
                        onClick={() => setExpandedReportId(isExpanded ? null : repId)}
                        className="flex-between"
                        style={{ padding: '16px 20px', cursor: 'pointer', hover: 'background: rgba(255,255,255,0.02)' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <FileText size={18} color="var(--primary)" />
                          <div>
                            <span style={{ fontSize: '14px', fontWeight: 600 }}>{ getReportName(rep.file_url)}</span>
                            <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                              <span>Format: {rep.file_type?.toUpperCase()}</span>
                              <span>Date: {new Date(rep.upload_time||rep.analyzed_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span className={`badge ${rep.status === 'analyzed' ? 'badge-success' : 'badge-info'}`}>
                            {rep.status || 'uploaded'}
                          </span>
                          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                        </div>
                      </div>

                      {isExpanded && (
                        <div style={{ padding: '20px', borderTop: '1px solid var(--border)', background: 'rgba(5, 13, 26, 0.5)', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                          <div>
                            <h4 style={{ fontSize: '13px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>Summary Evaluation</h4>
                            <p style={{ fontSize: '13px', lineHeight: 1.5 }}>{rep.analysis.analysis?.summary || 'No summary generated'}</p>
                          </div>

                          {rep.analysis.analysis?.key_abnormalities && rep.analysis.analysis.key_abnormalities.length > 0 && (
                            <div>
                              <h4 style={{ fontSize: '13px', color: 'var(--warning)', textTransform: 'uppercase', marginBottom: '6px' }}>Key Abnormalities</h4>
                              <ul style={{ paddingLeft: '20px', fontSize: '13px' }}>
                                {rep.analysis.analysis.key_abnormalities.map((item, idx) => <li key={idx}>{item}</li>)}
                              </ul>
                            </div>
                          )}

                          {rep.analysis.analysis?.recommendations && rep.analysis.analysis.recommendations.length > 0 && (
                            <div>
                              <h4 style={{ fontSize: '13px', color: 'var(--success)', textTransform: 'uppercase', marginBottom: '6px' }}>Recommendations</h4>
                              <ul style={{ paddingLeft: '20px', fontSize: '13px' }}>
                                {rep.analysis.analysis.recommendations.map((rec, idx) => <li key={idx}>{rec}</li>)}
                              </ul>
                            </div>
                          )}
                          {rep.analysis.analysis.insights && rep.analysis.analysis.insights.length > 0 && (
                            <div>
                              <h4 style={{ fontSize: '13px', color: 'var(--primary)', textTransform: 'uppercase', marginBottom: '6px' }}>Additional Insights</h4>
                              <ul style={{ paddingLeft: '20px', fontSize: '13px' }}>
                                {rep.analysis.analysis.insights.map((insight, idx) => <li key={idx}>{insight}</li>)}
                              </ul>
                            </div>
                           )}
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

      {/* Tab: Health Agent Chat */}
      {activeTab === 'chat' && (
        <div className="glass-card" style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: '450px' }}>
          <div className="flex-between" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '12px', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={18} color="var(--primary)" />
              Health Agent Co-Pilot
            </h3>
            <span className="badge badge-success">RAG Database Online</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, height: '350px', border: '1px solid var(--border)', borderRadius: '10px', overflow: 'hidden' }}>
            {/* Messages body */}
            <div style={{ flexGrow: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`chat-bubble ${msg.role === 'user' ? 'user' : 'agent'}`}>
                  {msg.text}
                </div>
              ))}
              {chatLoading && (
                <div className="chat-bubble agent" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="global-loading-bar" style={{ position: 'relative', width: '20px', height: '3px', margin: 0 }} />
                  Processing history database...
                </div>
              )}
            </div>

            {/* Input bar */}
            <form onSubmit={handleChatSend} className="chat-input-wrapper">
              <input
                type="text"
                value={chatQuestion}
                onChange={(e) => setChatQuestion(e.target.value)}
                placeholder="Ask anything about your clinical reports, BMI, blood sugar levels, etc."
                disabled={chatLoading}
                style={{ flexGrow: 1 }}
              />
              <button 
                type="submit" 
                className="btn btn-primary" 
                disabled={chatLoading || !chatQuestion.trim()}
                style={{ padding: '0 16px' }}
              >
                <Send size={16} />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Tab: Trends Charts */}
      {activeTab === 'trends' && (
        <div className="glass-card">
          <h3 style={{ fontSize: '18px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingUp size={18} color="var(--primary)" />
            Historical Biomarkers Trends
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '24px' }}>
            Values computed automatically from parsed laboratory diagnostics database. Hover coordinates to inspect.
          </p>

          {Object.keys(trends).length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
              <Activity size={32} style={{ marginBottom: '12px' }} />
              <p style={{ fontSize: '13px' }}>No biomarker trends extracted. Upload clinical records containing blood-work metrics.</p>
            </div>
          ) : (
            <div className="grid-2">
              {Object.entries(trends).map(([name, tData]) => {
                let badgeClass = 'badge-info';
                if (tData.trend === 'INCREASING') badgeClass = 'badge-danger';
                if (tData.trend === 'DECREASING') badgeClass = 'badge-success';

                return (
                  <div key={name} className="glass-card" style={{ padding: '20px', background: 'rgba(255,255,255,0.01)' }}>
                    <div className="flex-between" style={{ marginBottom: '16px' }}>
                      <div>
                        <h4 style={{ fontSize: '15px' }}>{tData.test_name}</h4>
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Units: {tData.units || 'N/A'}</span>
                      </div>
                      <span className={`badge ${badgeClass}`}>{tData.trend || 'STABLE'}</span>
                    </div>

                    <div className="grid-4" style={{ marginBottom: '16px', background: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: '8px', gap: '10px', textAlign: 'center' }}>
                      <div>
                        <div style={{ fontSize: '9px', color: 'var(--text-muted)' }}>LATEST</div>
                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{tData.latest_value}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '9px', color: 'var(--text-muted)' }}>AVG</div>
                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{tData.avg?.toFixed(1) || '0'}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '9px', color: 'var(--text-muted)' }}>MIN</div>
                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{tData.min}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '9px', color: 'var(--text-muted)' }}>MAX</div>
                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{tData.max}</div>
                      </div>
                    </div>

                    <TrendChart 
                      testName={tData.test_name} 
                      units={tData.units} 
                      points={tData.points} 
                      trend={tData.trend} 
                    />
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Tab: Health Profile Form */}
      {activeTab === 'profile' && (
        <div className="glass-card" style={{ maxWidth: '720px', margin: '0 auto' }}>
          <h3 style={{ fontSize: '18px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <User size={18} color="var(--primary)" />
            {userFullName}'s Personal Bio-Profile
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '24px' }}>
            Keep your vital metadata updated. This coordinates accuracy during RAG diagnostic reasoning.
          </p>

          <form onSubmit={handleProfileSave} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            <div className="grid-2">
              <div>
                <label htmlFor="birthdate">Date of Birth</label>
                <input
                  id="birthdate"
                  type="date"
                  value={profile.birthdate}
                  onChange={(e) => setProfile({ ...profile, birthdate: e.target.value })}
                />
              </div>

              <div>
                <label htmlFor="gender">Biological Sex</label>
                <select
                  id="gender"
                  value={profile.gender}
                  onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                  style={{backgroundColor: "#141d2b",color: "#ffffff"}}
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div className="grid-3">
              <div>
                <label htmlFor="height">Height (cm)</label>
                <input
                  id="height"
                  type="number"
                  value={profile.height}
                  onChange={(e) => setProfile({ ...profile, height: parseInt(e.target.value) || 0 })}
                />
              </div>

              <div>
                <label htmlFor="weight">Weight (kg)</label>
                <input
                  id="weight"
                  type="number"
                  value={profile.weight}
                  onChange={(e) => setProfile({ ...profile, weight: parseFloat(e.target.value) || 0 })}
                />
              </div>

              <div>
                <label>Calculated BMI</label>
                <div style={{
                  padding: '12px 16px',
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  color: 'var(--primary)'
                }}>
                  {calculateBMI()}
                </div>
              </div>
            </div>

            <div className="grid-2">
              <div>
                <label htmlFor="blood_type">Blood Type</label>
                <input
                  id="blood_type"
                  type="text"
                  placeholder="e.g. A+, O-"
                  value={profile.blood_type}
                  onChange={(e) => setProfile({ ...profile, blood_type: e.target.value })}
                />
              </div>

              <div>
                <label htmlFor="sleep_hours">Average Sleep (Hours)</label>
                <input
                  id="sleep_hours"
                  type="number"
                  value={profile.sleep_hours}
                  onChange={(e) => setProfile({ ...profile, sleep_hours: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>

            <div>
              <label htmlFor="stress_level">Stress Index Level (1-10): {profile.stress_level}</label>
              <input
                id="stress_level"
                type="range"
                min="1"
                max="10"
                value={profile.stress_level}
                onChange={(e) => setProfile({ ...profile, stress_level: parseInt(e.target.value) })}
                style={{ padding: 0 }}
              />
            </div>

            <div>
              <label htmlFor="conditions">Chronic Conditions (Comma Separated)</label>
              <input
                id="conditions"
                type="text"
                placeholder="e.g. Asthma, Hypertension"
                value={profile.chronic_conditions}
                onChange={(e) => setProfile({ ...profile, chronic_conditions: e.target.value })}
              />
            </div>

            <div>
              <label htmlFor="lifestyle">Lifestyle & Diet Habit Notes</label>
              <textarea
                id="lifestyle"
                placeholder="e.g. Vegeterian, active runner, works out 3x weekly..."
                value={profile.lifestyle}
                onChange={(e) => setProfile({ ...profile, lifestyle: e.target.value })}
                style={{ minHeight: '80px' }}
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={profileSaving}
              style={{ width: '100%', marginTop: '12px' }}
            >
              {profileSaving ? 'Saving Bio-metrics...' : 'Save Health Profile'}
            </button>

          </form>
        </div>
      )}

    </div>
  );
}
