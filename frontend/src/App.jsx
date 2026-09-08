import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, 
  Layers, 
  ShieldAlert, 
  CheckCircle2, 
  Clock, 
  BrainCircuit, 
  Database,
  Network,
  Zap,
  ArrowRight,
  ServerCog,
  Wallet,
  FileText,
  Scale,
  MessageSquare,
  Receipt,
  Play,
  Send
} from 'lucide-react';
import './index.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [events, setEvents] = useState([]);
  const [hitlQueue, setHitlQueue] = useState([]);
  const [inbox, setInbox] = useState([]);
  const [replyText, setReplyText] = useState({});
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/ws/stream');
    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setEvents((prev) => [{ ...data, timestamp: new Date().toLocaleTimeString(), id: Date.now() }, ...prev].slice(0, 50));
        
        if (data.type === 'workflow_end' && data.data?.decision?.includes('Review')) {
          fetchHitlQueue();
        }
      } catch (e) {
        console.error("Failed to parse event", e);
      }
    };
    return () => ws.current?.close();
  }, []);

  const fetchHitlQueue = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/hitl/');
      const data = await res.json();
      setHitlQueue(data.queue || []);
    } catch (e) {
      console.error("Failed to fetch HITL", e);
    }
  };

  const fetchInbox = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/inbox');
      const data = await res.json();
      setInbox(data || []);
    } catch (e) {
      console.error("Failed to fetch Inbox", e);
    }
  };

  useEffect(() => {
    fetchHitlQueue();
    if (activeTab === 'inbox') {
      fetchInbox();
    }
  }, [activeTab]);

  const handleResolve = async (hitlId, resolution) => {
    try {
      await fetch(`http://localhost:8000/api/hitl/${hitlId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolution, notes: "Resolved by Human Admin" })
      });
      fetchHitlQueue();
    } catch (e) {
      console.error("Failed to resolve", e);
    }
  };

  const handleReply = async (paymentId) => {
    const text = replyText[paymentId];
    if (!text) return;
    
    try {
      await fetch(`http://localhost:8000/api/inbox/reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_id: paymentId, message: text })
      });
      setReplyText({ ...replyText, [paymentId]: '' });
      alert("Reply sent! The Swarm will now resume processing.");
      setActiveTab('dashboard'); // take them back to dashboard to watch it resume
    } catch (e) {
      console.error("Failed to reply", e);
    }
  };

  // Extract unique payments processed from events
  const paymentsProcessed = new Set(events.map(e => e.data?.payment_id).filter(Boolean)).size;

  const getAgentStyle = (agentName) => {
    switch(agentName) {
      case 'Payment Agent': return { icon: <Wallet size={16} />, color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.15)' };
      case 'Accounts Receivable Agent': 
      case 'AR Agent': return { icon: <Receipt size={16} />, color: '#10b981', bg: 'rgba(16, 185, 129, 0.15)' };
      case 'Risk Agent': return { icon: <ShieldAlert size={16} />, color: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)' };
      case 'Policy Agent': return { icon: <FileText size={16} />, color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.15)' };
      case 'Decision Agent': return { icon: <Scale size={16} />, color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)' };
      case 'Communication Agent': return { icon: <MessageSquare size={16} />, color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.15)' };
      default: return { icon: <BrainCircuit size={16} />, color: '#94a3b8', bg: 'rgba(148, 163, 184, 0.15)' };
    }
  };

  const parseDecisionJSON = (str) => {
    try {
      let clean = str;
      if (clean.startsWith('```json')) clean = clean.replace('```json', '').replace('```', '').trim();
      return JSON.parse(clean);
    } catch(e) {
      return null;
    }
  };

  return (
    <div className="app-layout">
      <div className="mesh-bg"></div>
      
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <BrainCircuit color="white" size={24} />
          </div>
          <h1>Agent Collab<br/>Platform</h1>
        </div>

        <nav className="nav-menu">
          <div 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <Activity size={20} />
            <span>Live Swarm</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'hitl' ? 'active' : ''}`}
            onClick={() => setActiveTab('hitl')}
          >
            <ShieldAlert size={20} />
            <span>Review Queue</span>
            {hitlQueue.length > 0 && <span className="badge">{hitlQueue.length}</span>}
          </div>
          <div 
            className={`nav-item ${activeTab === 'inbox' ? 'active' : ''}`}
            onClick={() => setActiveTab('inbox')}
          >
            <Mail size={20} />
            <span>Customer Inbox</span>
            {inbox.length > 0 && <span className="badge">{inbox.length}</span>}
          </div>
        </nav>
      </aside>

      <main className="main-content">
        <header className="header">
          <div>
            <h1 className="header-title">
              {activeTab === 'dashboard' ? 'Autonomous Execution Engine' : activeTab === 'hitl' ? 'Human-in-the-Loop Reviews' : 'Customer Communications (Mock)'}
            </h1>
            <p className="header-subtitle">
              {activeTab === 'dashboard' ? 'Real-time multi-agent orchestration and task handoffs.' : activeTab === 'hitl' ? 'Exceptions requiring human judgement and policy overrides.' : 'Emails drafted and sent by the Communication Agent to customers.'}
            </p>
          </div>
        </header>

        {activeTab === 'dashboard' && (
          <>
            <div className="stats-row">
              <div className="stat-card">
                <div className="stat-icon icon-blue"><Network size={24} /></div>
                <div className="stat-value">{events.length}</div>
                <div className="stat-label">Total Swarm Events</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon icon-purple"><Zap size={24} /></div>
                <div className="stat-value">{paymentsProcessed}</div>
                <div className="stat-label">Payments Investigated</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon icon-green"><Layers size={24} /></div>
                <div className="stat-value">4</div>
                <div className="stat-label">Active Agents</div>
              </div>
            </div>

            <div className="dashboard-grid">
              <div className="panel">
                <h2><Activity size={20} className="text-accent-blue" /> Live Orchestration Timeline</h2>
                {events.length === 0 ? (
                  <div style={{ color: 'var(--text-secondary)', marginTop: '2rem', textAlign: 'center' }}>
                    Waiting for events... Trigger a webhook to see agents in action.
                  </div>
                ) : (
                  <div className="timeline">
                    {events.map((evt) => (
                      <div key={evt.id} className="timeline-item">
                        <div className={`timeline-dot ${evt.type === 'workflow_end' ? 'success' : evt.type === 'workflow_start' ? 'warning' : ''}`}>
                          {evt.type === 'agent_transfer' ? <ArrowRight size={12} color="var(--accent-blue)" /> : 
                           evt.type === 'workflow_start' ? <Zap size={12} color="var(--warning)" /> : 
                           <CheckCircle2 size={12} color="var(--success)" />}
                        </div>
                        <div className="timeline-content">
                          <span className="timeline-time"><Clock size={12} style={{display:'inline', marginRight:'4px', verticalAlign:'middle'}}/>{evt.timestamp}</span>
                          
                          {evt.type === 'workflow_start' && (
                            <div>
                              <strong style={{color:'var(--warning)'}}>Initiated Investigation</strong>
                              <div style={{marginTop:'6px', display:'flex', alignItems:'center', gap:'0.5rem'}}>
                                <span className="data-tag"><Play size={12}/> Payment {evt.data.payment_id}</span>
                              </div>
                            </div>
                          )}
                          
                          {evt.type === 'agent_transfer' && (
                            <div>
                              <strong style={{display:'block', marginBottom:'0.75rem'}}>Autonomous Agent Handoff</strong>
                              <div style={{display:'flex', alignItems:'center', gap:'0.75rem', flexWrap: 'wrap'}}>
                                <div className="agent-pill" style={{'--agent-color': getAgentStyle(evt.data.from).color, '--agent-bg': getAgentStyle(evt.data.from).bg}}>
                                  {getAgentStyle(evt.data.from).icon} {evt.data.from}
                                </div>
                                <ArrowRight size={16} color="var(--text-secondary)" />
                                <div className="agent-pill" style={{'--agent-color': getAgentStyle(evt.data.to).color, '--agent-bg': getAgentStyle(evt.data.to).bg}}>
                                  {getAgentStyle(evt.data.to).icon} {evt.data.to}
                                </div>
                              </div>
                            </div>
                          )}
                          
                          {evt.type === 'workflow_end' && (
                            <div>
                              <strong style={{color:'var(--success)', display:'block', marginBottom:'0.5rem'}}>Consensus Reached</strong>
                              
                              {(() => {
                                const parsed = parseDecisionJSON(evt.data.decision);
                                if (parsed) {
                                  return (
                                    <div className="decision-card">
                                      <div className="decision-header">
                                        <span className={`decision-badge ${parsed.decision === 'Approve' ? 'badge-success' : parsed.decision === 'Reject' ? 'badge-danger' : 'badge-warning'}`}>
                                          {parsed.decision.toUpperCase()}
                                        </span>
                                        {parsed.confidence && (
                                          <div className="confidence-meter-container">
                                            <span style={{fontSize:'0.75rem', color:'var(--text-secondary)'}}>CONFIDENCE</span>
                                            <div className="confidence-meter">
                                              <div className="confidence-fill" style={{width: `${parsed.confidence * 100}%`, background: parsed.confidence > 0.8 ? 'var(--success)' : 'var(--warning)'}}></div>
                                            </div>
                                            <span style={{fontSize:'0.75rem', fontWeight:'600'}}>{Math.round(parsed.confidence * 100)}%</span>
                                          </div>
                                        )}
                                      </div>
                                      <div className="decision-reasoning">{parsed.reasoning}</div>
                                      {parsed.evidence && parsed.evidence.length > 0 && (
                                        <div className="decision-evidence">
                                          <div style={{fontSize:'0.75rem', color:'var(--text-secondary)', marginBottom:'0.25rem'}}>EVIDENCE</div>
                                          <div style={{display:'flex', flexWrap:'wrap', gap:'0.25rem'}}>
                                            {parsed.evidence.map((ev, i) => (
                                              <span key={i} className="evidence-tag">{ev}</span>
                                            ))}
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  );
                                } else {
                                  return (
                                    <div style={{marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', fontSize: '0.8rem', whiteSpace: 'pre-wrap'}}>
                                      {evt.data.decision}
                                    </div>
                                  );
                                }
                              })()}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="panel">
                <h2><ServerCog size={20} /> Infrastructure Status</h2>
                <div className="status-list" style={{ marginTop: '1.5rem' }}>
                  <div className="status-node">
                    <span style={{fontWeight:500}}>Event Stream (Redis)</span>
                    <div className="status-indicator">
                      <span style={{fontSize:'0.875rem', color:'var(--text-secondary)'}}>Healthy</span>
                      <div className="ping"></div>
                    </div>
                  </div>
                  <div className="status-node">
                    <span style={{fontWeight:500}}>Vector Memory (Qdrant)</span>
                    <div className="status-indicator">
                      <span style={{fontSize:'0.875rem', color:'var(--text-secondary)'}}>Healthy</span>
                      <div className="ping"></div>
                    </div>
                  </div>
                  <div className="status-node">
                    <span style={{fontWeight:500}}>Document DB (Mongo)</span>
                    <div className="status-indicator">
                      <span style={{fontSize:'0.875rem', color:'var(--text-secondary)'}}>Healthy</span>
                      <div className="ping"></div>
                    </div>
                  </div>
                  <div className="status-node">
                    <span style={{fontWeight:500}}>Orchestrator (Celery)</span>
                    <div className="status-indicator">
                      <span style={{fontSize:'0.875rem', color:'var(--text-secondary)'}}>Healthy</span>
                      <div className="ping"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {activeTab === 'hitl' && (
          <div className="hitl-grid">
            {hitlQueue.length === 0 ? (
              <div className="panel" style={{gridColumn: '1 / -1', textAlign: 'center', padding: '4rem'}}>
                <ShieldAlert size={48} color="var(--text-secondary)" style={{margin:'0 auto 1rem'}} />
                <h3 style={{fontSize:'1.25rem', marginBottom:'0.5rem'}}>Queue Empty</h3>
                <p style={{color:'var(--text-secondary)'}}>No exceptions pending human review.</p>
              </div>
            ) : (
              hitlQueue.map((item) => (
                <div key={item.hitl_id} className="hitl-card">
                  <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                    <span style={{color:'var(--text-secondary)', fontSize:'0.875rem'}}>{item.payment_id}</span>
                    <span style={{color:'var(--text-secondary)', fontSize:'0.75rem'}}>{new Date(item.created_at).toLocaleTimeString()}</span>
                  </div>
                  
                  <div className="hitl-amount">${item.context?.amount?.toLocaleString() || '0.00'}</div>
                  <div style={{fontWeight:500, fontSize:'1.1rem'}}>{item.context?.sender}</div>
                  
                  <div className="flags">
                    {item.context?.flags?.map(f => (
                      <span key={f} className="flag-badge">{f.replace('_', ' ')}</span>
                    ))}
                  </div>
                  
                  <div style={{marginTop:'1.5rem', marginBottom:'0.5rem', fontSize:'0.75rem', textTransform:'uppercase', letterSpacing:'0.05em', color:'var(--text-secondary)'}}>
                    Swarm AI Assessment
                  </div>
                  <div className="reasoning-box">
                    {item.reasoning}
                  </div>
                  
                  <div className="btn-group">
                    <button className="btn btn-reject" onClick={() => handleResolve(item.hitl_id, "Rejected")}>
                      Reject
                    </button>
                    <button className="btn btn-approve" onClick={() => handleResolve(item.hitl_id, "Approved")}>
                      <CheckCircle2 size={18} /> Approve
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'inbox' && (
          <div className="hitl-grid" style={{ gridTemplateColumns: '1fr' }}>
            {inbox.length === 0 ? (
              <div className="panel" style={{ textAlign: 'center', padding: '4rem' }}>
                <Mail size={48} color="var(--text-secondary)" style={{margin:'0 auto 1rem'}} />
                <h3 style={{fontSize:'1.25rem', marginBottom:'0.5rem'}}>Inbox Empty</h3>
                <p style={{color:'var(--text-secondary)'}}>No automated emails have been sent yet.</p>
              </div>
            ) : (
              inbox.map((msg) => (
                <div key={msg.id} className="hitl-card" style={{ maxWidth: '800px', margin: '0 auto', width: '100%', marginBottom: '1rem' }}>
                  <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem', marginBottom: '1rem'}}>
                    <div>
                      <div style={{color:'var(--text-secondary)', fontSize:'0.875rem'}}>To: <span style={{color: 'var(--text-primary)'}}>{msg.to}</span></div>
                      <div style={{color:'var(--text-secondary)', fontSize:'0.875rem'}}>From: {msg.from}</div>
                    </div>
                    <span style={{color:'var(--text-secondary)', fontSize:'0.75rem'}}>
                      <Send size={12} style={{display:'inline', marginRight:'4px'}}/>
                      {new Date(msg.timestamp).toLocaleString()}
                    </span>
                  </div>
                  
                  <div style={{fontWeight:500, fontSize:'1.1rem', marginBottom: '1rem'}}>Subject: {msg.subject}</div>
                  
                  <div className="reasoning-box" style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', marginBottom: '1.5rem' }}>
                    {msg.body}
                  </div>
                  
                  <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem' }}>
                    <div style={{marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500}}>Customer Reply (Simulation)</div>
                    <textarea 
                      style={{ width: '100%', minHeight: '80px', padding: '0.75rem', borderRadius: '4px', background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)', color: 'white', marginBottom: '1rem' }}
                      placeholder="Type a mock reply (e.g. 'The PO number is PO-12345')..."
                      value={replyText[msg.payment_id] || ''}
                      onChange={(e) => setReplyText({...replyText, [msg.payment_id]: e.target.value})}
                    />
                    <button 
                      className="btn btn-approve" 
                      onClick={() => handleReply(msg.payment_id)}
                      disabled={!replyText[msg.payment_id]}
                      style={{ opacity: replyText[msg.payment_id] ? 1 : 0.5 }}
                    >
                      <Send size={18} /> Send Reply & Resume Swarm
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}
