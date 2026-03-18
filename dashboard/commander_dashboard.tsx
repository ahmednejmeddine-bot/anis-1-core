import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AgentInfo {
  id: string
  name: string
  description: string
  capabilities: string[]
  status: string
}

interface ActivityEntry {
  task: string
  agents_dispatched: string[]
  timestamp: string
  payload_keys: string[]
}

interface CouncilStatus {
  session_uptime_s: number
  session_started: string
  total_tasks_dispatched: number
  agents: Record<string, { status: string; last_run: string | null }>
}

interface Alert {
  alert_id: string
  severity: string
  message: string
  component: string
  timestamp: string
  acknowledged: boolean
}

interface AIResponse {
  agent: string
  agent_name: string
  agents_used: string[]
  agent_count: number
  execution_mode: 'single_agent' | 'crew'
  reviewer_included?: boolean
  task: string
  response: string
  model: string
  auto_routed: boolean
  execution_time_s?: number
  output_path?: string
  timestamp: string
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const AGENT_COLORS: Record<string, string> = {
  finance: '#6366f1',
  operations: '#22d3ee',
  strategy: '#f59e0b',
  document: '#a78bfa',
  watchtower: '#4ade80',
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#6b7280',
  info: '#3b82f6',
}

const AGENT_OPTIONS = [
  { value: '', label: 'Auto-route (recommended)' },
  { value: 'crew', label: '🤝 Full CrewAI Council (all agents + reviewer)' },
  { value: 'finance', label: 'FinanceAgent' },
  { value: 'operations', label: 'OperationsAgent' },
  { value: 'strategy', label: 'StrategyAgent' },
  { value: 'document', label: 'DocumentAgent' },
  { value: 'watchtower', label: 'WatchtowerAgent' },
  { value: 'reviewer', label: 'ReviewerAgent' },
]

const EXAMPLE_TASKS = [
  'Analyze budget variance and recommend cost reductions for Q2',
  'What are the top 3 operational risks this quarter?',
  'Draft a market entry strategy for the GCC region',
  'Summarise the key findings from our latest performance review',
  'Run a health check and flag any anomalies in system uptime',
]

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h}h ${m}m ${s}s`
}

function timeAgo(iso: string): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatusBadge({ status }: { status: string }) {
  const color = status === 'active' ? '#4ade80' : status === 'idle' ? '#6b7280' : '#ef4444'
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: 12, color }}>
      <span style={{ width: 7, height: 7, borderRadius: '50%', background: color, display: 'inline-block', boxShadow: `0 0 5px ${color}` }} />
      {status}
    </span>
  )
}

function AgentCard({ agent, detail }: { agent: AgentInfo; detail?: { status: string; last_run: string | null } }) {
  const color = AGENT_COLORS[agent.id] || '#6366f1'
  return (
    <div style={{
      background: '#111827', border: `1px solid ${color}33`, borderRadius: 12, padding: '1.25rem', transition: 'box-shadow 0.2s',
    }}
      onMouseEnter={e => (e.currentTarget.style.boxShadow = `0 0 20px ${color}33`)}
      onMouseLeave={e => (e.currentTarget.style.boxShadow = 'none')}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
        <span style={{ fontWeight: 700, fontSize: 15, color }}>{agent.name}</span>
        {detail && <StatusBadge status={detail.status} />}
      </div>
      <p style={{ color: '#94a3b8', fontSize: 12, marginBottom: 10, lineHeight: 1.5 }}>{agent.description}</p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
        {agent.capabilities.map(cap => (
          <span key={cap} style={{
            background: `${color}18`, color, border: `1px solid ${color}44`,
            borderRadius: 999, padding: '2px 8px', fontSize: 10, fontFamily: 'monospace',
          }}>{cap}</span>
        ))}
      </div>
      {detail?.last_run && (
        <p style={{ color: '#475569', fontSize: 11, marginTop: 10 }}>Last run: {timeAgo(detail.last_run)}</p>
      )}
    </div>
  )
}

function ActivityFeed({ entries }: { entries: ActivityEntry[] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {entries.length === 0 && <p style={{ color: '#475569', fontSize: 13, textAlign: 'center', padding: '1rem 0' }}>No activity yet</p>}
      {[...entries].reverse().slice(0, 30).map((e, i) => (
        <div key={i} style={{ background: '#0f172a', borderRadius: 8, padding: '0.6rem 0.9rem', borderLeft: '3px solid #6366f1' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#a5b4fc', fontWeight: 600, fontSize: 13, fontFamily: 'monospace' }}>{e.task}</span>
            <span style={{ color: '#475569', fontSize: 11 }}>{timeAgo(e.timestamp)}</span>
          </div>
          <span style={{ color: '#64748b', fontSize: 11 }}>→ {e.agents_dispatched.join(', ')}</span>
        </div>
      ))}
    </div>
  )
}

function AlertPanel({ alerts }: { alerts: Alert[] }) {
  const sorted = [...alerts].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {sorted.length === 0 && <p style={{ color: '#475569', fontSize: 13, textAlign: 'center', padding: '1rem 0' }}>No alerts</p>}
      {sorted.slice(0, 10).map(alert => {
        const color = SEVERITY_COLORS[alert.severity] || '#6b7280'
        return (
          <div key={alert.alert_id} style={{
            background: '#0f172a', borderLeft: `3px solid ${color}`, borderRadius: 8,
            padding: '0.6rem 0.9rem', opacity: alert.acknowledged ? 0.5 : 1,
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
              <span style={{ color, fontSize: 11, fontWeight: 700, textTransform: 'uppercase' }}>{alert.severity}</span>
              <span style={{ color: '#475569', fontSize: 11 }}>{timeAgo(alert.timestamp)}</span>
            </div>
            <p style={{ color: '#e2e8f0', fontSize: 13 }}>{alert.message}</p>
            <p style={{ color: '#475569', fontSize: 11, fontFamily: 'monospace' }}>{alert.component} · {alert.alert_id}</p>
          </div>
        )
      })}
    </div>
  )
}

function AIResponseCard({ result }: { result: AIResponse }) {
  const isCrew = result.execution_mode === 'crew'
  const color = isCrew ? '#a78bfa' : (AGENT_COLORS[result.agent] || '#6366f1')
  const modeLabel = isCrew ? 'CrewAI Council' : 'Single Agent'
  const modeBg = isCrew ? '#a78bfa' : '#6366f1'

  return (
    <div style={{
      background: '#0d1117', border: `1px solid ${color}44`, borderRadius: 12,
      padding: '1.25rem', marginTop: 16,
    }}>
      {/* Header row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          {/* Execution mode badge */}
          <span style={{
            background: `${modeBg}22`, color: modeBg, border: `1px solid ${modeBg}55`,
            borderRadius: 999, padding: '3px 10px', fontSize: 11, fontWeight: 700,
          }}>
            {modeLabel}
          </span>
          {/* Agent name */}
          <span style={{
            background: `${color}18`, color, border: `1px solid ${color}44`,
            borderRadius: 999, padding: '3px 10px', fontSize: 11, fontWeight: 700,
          }}>
            {result.agent_name}
          </span>
          {/* Reviewer badge */}
          {result.reviewer_included && (
            <span style={{
              background: '#4ade8018', color: '#4ade80', border: '1px solid #4ade8044',
              borderRadius: 999, padding: '3px 10px', fontSize: 11, fontWeight: 700,
            }}>
              ✓ Reviewer
            </span>
          )}
          {result.auto_routed && (
            <span style={{ color: '#475569', fontSize: 11 }}>auto-routed</span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {result.execution_time_s && (
            <span style={{ color: '#64748b', fontSize: 11, fontFamily: 'monospace' }}>
              {result.execution_time_s}s
            </span>
          )}
          <span style={{ color: '#4ade80', fontSize: 11, fontFamily: 'monospace' }}>{result.model}</span>
          <span style={{ color: '#475569', fontSize: 11 }}>{timeAgo(result.timestamp)}</span>
        </div>
      </div>

      {/* Agents used (crew mode) */}
      {isCrew && result.agents_used && result.agents_used.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 12 }}>
          {result.agents_used.map(a => {
            const ac = a === 'reviewer' ? '#4ade80' : (AGENT_COLORS[a] || '#6366f1')
            return (
              <span key={a} style={{
                background: `${ac}14`, color: ac, border: `1px solid ${ac}33`,
                borderRadius: 999, padding: '2px 8px', fontSize: 10, fontFamily: 'monospace',
              }}>{a}</span>
            )
          })}
        </div>
      )}

      {/* Task label */}
      <p style={{ color: '#64748b', fontSize: 11, marginBottom: 12, fontStyle: 'italic' }}>
        "{result.task}"
      </p>

      {/* Response body */}
      <div style={{
        color: '#e2e8f0', fontSize: 13.5, lineHeight: 1.75,
        whiteSpace: 'pre-wrap', wordBreak: 'break-word',
      }}>
        {result.response}
      </div>

      {/* Output file path */}
      {result.output_path && (
        <div style={{
          marginTop: 14, background: '#0f172a', borderRadius: 6,
          padding: '0.5rem 0.75rem', borderLeft: '3px solid #4ade8055',
        }}>
          <span style={{ color: '#475569', fontSize: 11 }}>Report saved → </span>
          <span style={{ color: '#4ade80', fontSize: 11, fontFamily: 'monospace' }}>{result.output_path}</span>
        </div>
      )}
    </div>
  )
}

function DispatchPanel({ onDispatched }: { onDispatched: () => void }) {
  const [task, setTask] = useState('')
  const [agentKey, setAgentKey] = useState('')
  const [context, setContext] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiResult, setAiResult] = useState<AIResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const selectStyle = {
    background: '#0f172a', border: '1px solid #1f2937', borderRadius: 8,
    color: '#f1f5f9', padding: '0.5rem 0.75rem', fontSize: 13, width: '100%',
  }

  const inputStyle = {
    ...selectStyle,
    resize: 'vertical' as const,
  }

  const dispatch = async () => {
    if (!task.trim()) return
    setLoading(true)
    setAiResult(null)
    setError(null)
    try {
      const res = await axios.post('/dispatch_task', {
        task: task.trim(),
        agent: agentKey || undefined,
        context: context.trim() || undefined,
      })
      setAiResult(res.data)
      onDispatched()
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(detail || 'Request failed. Check that the backend is running and your OpenAI key is set.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 720 }}>
      <p style={{ color: '#94a3b8', fontSize: 13, marginBottom: 16, lineHeight: 1.6 }}>
        Type any business task below and let the AI Council route it to the right agent, powered by GPT-4o.
      </p>

      {/* Example tasks */}
      <div style={{ marginBottom: 14 }}>
        <p style={{ color: '#475569', fontSize: 11, marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Examples</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {EXAMPLE_TASKS.map(ex => (
            <button key={ex} onClick={() => setTask(ex)} style={{
              background: '#111827', border: '1px solid #1f2937', borderRadius: 999,
              color: '#64748b', padding: '3px 10px', fontSize: 11, cursor: 'pointer',
              transition: 'all 0.15s',
            }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.color = '#a5b4fc' }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = '#1f2937'; e.currentTarget.style.color = '#64748b' }}
            >
              {ex}
            </button>
          ))}
        </div>
      </div>

      {/* Task input */}
      <div style={{ marginBottom: 10 }}>
        <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 5 }}>Task *</label>
        <textarea
          value={task}
          onChange={e => setTask(e.target.value)}
          placeholder="Describe what you want the agent to do..."
          rows={3}
          style={{ ...inputStyle, width: '100%' }}
          onKeyDown={e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) dispatch() }}
        />
      </div>

      {/* Agent + Context row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 10, marginBottom: 14 }}>
        <div>
          <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 5 }}>Agent</label>
          <select value={agentKey} onChange={e => setAgentKey(e.target.value)} style={selectStyle}>
            {AGENT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <div>
          <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 5 }}>Context (optional)</label>
          <input
            value={context}
            onChange={e => setContext(e.target.value)}
            placeholder="Extra background for the agent..."
            style={{ ...selectStyle, width: '100%' }}
          />
        </div>
      </div>

      {/* Dispatch button */}
      <button
        onClick={dispatch}
        disabled={loading || !task.trim()}
        style={{
          background: loading || !task.trim() ? '#374151' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
          color: '#fff', border: 'none', borderRadius: 8, padding: '0.65rem 1.75rem',
          cursor: loading || !task.trim() ? 'not-allowed' : 'pointer',
          fontWeight: 700, fontSize: 14, transition: 'all 0.2s',
          display: 'flex', alignItems: 'center', gap: 8,
        }}
      >
        {loading ? (
          <>
            <span style={{ display: 'inline-block', width: 14, height: 14, border: '2px solid #ffffff44', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
            Thinking...
          </>
        ) : 'Send to Agent  ↵'}
      </button>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      {/* Error */}
      {error && (
        <div style={{
          marginTop: 14, background: '#1c0a0a', border: '1px solid #ef444444',
          borderRadius: 8, padding: '0.75rem 1rem', color: '#fca5a5', fontSize: 13,
        }}>
          {error}
        </div>
      )}

      {/* AI Response */}
      {aiResult && <AIResponseCard result={aiResult} />}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main Dashboard
// ---------------------------------------------------------------------------

export default function CommanderDashboard() {
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [councilStatus, setCouncilStatus] = useState<CouncilStatus | null>(null)
  const [activity, setActivity] = useState<ActivityEntry[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null)
  const [openaiConfigured, setOpenaiConfigured] = useState<boolean | null>(null)
  const [activeTab, setActiveTab] = useState<'agents' | 'activity' | 'alerts' | 'dispatch'>('agents')

  const fetchAll = useCallback(async () => {
    try {
      const [agentsRes, statusRes, activityRes, alertsRes, healthRes] = await Promise.allSettled([
        axios.get('/api/council/agents'),
        axios.get('/api/council/status'),
        axios.get('/api/council/activity?limit=30'),
        axios.get('/api/agents/watchtower/alerts'),
        axios.get('/health'),
      ])

      if (agentsRes.status === 'fulfilled') setAgents(agentsRes.value.data.agents)
      if (statusRes.status === 'fulfilled') setCouncilStatus(statusRes.value.data)
      if (activityRes.status === 'fulfilled') setActivity(activityRes.value.data.log)
      if (alertsRes.status === 'fulfilled') setAlerts(alertsRes.value.data.alerts)
      if (healthRes.status === 'fulfilled') setOpenaiConfigured(healthRes.value.data.openai_configured)
      setBackendOnline(true)
    } catch {
      setBackendOnline(false)
    }
  }, [])

  useEffect(() => {
    fetchAll()
    const interval = setInterval(fetchAll, 8000)
    return () => clearInterval(interval)
  }, [fetchAll])

  const unacknowledgedAlerts = alerts.filter(a => !a.acknowledged)

  const tabs = [
    { id: 'agents' as const, label: 'Agents', count: agents.length },
    { id: 'activity' as const, label: 'Activity', count: activity.length },
    { id: 'alerts' as const, label: 'Alerts', count: unacknowledgedAlerts.length },
    { id: 'dispatch' as const, label: 'AI Dispatch', count: null },
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#0a0d14', color: '#f1f5f9', fontFamily: "'Segoe UI', system-ui, sans-serif" }}>

      {/* Header */}
      <header style={{
        borderBottom: '1px solid #1f2937', padding: '1rem 2rem',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#0d1117',
      }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 800, background: 'linear-gradient(135deg, #6366f1, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            ANIS-1 Commander
          </h1>
          <p style={{ color: '#475569', fontSize: 12, marginTop: 2 }}>Abdeljelil Group · AI Operations, Strategy & Automation</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {councilStatus && (
            <span style={{ color: '#64748b', fontSize: 12 }}>
              Uptime: <span style={{ color: '#a5b4fc' }}>{formatUptime(councilStatus.session_uptime_s)}</span>
            </span>
          )}
          {openaiConfigured !== null && (
            <span style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 12 }}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', background: openaiConfigured ? '#4ade80' : '#f59e0b', display: 'inline-block' }} />
              <span style={{ color: openaiConfigured ? '#4ade80' : '#f59e0b' }}>{openaiConfigured ? 'GPT-4o Ready' : 'No OpenAI Key'}</span>
            </span>
          )}
          <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
            <span style={{
              width: 8, height: 8, borderRadius: '50%',
              background: backendOnline === null ? '#eab308' : backendOnline ? '#4ade80' : '#ef4444',
              boxShadow: backendOnline ? '0 0 6px #4ade80' : undefined, display: 'inline-block',
            }} />
            <span style={{ color: backendOnline ? '#4ade80' : '#ef4444' }}>
              {backendOnline === null ? 'Connecting…' : backendOnline ? 'API Online' : 'API Offline'}
            </span>
          </span>
        </div>
      </header>

      {/* Stats bar */}
      {councilStatus && (
        <div style={{ display: 'flex', gap: 1, background: '#111827', borderBottom: '1px solid #1f2937' }}>
          {[
            { label: 'Agents', value: Object.keys(councilStatus.agents).length },
            { label: 'Tasks Dispatched', value: councilStatus.total_tasks_dispatched },
            { label: 'Active Agents', value: Object.values(councilStatus.agents).filter(a => a.status === 'active').length },
            { label: 'Unacknowledged Alerts', value: unacknowledgedAlerts.length },
          ].map(stat => (
            <div key={stat.label} style={{ flex: 1, padding: '0.75rem 1.5rem', borderRight: '1px solid #1f2937' }}>
              <p style={{ color: '#475569', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{stat.label}</p>
              <p style={{ color: '#f1f5f9', fontSize: 22, fontWeight: 700, marginTop: 2 }}>{stat.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #1f2937', padding: '0 2rem', background: '#0d1117' }}>
        {tabs.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
            background: 'none', border: 'none',
            borderBottom: activeTab === tab.id ? '2px solid #6366f1' : '2px solid transparent',
            color: activeTab === tab.id ? '#a5b4fc' : '#475569',
            padding: '0.75rem 1.25rem', cursor: 'pointer', fontSize: 13, fontWeight: 600,
            display: 'flex', alignItems: 'center', gap: 6, transition: 'color 0.15s',
          }}>
            {tab.label}
            {tab.count !== null && tab.count > 0 && (
              <span style={{
                background: tab.id === 'alerts' && unacknowledgedAlerts.length > 0 ? '#ef4444' : '#6366f133',
                color: tab.id === 'alerts' && unacknowledgedAlerts.length > 0 ? '#fff' : '#a5b4fc',
                borderRadius: 999, padding: '1px 7px', fontSize: 11,
              }}>{tab.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <main style={{ padding: '1.5rem 2rem', maxWidth: 1200, margin: '0 auto' }}>

        {activeTab === 'agents' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
            {agents.map(agent => (
              <AgentCard key={agent.id} agent={agent} detail={councilStatus?.agents[agent.id]} />
            ))}
            {agents.length === 0 && backendOnline === false && (
              <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: '#475569' }}>
                <p style={{ fontSize: 16, marginBottom: 8 }}>Backend API is offline</p>
                <p style={{ fontSize: 13 }}>Start the Python API server to connect the dashboard.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'activity' && <ActivityFeed entries={activity} />}
        {activeTab === 'alerts' && <AlertPanel alerts={alerts} />}
        {activeTab === 'dispatch' && <DispatchPanel onDispatched={fetchAll} />}
      </main>
    </div>
  )
}
