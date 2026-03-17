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
  agents: Record<string, { status: string; last_run: string | null; description?: string; capabilities?: string[] }>
}

interface Alert {
  alert_id: string
  severity: string
  message: string
  component: string
  timestamp: string
  acknowledged: boolean
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
      background: '#111827',
      border: `1px solid ${color}33`,
      borderRadius: 12,
      padding: '1.25rem',
      transition: 'box-shadow 0.2s',
    }}
      onMouseEnter={e => (e.currentTarget.style.boxShadow = `0 0 20px ${color}33`)}
      onMouseLeave={e => (e.currentTarget.style.boxShadow = 'none')}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
        <div>
          <span style={{ fontWeight: 700, fontSize: 15, color }}>{agent.name}</span>
        </div>
        {detail && <StatusBadge status={detail.status} />}
      </div>
      <p style={{ color: '#94a3b8', fontSize: 12, marginBottom: 10, lineHeight: 1.5 }}>{agent.description}</p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
        {agent.capabilities.map(cap => (
          <span key={cap} style={{
            background: `${color}18`,
            color,
            border: `1px solid ${color}44`,
            borderRadius: 999,
            padding: '2px 8px',
            fontSize: 10,
            fontFamily: 'monospace',
          }}>{cap}</span>
        ))}
      </div>
      {detail?.last_run && (
        <p style={{ color: '#475569', fontSize: 11, marginTop: 10 }}>
          Last run: {timeAgo(detail.last_run)}
        </p>
      )}
    </div>
  )
}

function ActivityFeed({ entries }: { entries: ActivityEntry[] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {entries.length === 0 && (
        <p style={{ color: '#475569', fontSize: 13, textAlign: 'center', padding: '1rem 0' }}>No activity yet</p>
      )}
      {[...entries].reverse().slice(0, 20).map((e, i) => (
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
      {sorted.length === 0 && (
        <p style={{ color: '#475569', fontSize: 13, textAlign: 'center', padding: '1rem 0' }}>No alerts</p>
      )}
      {sorted.slice(0, 10).map(alert => {
        const color = SEVERITY_COLORS[alert.severity] || '#6b7280'
        return (
          <div key={alert.alert_id} style={{
            background: '#0f172a',
            borderLeft: `3px solid ${color}`,
            borderRadius: 8,
            padding: '0.6rem 0.9rem',
            opacity: alert.acknowledged ? 0.5 : 1,
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

function DispatchPanel({ onDispatched }: { onDispatched: () => void }) {
  const TASKS = [
    'budget_analysis', 'revenue_forecasting', 'risk_assessment',
    'process_monitoring', 'kpi_tracking', 'market_analysis',
    'document_summarisation', 'health_check', 'anomaly_detection', 'initiative_planning',
  ]

  const [task, setTask] = useState(TASKS[0])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  const dispatch = async () => {
    setLoading(true)
    setResult(null)
    try {
      const res = await axios.post('/api/council/dispatch', { task, payload: {} })
      setResult(JSON.stringify(res.data, null, 2))
      onDispatched()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail || (err as { message?: string })?.message || 'Unknown error'
      setResult(`Error: ${msg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
        <select
          value={task}
          onChange={e => setTask(e.target.value)}
          style={{
            flex: 1,
            background: '#0f172a',
            border: '1px solid #1f2937',
            borderRadius: 8,
            color: '#f1f5f9',
            padding: '0.5rem 0.75rem',
            fontSize: 13,
            fontFamily: 'monospace',
          }}
        >
          {TASKS.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <button
          onClick={dispatch}
          disabled={loading}
          style={{
            background: loading ? '#374151' : '#6366f1',
            color: '#fff',
            border: 'none',
            borderRadius: 8,
            padding: '0.5rem 1.25rem',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 600,
            fontSize: 13,
            transition: 'background 0.2s',
          }}
        >
          {loading ? '...' : 'Dispatch'}
        </button>
      </div>
      {result && (
        <pre style={{
          background: '#0a0d14',
          border: '1px solid #1f2937',
          borderRadius: 8,
          padding: '0.75rem',
          fontSize: 11,
          color: '#94a3b8',
          overflowX: 'auto',
          maxHeight: 240,
          overflowY: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}>{result}</pre>
      )}
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
  const [activeTab, setActiveTab] = useState<'agents' | 'activity' | 'alerts' | 'dispatch'>('agents')

  const fetchAll = useCallback(async () => {
    try {
      const [agentsRes, statusRes, activityRes, alertsRes] = await Promise.allSettled([
        axios.get('/api/council/agents'),
        axios.get('/api/council/status'),
        axios.get('/api/council/activity?limit=30'),
        axios.get('/api/agents/watchtower/alerts'),
      ])

      if (agentsRes.status === 'fulfilled') setAgents(agentsRes.value.data.agents)
      if (statusRes.status === 'fulfilled') setCouncilStatus(statusRes.value.data)
      if (activityRes.status === 'fulfilled') setActivity(activityRes.value.data.log)
      if (alertsRes.status === 'fulfilled') setAlerts(alertsRes.value.data.alerts)
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
    { id: 'dispatch' as const, label: 'Dispatch', count: null },
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#0a0d14', color: '#f1f5f9', fontFamily: "'Segoe UI', system-ui, sans-serif" }}>
      {/* Header */}
      <header style={{
        borderBottom: '1px solid #1f2937',
        padding: '1rem 2rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#0d1117',
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
          <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
            <span style={{
              width: 8, height: 8, borderRadius: '50%',
              background: backendOnline === null ? '#eab308' : backendOnline ? '#4ade80' : '#ef4444',
              boxShadow: backendOnline ? '0 0 6px #4ade80' : undefined,
              display: 'inline-block',
            }} />
            <span style={{ color: backendOnline ? '#4ade80' : '#ef4444' }}>
              {backendOnline === null ? 'Connecting…' : backendOnline ? 'API Online' : 'API Offline'}
            </span>
          </span>
        </div>
      </header>

      {/* Stats bar */}
      {councilStatus && (
        <div style={{
          display: 'flex', gap: 1, background: '#111827', borderBottom: '1px solid #1f2937',
        }}>
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
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              background: 'none',
              border: 'none',
              borderBottom: activeTab === tab.id ? '2px solid #6366f1' : '2px solid transparent',
              color: activeTab === tab.id ? '#a5b4fc' : '#475569',
              padding: '0.75rem 1.25rem',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              transition: 'color 0.15s',
            }}
          >
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
              <AgentCard
                key={agent.id}
                agent={agent}
                detail={councilStatus?.agents[agent.id]}
              />
            ))}
            {agents.length === 0 && backendOnline === false && (
              <div style={{
                gridColumn: '1 / -1',
                textAlign: 'center',
                padding: '3rem',
                color: '#475569',
              }}>
                <p style={{ fontSize: 16, marginBottom: 8 }}>Backend API is offline</p>
                <p style={{ fontSize: 13 }}>Start the Python API server to connect the dashboard.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'activity' && <ActivityFeed entries={activity} />}

        {activeTab === 'alerts' && <AlertPanel alerts={alerts} />}

        {activeTab === 'dispatch' && (
          <div style={{ maxWidth: 600 }}>
            <p style={{ color: '#94a3b8', fontSize: 13, marginBottom: 16 }}>
              Select a task and dispatch it to the AI Council. The council will route it to the appropriate agent(s) automatically.
            </p>
            <DispatchPanel onDispatched={fetchAll} />
          </div>
        )}
      </main>
    </div>
  )
}
