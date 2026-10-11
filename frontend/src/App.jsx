import { useEffect, useState } from 'react'

import {
  Activity,
  ArrowUpRight,
  BookOpen,
  Bookmark,
  BrainCircuit,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clock3,
  FileText,
  FlaskConical,
  FolderOpen,
  LayoutDashboard,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  Wifi,
  WifiOff,
  Command,
  TrendingUp,
  Layers3,
} from 'lucide-react'

import { checkBackend } from './services/api'

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard },
  { label: 'Discover Papers', icon: Search },
  { label: 'My Library', icon: FolderOpen },
  { label: 'AI Assistant', icon: BrainCircuit },
  { label: 'Evaluation Lab', icon: FlaskConical },
]

const demoPapers = [
  {
    tag: 'LLMs',
    title: 'Attention Is All You Need',
    authors: 'Vaswani et al.',
    year: '2017',
    description:
      'The foundational paper introducing the Transformer architecture based entirely on attention mechanisms.',
    color: 'violet',
  },
  {
    tag: 'RAG',
    title: 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks',
    authors: 'Lewis et al.',
    year: '2020',
    description:
      'Combines a parametric language model with retrieved non-parametric knowledge to improve generation.',
    color: 'blue',
  },
  {
    tag: 'Evaluation',
    title: 'Lost in the Middle: How Language Models Use Long Contexts',
    authors: 'Liu et al.',
    year: '2023',
    description:
      'Studies how language models use relevant information depending on its position in long contexts.',
    color: 'amber',
  },
]

const topics = [
  'AI Agents',
  'RAG',
  'Multimodal AI',
  'Long Context',
  'LLM Evaluation',
]

function App() {
  const [active, setActive] = useState('Dashboard')
  const [apiStatus, setApiStatus] = useState('checking')
  const [query, setQuery] = useState('')

  useEffect(() => {
    checkBackend()
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'))
  }, [])

  const visiblePapers = demoPapers.filter((paper) =>
    `${paper.title} ${paper.authors} ${paper.tag}`
      .toLowerCase()
      .includes(query.toLowerCase()),
  )

  const goTo = (page) => {
    setActive(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <BrainCircuit size={21} strokeWidth={1.7} />
          </div>

          <div>
            <strong>ResearchPilot</strong>
            <span>RESEARCH INTELLIGENCE</span>
          </div>
        </div>

        <button className="workspace-switch">
          <div className="workspace-avatar">R</div>

          <div className="workspace-copy">
            <strong>Research workspace</strong>
            <span>Personal plan</span>
          </div>

          <ChevronDown size={15} />
        </button>

        <div className="nav-label">WORKSPACE</div>

        <nav className="nav-list">
          {navItems.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`nav-item ${active === label ? 'active' : ''}`}
              onClick={() => goTo(label)}
            >
              <Icon size={18} strokeWidth={1.7} />
              <span>{label}</span>

              {label === 'Evaluation Lab' && (
                <span className="nav-badge">LAB</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="privacy-note">
            <ShieldCheck size={16} />

            <div>
              <strong>Private by design</strong>
              <span>
                Your research workspace is isolated and access-controlled.
              </span>
            </div>
          </div>

          <button className="nav-item">
            <Settings2 size={18} />
            <span>Settings</span>
          </button>

          <button className="nav-item">
            <CircleHelp size={18} />
            <span>Help & documentation</span>
          </button>

          <div className="profile">
            <div className="profile-avatar">SS</div>

            <div className="profile-copy">
              <strong>Researcher</strong>
              <span>Personal workspace</span>
            </div>

            <button className="icon-button" aria-label="Profile settings">
              <Settings2 size={16} />
            </button>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            <span>ResearchPilot</span>
            <span className="slash">/</span>
            <strong>{active}</strong>
          </div>

          <div className="topbar-right">
            <div className={`connection ${apiStatus}`}>
              {apiStatus === 'online' ? (
                <Wifi size={14} />
              ) : apiStatus === 'offline' ? (
                <WifiOff size={14} />
              ) : (
                <Activity size={14} />
              )}

              <span>
                {apiStatus === 'online'
                  ? 'System online'
                  : apiStatus === 'offline'
                    ? 'Backend offline'
                    : 'Connecting…'}
              </span>
            </div>

            <button className="help-button">
              <CircleHelp size={16} />
              Help
            </button>
          </div>
        </header>

        <div className="page-content">
          {active === 'Dashboard' ? (
            <Dashboard
              apiStatus={apiStatus}
              query={query}
              setQuery={setQuery}
              goTo={goTo}
            />
          ) : active === 'Discover Papers' ? (
            <DiscoverPage
              query={query}
              setQuery={setQuery}
              papers={visiblePapers}
              goTo={goTo}
            />
          ) : active === 'My Library' ? (
            <LibraryPage />
          ) : active === 'AI Assistant' ? (
            <AssistantPage />
          ) : (
            <EvaluationPage />
          )}
        </div>
      </main>
    </div>
  )
}


/* =========================================================
   DASHBOARD
   ========================================================= */

function Dashboard({ apiStatus, query, setQuery, goTo }) {
  return (
    <section className="research-dashboard">

      <div className="dashboard-intro">
        <div>
          <div className="eyebrow">
            <Sparkles size={13} />
            RESEARCH INTELLIGENCE
          </div>

          <h1>
            What are you
            <br />
            <em>investigating?</em>
          </h1>

          <p>
            Search the literature, interrogate your papers, and build
            knowledge with an AI research companion.
          </p>
        </div>

        <div className="workspace-status">
          <span className="status-pulse" />
          Workspace ready
        </div>
      </div>


      <div className="research-command">
        <div className="command-top">
          <span className="command-label">
            <Search size={18} />
            Research command
          </span>

          <span className="command-shortcut">
            <Command size={12} />
            K
          </span>
        </div>

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              goTo('Discover Papers')
            }
          }}
          placeholder="Search papers, authors, concepts, or research topics..."
        />

        <button
          className="command-submit"
          onClick={() => goTo('Discover Papers')}
          aria-label="Search research"
        >
          <ArrowUpRight size={19} />
        </button>

        <div className="command-footer">
          <span>Try searching for</span>

          {topics.slice(0, 3).map((topic) => (
            <button
              key={topic}
              onClick={() => {
                setQuery(topic)
                goTo('Discover Papers')
              }}
            >
              {topic}
            </button>
          ))}
        </div>
      </div>


      <div className="dashboard-grid">

        <section className="research-feed">
          <div className="section-heading">
            <div>
              <span className="section-kicker">LITERATURE</span>
              <h2>Recent discoveries</h2>
            </div>

            <button
              className="subtle-button"
              onClick={() => goTo('Discover Papers')}
            >
              View library
              <ArrowUpRight size={14} />
            </button>
          </div>

          <div className="paper-feed">
            {demoPapers.map((paper, index) => (
              <ResearchRow
                key={paper.title}
                paper={paper}
                number={String(index + 1).padStart(2, '0')}
                onOpen={() => goTo('Discover Papers')}
              />
            ))}
          </div>
        </section>


        <aside className="research-pulse">

          <div className="pulse-header">
            <div>
              <span className="section-kicker">WORKSPACE</span>
              <h2>Research pulse</h2>
            </div>

            <Activity size={18} />
          </div>

          <div className="pulse-main">
            <strong>03</strong>
            <span>preview papers<br />in your workspace</span>
          </div>

          <div className="pulse-divider" />

          <div className="pulse-stat">
            <span>Topics explored</span>
            <strong>05</strong>
          </div>

          <div className="pulse-stat">
            <span>AI readiness</span>
            <strong className="teal-text">
              {apiStatus === 'online' ? 'READY' : 'WAITING'}
            </strong>
          </div>

          <div className="pulse-topics">
            {topics.map((topic) => (
              <span key={topic}>{topic}</span>
            ))}
          </div>

          <button
            className="pulse-action"
            onClick={() => goTo('AI Assistant')}
          >
            <BrainCircuit size={17} />
            Open research assistant
            <ArrowUpRight size={15} />
          </button>
        </aside>

      </div>


      <section className="workflow-strip">
        <div className="workflow-title">
          <span className="section-kicker">WORKFLOW</span>
          <strong>Your research loop</strong>
        </div>

        <WorkflowStep
          number="01"
          icon={Search}
          title="Discover"
          text="Find relevant literature"
        />

        <WorkflowStep
          number="02"
          icon={FileText}
          title="Understand"
          text="Extract the important ideas"
        />

        <WorkflowStep
          number="03"
          icon={BrainCircuit}
          title="Question"
          text="Interrogate your sources"
        />

        <WorkflowStep
          number="04"
          icon={FlaskConical}
          title="Evaluate"
          text="Measure answer quality"
        />
      </section>

    </section>
  )
}


/* =========================================================
   DISCOVER
   ========================================================= */

function DiscoverPage({ query, setQuery, papers, goTo }) {
  return (
    <section className="research-discover">

      <div className="discover-header">
        <div>
          <div className="eyebrow">
            <Search size={13} />
            LITERATURE DISCOVERY
          </div>

          <h1>Discover research.</h1>

          <p>
            Explore academic literature by topic, title, author, or idea.
          </p>
        </div>

        <div className="result-count">
          <strong>{papers.length}</strong>
          <span>results</span>
        </div>
      </div>


      <div className="large-search">
        <Search size={20} />

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search papers, authors, concepts..."
          autoFocus
        />

        <span>ENTER</span>
      </div>


      <div className="topic-row">
        <span>EXPLORE TOPICS</span>

        {topics.map((topic) => (
          <button
            key={topic}
            onClick={() => setQuery(topic)}
          >
            {topic}
          </button>
        ))}
      </div>


      <div className="discover-list">

        <div className="list-heading">
          <span>DISCOVERIES</span>
          <span>YEAR</span>
        </div>

        {papers.map((paper, index) => (
          <ResearchRow
            key={paper.title}
            paper={paper}
            number={String(index + 1).padStart(2, '0')}
            onOpen={() => goTo('AI Assistant')}
          />
        ))}

        {papers.length === 0 && (
          <div className="empty-state">
            <Search size={22} />
            <strong>No matching papers</strong>
            <span>
              Try another topic or keyword. Live research search will be
              connected on Day 2.
            </span>
          </div>
        )}

      </div>

      <div className="demo-disclaimer">
        <CheckCircle2 size={14} />
        Preview literature only — live paper discovery is the next backend
        integration.
      </div>

    </section>
  )
}


/* =========================================================
   LIBRARY
   ========================================================= */

function LibraryPage() {
  return (
    <section className="simple-page redesigned-simple-page">

      <div className="eyebrow">
        <FolderOpen size={13} />
        YOUR KNOWLEDGE BASE
      </div>

      <h1>My library.</h1>

      <p className="subheading">
        Build a private research collection and turn documents into
        searchable knowledge.
      </p>

      <div className="library-layout">

        <div className="upload-panel">
          <div className="upload-icon">
            <UploadCloud size={28} />
          </div>

          <span className="section-kicker">DOCUMENT INGESTION</span>

          <h2>Bring a paper into ResearchPilot.</h2>

          <p>
            Upload a research document and the ingestion pipeline will
            prepare it for grounded AI conversations.
          </p>

          <button className="primary-button" disabled>
            <UploadCloud size={16} />
            Upload coming on Day 2
          </button>

          <small>
            PDF, DOCX and TXT support will be configured by the backend.
          </small>
        </div>

        <div className="library-empty">
          <Layers3 size={28} />
          <span className="section-kicker">YOUR COLLECTION</span>
          <strong>No documents yet.</strong>
          <p>
            Your uploaded papers, extracted metadata, and indexed chunks
            will appear here.
          </p>
        </div>

      </div>

    </section>
  )
}


/* =========================================================
   AI ASSISTANT
   ========================================================= */

function AssistantPage() {
  return (
    <section className="assistant-workspace">

      <div className="assistant-header">
        <div>
          <div className="eyebrow">
            <BrainCircuit size={13} />
            PAPER-GROUNDED INTELLIGENCE
          </div>

          <h1>Ask your research.</h1>

          <p>
            A grounded AI workspace for understanding papers, methods,
            findings, and limitations.
          </p>
        </div>
      </div>

      <div className="assistant-shell">

        <div className="assistant-orb">
          <BrainCircuit size={42} strokeWidth={1.2} />
        </div>

        <span className="section-kicker">RESEARCHPILOT AI</span>

        <h2>Your research conversation starts here.</h2>

        <p>
          Select or upload a paper first. Then ask questions grounded in
          the source instead of relying on unsupported answers.
        </p>

        <div className="suggestion-row">
          <button>Explain the main contribution</button>
          <button>What are the limitations?</button>
          <button>Explain the methodology</button>
        </div>

        <div className="chat-input-disabled">
          <span>Choose a paper to start asking questions…</span>

          <button disabled>
            <ArrowUpRight size={17} />
          </button>
        </div>

      </div>

    </section>
  )
}


/* =========================================================
   EVALUATION
   ========================================================= */

function EvaluationPage() {
  return (
    <section className="simple-page evaluation-page">

      <div className="eyebrow">
        <FlaskConical size={13} />
        QUALITY & RELIABILITY
      </div>

      <h1>Evaluation lab.</h1>

      <p className="subheading">
        Measure whether ResearchPilot answers accurately, retrieves the
        right evidence, and supports its claims.
      </p>

      <div className="metrics-grid">
        <Metric
          label="Faithfulness"
          value="—"
          caption="Awaiting evaluation"
        />

        <Metric
          label="Retrieval quality"
          value="—"
          caption="Awaiting evaluation"
        />

        <Metric
          label="Citation support"
          value="—"
          caption="Awaiting evaluation"
        />

        <Metric
          label="Latency"
          value="—"
          caption="Awaiting evaluation"
        />
      </div>

      <div className="evaluation-empty">
        <FlaskConical size={28} />
        <span className="section-kicker">NO BENCHMARK RUNS</span>
        <strong>Your evaluation workspace is ready.</strong>
        <p>
          Benchmarking will populate this area once the RAG pipeline is
          connected.
        </p>
      </div>

    </section>
  )
}


/* =========================================================
   COMPONENTS
   ========================================================= */

function ResearchRow({ paper, number, onOpen }) {
  return (
    <article className="research-row">

      <div className="paper-number">
        {number}
      </div>

      <div className={`paper-mark ${paper.color}`}>
        <BookOpen size={19} strokeWidth={1.6} />
        <span>{paper.tag}</span>
      </div>

      <div className="research-row-content">

        <div className="paper-meta">
          {paper.authors}
          <span>·</span>
          {paper.year}
        </div>

        <h3>{paper.title}</h3>

        <p>{paper.description}</p>

        <button className="text-link" onClick={onOpen}>
          Explore paper
          <ArrowUpRight size={13} />
        </button>

      </div>

      <button
        className="bookmark-button"
        aria-label={`Save ${paper.title}`}
        title="Save paper"
      >
        <Bookmark size={17} />
      </button>

    </article>
  )
}


function WorkflowStep({ number, icon: Icon, title, text }) {
  return (
    <div className="workflow-step">

      <span className="workflow-number">{number}</span>

      <div className="workflow-icon">
        <Icon size={17} />
      </div>

      <div>
        <strong>{title}</strong>
        <span>{text}</span>
      </div>

    </div>
  )
}


function Metric({ label, value, caption }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{caption}</small>
    </div>
  )
}

export default App