import { useEffect, useState } from 'react'
import axios from 'axios'
import './App.css'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts'
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Download,
  RefreshCw,
  Users,
  MessageSquare,
  Clock,
  Activity,
  Layers,
  ArrowRight,
  ExternalLink,
  CheckCircle2,
  Info
} from 'lucide-react'

const BACKEND_BASE = 'http://127.0.0.1:8000'

// Safe parsing of handles, URLs, and queries
function parseUsername(input) {
  if (!input) return ''
  let text = input.trim()
  // Strip URL query parameters (e.g. ?stkn=...)
  if (text.includes('?')) {
    text = text.split('?')[0]
  }
  // Strip URL hash
  if (text.includes('#')) {
    text = text.split('#')[0]
  }
  text = text.replace(/\/+$/, '')

  try {
    if (text.startsWith('http://') || text.startsWith('https://')) {
      const parsed = new URL(text)
      const segments = parsed.pathname.split('/').filter(Boolean)
      if (segments.length > 0) {
        return segments[segments.length - 1].replace(/^@/, '')
      }
    }
  } catch (e) {
    // Fall back to string splitting
  }

  if (text.includes('instagram.com/')) {
    const after = text.split('instagram.com/')[1]
    const segs = after.split('/').filter(Boolean)
    if (segs.length > 0) {
      return segs[0].replace(/^@/, '')
    }
  }

  const parts = text.split('/').filter(Boolean)
  const last = parts[parts.length - 1] || text
  return last.replace(/^@/, '').trim()
}

function App() {
  const [screen, setScreen] = useState('loading') // 'loading' | 'input' | 'dashboard'
  const [profileInput, setProfileInput] = useState('')
  const [activeUsername, setActiveUsername] = useState('demo_creator')
  
  const [loading, setLoading] = useState(false)
  const [downloadingPdf, setDownloadingPdf] = useState(false)
  const [error, setError] = useState('')

  const [influencer, setInfluencer] = useState(null)
  const [analysis, setAnalysis] = useState(null)

  // Initial startup screen transition
  useEffect(() => {
    const timer = setTimeout(() => {
      setScreen('input')
    }, 1800)
    return () => clearTimeout(timer)
  }, [])

  // Main API Call to Backend
  async function fetchAnalysis(usernameToQuery) {
    const target = usernameToQuery || 'demo_creator'
    setLoading(true)
    setError('')

    try {
      const response = await axios.get(`${BACKEND_BASE}/api/analyze/${encodeURIComponent(target)}`, {
        timeout: 25000
      })

      if (response.data.status === 'success') {
        setInfluencer(response.data.influencer)
        setAnalysis(response.data.analysis)
        setActiveUsername(response.data.username)
        setScreen('dashboard')
      } else {
        setError(response.data.message || 'Unable to analyze this profile.')
      }
    } catch (err) {
      console.error('Fetch error:', err)
      if (err.code === 'ERR_NETWORK') {
        setError('Cannot reach FastAPI backend at http://127.0.0.1:8000. Ensure backend server is running.')
      } else {
        setError(err.response?.data?.message || 'Error executing engagement analysis.')
      }
    } finally {
      setLoading(false)
    }
  }

  // Handle Form Submission
  async function handleAnalyze(e) {
    e.preventDefault()
    const cleanUser = parseUsername(profileInput)

    if (!cleanUser) {
      setError('Please enter a valid Instagram profile URL or username.')
      return
    }

    await fetchAnalysis(cleanUser)
  }

  // Download PDF Brand Trust Scorecard
  async function handleDownloadReport() {
    try {
      setDownloadingPdf(true)
      const user = activeUsername || 'demo_creator'
      const response = await axios.get(`${BACKEND_BASE}/api/report/${encodeURIComponent(user)}`, {
        responseType: 'blob',
        timeout: 30000
      })

      const blob = new Blob([response.data], { type: 'application/pdf' })
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.setAttribute('download', `EngagementPodGuard_Report_${user}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(downloadUrl)
    } catch (err) {
      console.error('PDF Download Error:', err)
      alert('Unable to generate PDF report at this moment. Ensure backend ReportLab service is active.')
    } finally {
      setDownloadingPdf(false)
    }
  }

  // ==========================================
  // RENDER: STARTUP SCREEN
  // ==========================================
  if (screen === 'loading') {
    return (
      <div className="startup-screen">
        <div className="startup-content">
          <div className="startup-logo">EP</div>
          <h1>EngagementPodGuard</h1>
          <p>
            Measure audience authenticity.
            <br />
            Detect coordinated engagement & LLM comment pods.
          </p>
          <div className="startup-loader">
            <div className="startup-loader-bar"></div>
          </div>
          <span className="startup-status">
            Initializing neural detection engine & NetworkX topology...
          </span>
        </div>
      </div>
    )
  }

  // ==========================================
  // RENDER: INPUT SCREEN
  // ==========================================
  if (screen === 'input') {
    return (
      <div className="profile-input-screen">
        <div className="profile-input-glow"></div>

        <div className="profile-input-card">
          <div className="input-logo">EP</div>

          <span className="input-eyebrow">
            AUDIENCE AUTHENTICITY INTELLIGENCE
          </span>

          <h1>Analyze Social Creator Profile</h1>

          <p className="input-description">
            Enter an Instagram profile URL or handle to evaluate engagement anomalies,
            semantic comment pods, timestamp concentration bursts, and account coordination networks.
          </p>

          <form onSubmit={handleAnalyze} className="profile-form">
            <label htmlFor="instagram-url">
              Instagram Profile URL or Username
            </label>

            <div className="url-input-wrapper">
              <span style={{ color: '#00d9ff', marginRight: '10px', display: 'flex', alignItems: 'center' }}>
                <ExternalLink size={18} />
              </span>
              <input
                id="instagram-url"
                type="text"
                value={profileInput}
                onChange={(e) => setProfileInput(e.target.value)}
                placeholder="Paste Instagram URL or username (e.g. https://www.instagram.com/nikbites_)"
                autoComplete="off"
              />
            </div>

            {error && (
              <div className="input-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="analyze-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="button-spinner"></span>
                  Analyzing Profile Signals...
                </>
              ) : (
                <>
                  Analyze Profile
                  <span className="button-arrow">→</span>
                </>
              )}
            </button>
          </form>

          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={() => {
                setProfileInput('https://www.instagram.com/nikbites_')
                fetchAnalysis('nikbites_')
              }}
              className="action-btn-secondary"
              style={{ fontSize: '11px', padding: '6px 14px', borderColor: 'rgba(0, 217, 255, 0.4)' }}
            >
              🔍 Live Scan: @nikbites_
            </button>

            <button
              type="button"
              onClick={() => {
                setProfileInput('demo_creator')
                fetchAnalysis('demo_creator')
              }}
              className="action-btn-secondary"
              style={{ fontSize: '11px', padding: '6px 14px' }}
            >
              📊 Benchmark Demo: @demo_creator
            </button>
          </div>

          <div className="input-security-note">
            <span>●</span>
            Explainable signals only. Product adheres to non-accusatory evaluation principles.
          </div>
        </div>
      </div>
    )
  }

  // ==========================================
  // RENDER: LOADING STATE
  // ==========================================
  if (loading && !analysis) {
    return (
      <div className="loading-screen">
        <div className="loader"></div>
        <h1>EngagementPodGuard</h1>
        <p>Evaluating engagement anomalies, semantic similarities, and network clusters...</p>
      </div>
    )
  }

  // ==========================================
  // RENDER: ERROR STATE
  // ==========================================
  if (error && !analysis) {
    return (
      <div className="error-screen">
        <h1>EngagementPodGuard</h1>
        <h2>Unable to load analysis</h2>
        <p>{error}</p>
        <button onClick={() => fetchAnalysis('demo_creator')}>
          Try Synthetic Demo Profile (demo_creator)
        </button>
      </div>
    )
  }

  // ==========================================
  // DERIVED METRICS FOR DASHBOARD
  // ==========================================
  const followers = influencer?.followers || 100000
  const following = influencer?.following || 850
  const ratio = following > 0 ? (followers / following).toFixed(1) : followers

  const authScore = analysis?.authenticity_score ?? 68.5
  const overallRisk = analysis?.overall_risk ?? 31.5
  const authLabel = analysis?.authenticity_label || (overallRisk > 65 ? 'ELEVATED RISK' : overallRisk > 30 ? 'MODERATE RISK' : 'LOW RISK')
  const authStatus = analysis?.authenticity_status || 'POTENTIAL ENGAGEMENT POD PATTERN'

  const authBadgeClass = overallRisk > 65 ? 'auth-badge-elevated' : overallRisk > 30 ? 'auth-badge-moderate' : 'auth-badge-low'

  const clusters = analysis?.clusters || []
  const evidence = analysis?.evidence || []
  const charts = analysis?.charts || {}

  // Chart data
  const trendData = charts.engagement_trend || []
  const timelineData = charts.timeline || []
  const riskComponents = charts.risk_components || [
    { name: 'Engagement Anomaly', score: analysis?.engagement_risk || 42, weight: '25%' },
    { name: 'Comment Similarity', score: analysis?.semantic_risk || 78, weight: '25%' },
    { name: 'Timestamp Coordination', score: analysis?.timing_risk || 81, weight: '25%' },
    { name: 'Account Coordination', score: analysis?.coordination_risk || 75, weight: '25%' }
  ]
  const pieData = charts.suspicious_vs_normal || [
    { name: 'Normal Comments', value: Math.max(0, (analysis?.total_comments || 1000) - (analysis?.suspicious_comments || 500)), color: '#10b981' },
    { name: 'Coordinated Comments', value: analysis?.suspicious_comments || 500, color: '#ef4444' }
  ]

  // Network graph preview
  const networkNodes = analysis?.network?.nodes || []
  const networkEdges = analysis?.network?.edges || []

  return (
    <div className="app">
      {/* ================= NAVBAR ================= */}
      <header className="navbar">
        <div className="brand" onClick={() => setScreen('input')} style={{ cursor: 'pointer' }}>
          <div className="brand-icon">EP</div>
          <div>
            <h1>EngagementPodGuard</h1>
            <span>Audience Authenticity & Pod Detector</span>
          </div>
        </div>

        <div className="navbar-actions">
          {influencer?.is_live ? (
            <div className="demo-badge" style={{ borderColor: 'rgba(16, 185, 129, 0.4)', color: '#34d399', background: 'rgba(16, 185, 129, 0.08)' }}>
              🟢 LIVE INSTAGRAM PROFILE
            </div>
          ) : (
            <div className="demo-badge">
              SYNTHETIC BENCHMARK DATA
            </div>
          )}
        </div>
      </header>

      {/* ================= MAIN DASHBOARD ================= */}
      <main className="dashboard">
        {/* ================= PROFILE CARD ================= */}
        <section className="profile-card">
          <div>
            <span className="section-label">ANALYZED PROFILE</span>
            <h2>@{influencer?.username}</h2>
            <p>{influencer?.profile_url || `https://instagram.com/${influencer?.username}`}</p>
          </div>

          <div className="profile-stats">
            <div>
              <strong>{followers.toLocaleString()}</strong>
              <span>Followers</span>
            </div>
            <div>
              <strong>{following.toLocaleString()}</strong>
              <span>Following</span>
            </div>
            <div>
              <strong>{ratio}:1</strong>
              <span>Follower/Following</span>
            </div>
            <div>
              <strong>{influencer?.posts_count || analysis?.total_posts || 20}</strong>
              <span>Analyzed Posts</span>
            </div>
          </div>
        </section>

        {/* ================= ACTION BAR ================= */}
        <div className="action-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button
              onClick={() => setScreen('input')}
              className="action-btn-secondary"
            >
              ← Analyze Another Profile
            </button>
            <button
              onClick={() => fetchAnalysis(activeUsername)}
              className="action-btn-secondary"
              disabled={loading}
            >
              <RefreshCw size={14} className={loading ? 'button-spinner' : ''} />
              Re-run Engine
            </button>
          </div>

          <button
            onClick={handleDownloadReport}
            className="download-scorecard-btn"
            disabled={downloadingPdf}
          >
            <Download size={16} />
            {downloadingPdf ? 'Building Scorecard PDF...' : 'Generate Brand Trust Scorecard'}
          </button>
        </div>

        {/* ================= HERO SECTION ================= */}
        <section className="hero-grid">
          {/* AUTHENTICITY INDICATOR */}
          <div className="authenticity-card">
            <span className="section-label">AUDIENCE AUTHENTICITY INDICATOR</span>

            <div className="score-row">
              <div className="score-circle">
                <div>
                  <strong>{authScore}</strong>
                  <span>/ 100</span>
                </div>
              </div>

              <div className="score-info">
                <h2>{authStatus}</h2>
                <p>
                  Composite indicator synthesized across 4 orthogonal dimensions:
                  engagement anomalies, semantic repetition, temporal burst windows, and account graph coordination.
                </p>
                <div className={`status-badge ${authBadgeClass}`} style={{ display: 'inline-block' }}>
                  {authLabel} • {analysis?.confidence || 'High Confidence'}
                </div>
              </div>
            </div>
          </div>

          {/* DETECTION SIGNALS BREAKDOWN */}
          <div className="risk-card">
            <span className="section-label">DETECTION SIGNALS (25% WEIGHT EACH)</span>

            <div className="risk-item">
              <span>Engagement Anomaly</span>
              <strong>{analysis?.engagement_risk}%</strong>
            </div>
            <div className="risk-bar">
              <div style={{ width: `${Math.min(100, analysis?.engagement_risk || 0)}%`, background: '#ffcb6b' }}></div>
            </div>

            <div className="risk-item">
              <span>Comment Semantic Similarity</span>
              <strong>{analysis?.semantic_risk}%</strong>
            </div>
            <div className="risk-bar">
              <div style={{ width: `${Math.min(100, analysis?.semantic_risk || 0)}%`, background: '#ff6b6b' }}></div>
            </div>

            <div className="risk-item">
              <span>Timestamp Coordination (Bursts)</span>
              <strong>{analysis?.timing_risk}%</strong>
            </div>
            <div className="risk-bar">
              <div style={{ width: `${Math.min(100, analysis?.timing_risk || 0)}%`, background: '#00d9ff' }}></div>
            </div>

            <div className="risk-item">
              <span>Account Coordination (Network)</span>
              <strong>{analysis?.coordination_risk}%</strong>
            </div>
            <div className="risk-bar">
              <div style={{ width: `${Math.min(100, analysis?.coordination_risk || 0)}%`, background: '#a78bfa' }}></div>
            </div>
          </div>
        </section>

        {/* ================= METRICS GRID ================= */}
        <section className="metrics-grid">
          <div className="metric-card">
            <span>Average Likes</span>
            <strong>{analysis?.avg_likes?.toLocaleString() || 0}</strong>
            <small>Across analyzed posts</small>
          </div>

          <div className="metric-card">
            <span>Average Comments</span>
            <strong>{analysis?.avg_comments?.toLocaleString() || 0}</strong>
            <small>Per post average</small>
          </div>

          <div className="metric-card">
            <span>Total Comments</span>
            <strong>{(analysis?.total_comments || 0).toLocaleString()}</strong>
            <small>Evaluated in dataset</small>
          </div>

          <div className="metric-card warning">
            <span>Suspicious Comments</span>
            <strong>{(analysis?.suspicious_comments || 0).toLocaleString()}</strong>
            <small>Pod templates & bursts</small>
          </div>

          <div className="metric-card warning">
            <span>Suspicious Accounts</span>
            <strong>{(analysis?.suspicious_accounts || 0).toLocaleString()}</strong>
            <small>Coordinated commenter accounts</small>
          </div>

          <div className="metric-card">
            <span>Detected Pod Clusters</span>
            <strong>{clusters.length}</strong>
            <small>Synchronized pods identified</small>
          </div>
        </section>

        {/* ================= VISUALIZATIONS SECTION ================= */}
        <section className="charts-grid">
          {/* ENGAGEMENT TREND CHART */}
          <div className="chart-card">
            <span className="section-label">POST-LEVEL ENGAGEMENT CONSISTENCY</span>
            <h3>Likes & Comments Across Posts</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient id="colorLikes" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00d9ff" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#00d9ff" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorComments" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#5865ff" stopOpacity={0.6} />
                      <stop offset="95%" stopColor="#5865ff" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(130, 160, 200, 0.1)" />
                  <XAxis dataKey="post_name" stroke="#61718a" fontSize={11} />
                  <YAxis stroke="#61718a" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      background: '#091326',
                      borderColor: 'rgba(130, 160, 200, 0.2)',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Area
                    type="monotone"
                    dataKey="likes"
                    name="Post Likes"
                    stroke="#00d9ff"
                    fillOpacity={1}
                    fill="url(#colorLikes)"
                  />
                  <Area
                    type="monotone"
                    dataKey="comments"
                    name="Comments"
                    stroke="#5865ff"
                    fillOpacity={1}
                    fill="url(#colorComments)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* SUSPICIOUS VS NORMAL PIE CHART */}
          <div className="chart-card">
            <span className="section-label">COMMENT COMPOSITION</span>
            <h3>Normal vs Coordinated Pod Activity</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: '#091326',
                      borderColor: 'rgba(130, 160, 200, 0.2)',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        {/* ================= TIMELINE BURST CHART ================= */}
        <section className="charts-grid" style={{ marginTop: '20px' }}>
          <div className="chart-card">
            <span className="section-label">ARRIVAL WINDOW CONCENTRATION</span>
            <h3>Comment Submission Velocity (Response Latency)</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={timelineData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(130, 160, 200, 0.1)" />
                  <XAxis dataKey="window" stroke="#61718a" fontSize={11} />
                  <YAxis stroke="#61718a" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      background: '#091326',
                      borderColor: 'rgba(130, 160, 200, 0.2)',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Bar dataKey="normal" name="Organic Activity" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="suspicious" name="Burst / Pod Spike" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card">
            <span className="section-label">RISK FACTOR MATRIX</span>
            <h3>Component Weight Breakdown (25% Each)</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={riskComponents} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(130, 160, 200, 0.1)" />
                  <XAxis type="number" domain={[0, 100]} stroke="#61718a" fontSize={11} />
                  <YAxis dataKey="name" type="category" stroke="#8c9cb5" fontSize={10} width={130} />
                  <Tooltip
                    contentStyle={{
                      background: '#091326',
                      borderColor: 'rgba(130, 160, 200, 0.2)',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                  <Bar dataKey="score" name="Risk Score (%)" fill="#00d9ff" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        {/* ================= NETWORK COORDINATION GRAPH ================= */}
        <section className="network-panel">
          <div className="panel-header">
            <div>
              <span className="section-label">TOPOLOGICAL COORDINATION GRAPH (NETWORKX)</span>
              <h2>Account Co-Occurrence & Pod Structure</h2>
            </div>
            <span className="cluster-count">{networkNodes.length} active nodes</span>
          </div>

          <p className="description">
            Nodes represent commenter accounts; edges connect accounts that frequently share identical templates
            and comment in tight sub-minute burst windows. Red nodes depict accounts belonging to detected pods.
          </p>

          <div className="network-svg-container">
            <svg width="100%" height="100%" viewBox="0 0 800 320">
              {/* Draw Edges */}
              {networkEdges.slice(0, 45).map((edge, idx) => {
                const x1 = 120 + ((idx * 47) % 560)
                const y1 = 40 + ((idx * 31) % 240)
                const x2 = x1 + (((idx % 5) - 2) * 55)
                const y2 = y1 + (((idx % 4) - 1.5) * 45)
                return (
                  <line
                    key={`edge-${idx}`}
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    stroke="rgba(239, 68, 68, 0.35)"
                    strokeWidth="1.5"
                    strokeDasharray="2 2"
                  />
                )
              })}

              {/* Draw Nodes */}
              {networkNodes.slice(0, 50).map((node, idx) => {
                const cx = 100 + ((idx * 53) % 600)
                const cy = 40 + ((idx * 27) % 240)
                const isSusp = node.is_suspicious
                return (
                  <g key={`node-${idx}`} transform={`translate(${cx}, ${cy})`}>
                    <circle
                      r={isSusp ? 7 : 5}
                      fill={isSusp ? '#ef4444' : '#10b981'}
                      stroke={isSusp ? 'rgba(239, 68, 68, 0.5)' : 'rgba(16, 185, 129, 0.3)'}
                      strokeWidth={isSusp ? 4 : 2}
                      opacity={0.9}
                    />
                  </g>
                )
              })}
            </svg>
          </div>

          <div className="network-legend">
            <div>
              <span className="legend-dot" style={{ background: '#ef4444' }}></span>
              Coordinated Pod Account (Repeated bursts & shared templates)
            </div>
            <div>
              <span className="legend-dot" style={{ background: '#10b981' }}></span>
              Normal Community Account
            </div>
          </div>
        </section>

        {/* ================= CLUSTERS SECTION ================= */}
        <section className="clusters-panel">
          <div className="panel-header">
            <div>
              <span className="section-label">COORDINATION CLUSTERS</span>
              <h2>Coordinated Engagement Clusters</h2>
            </div>
            <span className="cluster-count">{clusters.length} pods detected</span>
          </div>

          <div className="cluster-grid">
            {clusters.map((cluster, i) => (
              <div className="cluster-card" key={cluster.id || i}>
                <div className="cluster-top">
                  <h3>{cluster.cluster_name || `Cluster #${i + 1}`}</h3>
                  <span>Risk {cluster.risk_score}%</span>
                </div>

                <div className="cluster-stats">
                  <div>
                    <strong>{cluster.account_count}</strong>
                    <span>Accounts</span>
                  </div>
                  <div>
                    <strong>{cluster.comment_count}</strong>
                    <span>Comments</span>
                  </div>
                  <div>
                    <strong>{cluster.semantic_similarity}%</strong>
                    <span>Similarity</span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '10px', color: '#62e8ff' }}>
                  <span>Timing: {cluster.timing_score}%</span>
                  <span>Coordination: {cluster.coordination_score}%</span>
                </div>

                <div className="evidence-text">
                  {cluster.explanation || 'Accounts repeatedly interacted with identical templates in concentrated windows.'}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ================= EVIDENCE SECTION ("Why this result?") ================= */}
        <section className="evidence-section">
          <div className="panel-header">
            <div>
              <span className="section-label">EXPLAINABLE EVIDENCE</span>
              <h2>Why this result?</h2>
            </div>
            <span className="signal">EVIDENCE AUDIT</span>
          </div>

          <p className="description">
            Transparent breakdown of suspicious signals identified across semantic text analysis,
            arrival burst clustering, and account graph co-occurrence patterns.
          </p>

          <div className="evidence-grid">
            {evidence.map((item, idx) => {
              const sev = (item.severity || 'medium').toLowerCase()
              const sevClass = sev === 'high' ? 'severity-high' : sev === 'medium' ? 'severity-medium' : 'severity-low'

              return (
                <div className="evidence-card" key={idx}>
                  <div>
                    <div className="evidence-header">
                      <span className={`severity-pill ${sevClass}`}>{item.severity} severity</span>
                      <CheckCircle2 size={15} color={sev === 'high' ? '#ff6b6b' : '#ffcb6b'} />
                    </div>
                    <h4>{item.title}</h4>
                    <p>{item.message}</p>
                  </div>

                  {item.evidence && (
                    <div className="evidence-metrics">
                      {Object.entries(item.evidence).map(([k, v]) => (
                        <span className="metric-pill" key={k}>
                          {k.replace(/_/g, ' ')}: {v}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </section>

        {/* ================= DATA NOTICE & FOOTER ================= */}
        <div className="data-notice">
          <strong>Demo / Synthetic Dataset</strong>
          <span>
            This dashboard uses synthetic social media telemetry to demonstrate coordinated pod detection.
            Adhering to our core methodology, EngagementPodGuard presents explainable engagement anomalies
            without making unsubstantiated declarations of fraudulent intent.
          </span>
        </div>
      </main>
    </div>
  )
}

export default App