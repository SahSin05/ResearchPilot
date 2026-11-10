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
  Layers3,
  Send,
  RefreshCw,
} from 'lucide-react'

import {
  checkBackend,
  getDocuments,
  uploadDocument,
  searchPapers,
  getPaperExplanation,
  chatWithDocument,
} from './services/api'


const navItems = [
  {
    label: 'Dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'Discover Papers',
    icon: Search,
  },
  {
    label: 'My Library',
    icon: FolderOpen,
  },
  {
    label: 'AI Assistant',
    icon: BrainCircuit,
  },
  {
    label: 'Evaluation Lab',
    icon: FlaskConical,
  },
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
    title:
      'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks',
    authors: 'Lewis et al.',
    year: '2020',
    description:
      'Combines a parametric language model with retrieved non-parametric knowledge to improve generation.',
    color: 'blue',
  },
  {
    tag: 'Evaluation',
    title:
      'Lost in the Middle: How Language Models Use Long Contexts',
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
  const [papers, setPapers] = useState([])
  const [searching, setSearching] = useState(false)

  const [uploadedDocuments, setUploadedDocuments] = useState([])
  const [loadingDocuments, setLoadingDocuments] = useState(true)

  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')

  const [selectedDocument, setSelectedDocument] = useState(null)

  const goTo = (page) => {
    setActive(page)

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }


  useEffect(() => {
    checkBackend()
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'))
  }, [])


  useEffect(() => {
    const loadDocuments = async () => {
      setLoadingDocuments(true)

      try {
        const data = await getDocuments()

        setUploadedDocuments(
          Array.isArray(data)
            ? data
            : data.documents || []
        )
      } catch (error) {
        console.error(
          'Failed to load documents:',
          error
        )
      } finally {
        setLoadingDocuments(false)
      }
    }

    loadDocuments()
  }, [])


  useEffect(() => {
    const trimmedQuery = query.trim()

    if (!trimmedQuery) {
      setPapers([])
      setSearching(false)
      return
    }

    const controller = new AbortController()

    const timer = setTimeout(async () => {
      setSearching(true)

      try {
        const data = await searchPapers(
          trimmedQuery,
          {
            signal: controller.signal,
          }
        )

        setPapers(data.papers || [])
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error(
            'Paper search failed:',
            error
          )

          setPapers([])
        }
      } finally {
        if (!controller.signal.aborted) {
          setSearching(false)
        }
      }
    }, 700)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [query])


  const handleDocumentUpload = async (file) => {
    if (!file) {
      return
    }

    setUploading(true)
    setUploadError('')

    try {
      const document =
        await uploadDocument(file)

      setUploadedDocuments(
        (current) => [
          document,
          ...current,
        ]
      )

      setSelectedDocument(document)

      goTo('AI Assistant')
    } catch (error) {
      console.error(
        'Document upload failed:',
        error
      )

      setUploadError(
        error.message ||
          'Document upload failed'
      )
    } finally {
      setUploading(false)
    }
  }


  const handleSelectDocument = (
    document
  ) => {
    setSelectedDocument(document)
  }


  return (
    <div className="app-shell">

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-mark">
            <BrainCircuit
              size={21}
              strokeWidth={1.7}
            />
          </div>

          <div>
            <strong>
              ResearchPilot
            </strong>

            <span>
              RESEARCH INTELLIGENCE
            </span>
          </div>

        </div>


        <button className="workspace-switch">

          <div className="workspace-avatar">
            R
          </div>

          <div className="workspace-copy">

            <strong>
              Research workspace
            </strong>

            <span>
              Personal plan
            </span>

          </div>

          <ChevronDown size={15} />

        </button>


        <div className="nav-label">
          WORKSPACE
        </div>


        <nav className="nav-list">

          {navItems.map(
            ({
              label,
              icon: Icon,
            }) => (

              <button
                key={label}
                className={`nav-item ${
                  active === label
                    ? 'active'
                    : ''
                }`}
                onClick={() =>
                  goTo(label)
                }
              >

                <Icon
                  size={18}
                  strokeWidth={1.7}
                />

                <span>
                  {label}
                </span>

                {label ===
                  'Evaluation Lab' && (
                  <span className="nav-badge">
                    LAB
                  </span>
                )}

              </button>

            )
          )}

        </nav>


        <div className="sidebar-bottom">

          <div className="privacy-note">

            <ShieldCheck size={16} />

            <div>

              <strong>
                Private by design
              </strong>

              <span>
                Your research workspace is isolated
                and access-controlled.
              </span>

            </div>

          </div>


          <button className="nav-item">

            <Settings2 size={18} />

            <span>
              Settings
            </span>

          </button>


          <button className="nav-item">

            <CircleHelp size={18} />

            <span>
              Help & documentation
            </span>

          </button>


          <div className="profile">

            <div className="profile-avatar">
              SS
            </div>

            <div className="profile-copy">

              <strong>
                Researcher
              </strong>

              <span>
                Personal workspace
              </span>

            </div>

            <button
              className="icon-button"
              aria-label="Profile settings"
            >

              <Settings2 size={16} />

            </button>

          </div>

        </div>

      </aside>


      <main className="main-area">

        <header className="topbar">

          <div className="breadcrumb">

            <span>
              ResearchPilot
            </span>

            <span className="slash">
              /
            </span>

            <strong>
              {active}
            </strong>

          </div>


          <div className="topbar-right">

            <div
              className={`connection ${
                apiStatus
              }`}
            >

              {apiStatus ===
              'online' ? (
                <Wifi size={14} />
              ) : apiStatus ===
                'offline' ? (
                <WifiOff size={14} />
              ) : (
                <Activity size={14} />
              )}

              <span>

                {apiStatus ===
                'online'
                  ? 'System online'
                  : apiStatus ===
                    'offline'
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

          {active ===
          'Dashboard' ? (

            <Dashboard
              apiStatus={apiStatus}
              query={query}
              setQuery={setQuery}
              goTo={goTo}
            />

          ) : active ===
            'Discover Papers' ? (

            <DiscoverPage
              query={query}
              setQuery={setQuery}
              papers={papers}
              searching={searching}
              goTo={goTo}
            />

          ) : active ===
            'My Library' ? (

            <LibraryPage
              onUpload={
                handleDocumentUpload
              }
              uploading={uploading}
              uploadError={
                uploadError
              }
              documents={
                uploadedDocuments
              }
              loadingDocuments={
                loadingDocuments
              }
              selectedDocument={
                selectedDocument
              }
              onSelectDocument={
                handleSelectDocument
              }
              onOpenAssistant={() =>
                goTo(
                  'AI Assistant'
                )
              }
            />

          ) : active ===
            'AI Assistant' ? (

            <AssistantPage
              selectedDocument={
                selectedDocument
              }
              onSelectDocument={
                handleSelectDocument
              }
              documents={
                uploadedDocuments
              }
              goTo={goTo}
            />

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

function Dashboard({
  apiStatus,
  query,
  setQuery,
  goTo,
}) {

  return (
    <section className="research-dashboard">

      <div className="dashboard-intro">

        <div>

          <div className="eyebrow">

            <Sparkles size={13} />

            RESEARCH INTELLIGENCE

          </div>


          <h1>
            What are
            <br />
            <em>
              investigating?
            </em>
          </h1>


          <p>
            Search the literature, interrogate your
            papers, and build knowledge with an AI
            research companion.
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
          onChange={(e) =>
            setQuery(
              e.target.value
            )
          }
          onKeyDown={(e) => {
            if (
              e.key ===
              'Enter'
            ) {
              goTo(
                'Discover Papers'
              )
            }
          }}
          placeholder="Search papers, authors, concepts, or research topics..."
        />


        <button
          className="command-submit"
          onClick={() =>
            goTo(
              'Discover Papers'
            )
          }
          aria-label="Search research"
        >

          <ArrowUpRight size={19} />

        </button>


        <div className="command-footer">

          <span>
            Try searching for
          </span>

          {topics
            .slice(0, 3)
            .map(
              (topic) => (

                <button
                  key={topic}
                  onClick={() => {
                    setQuery(
                      topic
                    )

                    goTo(
                      'Discover Papers'
                    )
                  }}
                >
                  {topic}
                </button>

              )
            )}

        </div>

      </div>


      <div className="dashboard-grid">

        <section className="research-feed">

          <div className="section-heading">

            <div>

              <span className="section-kicker">
                LITERATURE
              </span>

              <h2>
                Recent discoveries
              </h2>

            </div>


            <button
              className="subtle-button"
              onClick={() =>
                goTo(
                  'Discover Papers'
                )
              }
            >

              View library

              <ArrowUpRight size={14} />

            </button>

          </div>


          <div className="paper-feed">

            {demoPapers.map(
              (
                paper,
                index
              ) => (

                <ResearchRow
                  key={
                    paper.title
                  }
                  paper={paper}
                  number={String(
                    index + 1
                  ).padStart(
                    2,
                    '0'
                  )}
                  onOpen={() =>
                    goTo(
                      'Discover Papers'
                    )
                  }
                />

              )
            )}

          </div>

        </section>


        <aside className="research-pulse">

          <div className="pulse-header">

            <div>

              <span className="section-kicker">
                WORKSPACE
              </span>

              <h2>
                Research pulse
              </h2>

            </div>

            <Activity size={18} />

          </div>


          <div className="pulse-main">

            <strong>
              03
            </strong>

            <span>
              preview papers
              <br />
              in your workspace
            </span>

          </div>


          <div className="pulse-divider" />


          <div className="pulse-stat">

            <span>
              Topics explored
            </span>

            <strong>
              05
            </strong>

          </div>


          <div className="pulse-stat">

            <span>
              AI readiness
            </span>

            <strong className="teal-text">

              {apiStatus ===
              'online'
                ? 'READY'
                : 'WAITING'}

            </strong>

          </div>


          <div className="pulse-topics">

            {topics.map(
              (topic) => (
                <span key={topic}>
                  {topic}
                </span>
              )
            )}

          </div>


          <button
            className="pulse-action"
            onClick={() =>
              goTo(
                'AI Assistant'
              )
            }
          >

            <BrainCircuit size={17} />

            Open research assistant

            <ArrowUpRight size={15} />

          </button>

        </aside>

      </div>


      <section className="workflow-strip">

        <div className="workflow-title">

          <span className="section-kicker">
            WORKFLOW
          </span>

          <strong>
            Your research loop
          </strong>

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

function DiscoverPage({
  query,
  setQuery,
  papers,
  searching,
  goTo,
}) {

  return (
    <section className="research-discover">

      <div className="discover-header">

        <div>

          <div className="eyebrow">

            <Search size={13} />

            LITERATURE DISCOVERY

          </div>


          <h1>
            Discover research.
          </h1>


          <p>
            Explore academic literature by topic,
            title, author, or idea.
          </p>

        </div>


        <div className="result-count">

          <strong>
            {papers.length}
          </strong>

          <span>
            results
          </span>

        </div>

      </div>


      <div className="large-search">

        <Search size={20} />

        <input
          value={query}
          onChange={(e) =>
            setQuery(
              e.target.value
            )
          }
          placeholder="Search papers, authors, concepts..."
          autoFocus
        />

        <span>
          ENTER
        </span>

      </div>


      <div className="topic-row">

        <span>
          EXPLORE TOPICS
        </span>

        {topics.map(
          (topic) => (

            <button
              key={topic}
              onClick={() =>
                setQuery(
                  topic
                )
              }
            >
              {topic}
            </button>

          )
        )}

      </div>


      <div className="discover-list">

        <div className="list-heading">

          <span>
            DISCOVERIES
          </span>

          <span>
            YEAR
          </span>

        </div>


        {papers.map(
          (
            paper,
            index
          ) => (

            <ResearchRow
              key={
                paper.id ||
                paper.openalex_id ||
                paper.title
              }
              paper={{
                ...paper,
                tag: 'Research',
                authors:
                  Array.isArray(
                    paper.authors
                  )
                    ? paper.authors.join(
                        ', '
                      )
                    : paper.authors ||
                      'Unknown authors',
                year:
                  paper.publication_year ||
                  'N/A',
                description:
                  paper.abstract ||
                  'No abstract available for this paper.',
                color: 'blue',
              }}
              number={String(
                index + 1
              ).padStart(
                2,
                '0'
              )}
              onOpen={() =>
                goTo(
                  'My Library'
                )
              }
            />

          )
        )}


        {searching && (

          <div className="empty-state">

            <Search size={22} />

            <strong>
              Searching research literature…
            </strong>

            <span>
              Querying OpenAlex for relevant papers.
            </span>

          </div>

        )}


        {!searching &&
          query.trim() &&
          papers.length === 0 && (

            <div className="empty-state">

              <Search size={22} />

              <strong>
                No matching papers
              </strong>

              <span>
                Try another topic or keyword.
              </span>

            </div>

          )}

      </div>


      <div className="demo-disclaimer">

        <CheckCircle2 size={14} />

        Live literature search powered by
        OpenAlex.

      </div>

    </section>
  )
}


/* =========================================================
   LIBRARY
   ========================================================= */

function LibraryPage({
  onUpload,
  uploading,
  uploadError,
  documents,
  loadingDocuments,
  selectedDocument,
  onSelectDocument,
  onOpenAssistant,
}) {

  return (
    <section className="simple-page">

      <div className="eyebrow">

        <FolderOpen size={13} />

        YOUR KNOWLEDGE BASE

      </div>


      <h1>
        My library.
      </h1>


      <p className="subheading">
        Build a private research collection and turn
        documents into searchable knowledge.
      </p>


      <div className="library-layout">

        <div className="upload-panel">

          <div className="upload-icon">

            <UploadCloud size={28} />

          </div>


          <span className="section-kicker">
            DOCUMENT INGESTION
          </span>


          <h2>
            Bring a paper into ResearchPilot.
          </h2>


          <p>
            Upload a research document and the
            ingestion pipeline will prepare it for
            grounded AI conversations.
          </p>


          <label
            className={`primary-button ${
              uploading
                ? 'uploading'
                : ''
            }`}
          >

            <UploadCloud size={16} />

            {uploading
              ? 'Uploading…'
              : 'Upload document'}


            <input
              type="file"
              accept=".pdf,.docx,.txt"
              hidden
              disabled={uploading}
              onChange={(e) => {

                const file =
                  e.target.files?.[0]

                if (file) {
                  onUpload(file)
                }

                e.target.value = ''

              }}
            />

          </label>


          <small>
            Supported formats: PDF, DOCX and TXT.
          </small>


          {uploadError && (

            <div className="upload-error">
              {uploadError}
            </div>

          )}

        </div>


        <div className="library-empty">

          {loadingDocuments ? (

            <>

              <Activity size={28} />

              <span className="section-kicker">
                YOUR COLLECTION
              </span>

              <strong>
                Loading documents…
              </strong>

              <p>
                Loading your research collection.
              </p>

            </>

          ) : documents.length === 0 ? (

            <>

              <Layers3 size={28} />

              <span className="section-kicker">
                YOUR COLLECTION
              </span>

              <strong>
                No documents yet.
              </strong>

              <p>
                Your uploaded papers, extracted
                metadata, and indexed chunks will
                appear here.
              </p>

            </>

          ) : (

            <>

              <span className="section-kicker">
                YOUR COLLECTION
              </span>


              <strong>

                {documents.length}

                {' '}

                document
                {documents.length !== 1
                  ? 's'
                  : ''}

              </strong>


              <div className="document-list">

                {documents.map(
                  (document) => {

                    const isSelected =
                      selectedDocument?.id ===
                      document.id

                    return (

                      <button
                        type="button"
                        className={`document-item ${
                          isSelected
                            ? 'selected'
                            : ''
                        }`}
                        key={
                          document.id
                        }
                        onClick={() => {
                          onSelectDocument(
                            document
                          )

                          onOpenAssistant()
                        }}
                      >

                        <FileText
                          size={20}
                        />


                        <div>

                          <strong>
                            {
                              document.filename
                            }
                          </strong>


                          <span>

                            {
                              document.file_type
                            }

                            {' · '}

                            {
                              document.page_count ??
                              1
                            }

                            {' '}

                            page
                            {document.page_count !==
                            1
                              ? 's'
                              : ''}

                            {' · '}

                            {
                              document.processing_status ||
                              'unknown'
                            }

                          </span>

                        </div>

                        <ArrowUpRight
                          size={15}
                        />

                      </button>

                    )
                  }
                )}

              </div>


              {selectedDocument && (

                <div className="library-selection">

                  <strong>
                    Selected paper
                  </strong>

                  <span>
                    {
                      selectedDocument.filename
                    }
                  </span>

                  <button
                    className="subtle-button"
                    onClick={
                      onOpenAssistant
                    }
                  >
                    Open AI Assistant
                    <ArrowUpRight
                      size={14}
                    />
                  </button>

                </div>

              )}

            </>

          )}

        </div>

      </div>

    </section>
  )
}


/* =========================================================
   AI ASSISTANT
   ========================================================= */

function AssistantPage({
  selectedDocument,
  onSelectDocument,
  documents,
  goTo,
}) {

  const [activeTab, setActiveTab] =
    useState('explanation')

  const [explanation, setExplanation] =
    useState(null)

  const [loadingExplanation, setLoadingExplanation] =
    useState(false)

  const [explanationError, setExplanationError] =
    useState('')

  const [question, setQuestion] =
    useState('')

  const [messages, setMessages] =
    useState([])

  const [sending, setSending] =
    useState(false)

  const [chatError, setChatError] =
    useState('')


  useEffect(() => {
    setExplanation(null)
    setExplanationError('')
    setMessages([])
    setQuestion('')

    if (!selectedDocument) {
      return
    }

    loadExplanation(
      selectedDocument.id
    )
  }, [selectedDocument])


  const loadExplanation = async (
    documentId
  ) => {
    setLoadingExplanation(true)
    setExplanationError('')

    try {
      const data =
        await getPaperExplanation(
          documentId
        )

      setExplanation(data)
    } catch (error) {
      console.error(
        'Failed to load paper explanation:',
        error
      )

      setExplanationError(
        error.message ||
          'Failed to generate paper explanation'
      )
    } finally {
      setLoadingExplanation(false)
    }
  }


  const sendQuestion = async (
    questionOverride
  ) => {

    const text =
      (
        questionOverride ??
        question
      ).trim()

    if (
      !text ||
      !selectedDocument ||
      sending
    ) {
      return
    }

    setChatError('')

    setMessages(
      (current) => [
        ...current,
        {
          id:
            `${Date.now()}-user`,
          role: 'user',
          content: text,
        },
      ]
    )

    setQuestion('')
    setSending(true)

    try {

      const response =
        await chatWithDocument(
          selectedDocument.id,
          text
        )

      setMessages(
        (current) => [
          ...current,
          {
            id:
              `${Date.now()}-assistant`,
            role: 'assistant',
            content:
              response.answer,
            sources:
              response.sources ||
              [],
          },
        ]
      )

      setActiveTab('chat')

    } catch (error) {

      console.error(
        'Chat request failed:',
        error
      )

      setChatError(
        error.message ||
          'Failed to get an answer'
      )

    } finally {
      setSending(false)
    }
  }


  if (!selectedDocument) {

    return (
      <section className="assistant-workspace">

        <div className="assistant-header">

          <div>

            <div className="eyebrow">

              <BrainCircuit size={13} />

              PAPER-GROUNDED INTELLIGENCE

            </div>

            <h1>
              Ask your research.
            </h1>

            <p>
              A grounded AI workspace for understanding
              papers, methods, findings, and limitations.
            </p>

          </div>

        </div>


        <div className="assistant-shell">

          <div className="assistant-orb">

            <BrainCircuit
              size={42}
              strokeWidth={1.2}
            />

          </div>


          <span className="section-kicker">
            RESEARCHPILOT AI
          </span>


          <h2>
            Select a paper to begin.
          </h2>


          <p>
            Choose an uploaded research paper from
            your library before asking questions.
          </p>


          {documents.length === 0 ? (

            <button
              className="primary-button"
              onClick={() =>
                goTo(
                  'My Library'
                )
              }
            >

              <FolderOpen
                size={16}
              />

              Open My Library

              <ArrowUpRight
                size={15}
              />

            </button>

          ) : (

            <div className="assistant-document-picker">

              {documents.map(
                (document) => (

                  <button
                    type="button"
                    className="document-item"
                    key={
                      document.id
                    }
                    onClick={() =>
                      onSelectDocument(
                        document
                      )
                    }
                  >

                    <FileText
                      size={20}
                    />

                    <div>

                      <strong>
                        {
                          document.filename
                        }
                      </strong>

                      <span>
                        {
                          document.processing_status ||
                          'unknown'
                        }
                      </span>

                    </div>

                    <ArrowUpRight
                      size={15}
                    />

                  </button>

                )
              )}

            </div>

          )}

        </div>

      </section>
    )
  }


  return (
    <section className="assistant-workspace">

      <div className="assistant-header">

        <div>

          <div className="eyebrow">

            <BrainCircuit size={13} />

            PAPER-GROUNDED INTELLIGENCE

          </div>


          <h1>
            {selectedDocument.filename}
          </h1>


          <p>
            ResearchPilot is grounding its answers in
            the indexed evidence from this paper.
          </p>

        </div>


        <div className="assistant-document-status">

          <CheckCircle2 size={15} />

          {selectedDocument.processing_status ===
          'completed'
            ? 'Indexed and ready'
            : selectedDocument.processing_status ||
              'Processing'}

        </div>

      </div>


      <div className="assistant-tabs">

        <button
          className={
            activeTab ===
            'explanation'
              ? 'active'
              : ''
          }
          onClick={() =>
            setActiveTab(
              'explanation'
            )
          }
        >
          Paper explanation
        </button>

        <button
          className={
            activeTab ===
            'chat'
              ? 'active'
              : ''
          }
          onClick={() =>
            setActiveTab(
              'chat'
            )
          }
        >
          Ask questions
        </button>

      </div>


      {activeTab ===
      'explanation' ? (

        <ExplanationView
          explanation={
            explanation
          }
          loading={
            loadingExplanation
          }
          error={
            explanationError
          }
          onRetry={() =>
            loadExplanation(
              selectedDocument.id
            )
          }
          onAsk={(prompt) => {
            setActiveTab(
              'chat'
            )

            sendQuestion(prompt)
          }}
        />

      ) : (

        <ChatView
          messages={messages}
          question={question}
          setQuestion={setQuestion}
          sending={sending}
          error={chatError}
          onSend={() =>
            sendQuestion()
          }
          onSuggestion={
            (prompt) =>
              sendQuestion(prompt)
          }
        />

      )}

    </section>
  )
}


/* =========================================================
   EXPLANATION
   ========================================================= */

function ExplanationView({
  explanation,
  loading,
  error,
  onRetry,
  onAsk,
}) {

  if (loading) {

    return (
      <div className="assistant-shell">

        <RefreshCw
          className="spin"
          size={28}
        />

        <span className="section-kicker">
          ANALYZING PAPER
        </span>

        <h2>
          Building your paper explanation…
        </h2>

        <p>
          ResearchPilot is retrieving relevant evidence
          and generating a structured explanation.
        </p>

      </div>
    )
  }


  if (error) {

    return (
      <div className="assistant-shell">

        <BrainCircuit size={28} />

        <span className="section-kicker">
          EXPLANATION ERROR
        </span>

        <h2>
          We couldn't generate the explanation.
        </h2>

        <p>
          {error}
        </p>

        <button
          className="primary-button"
          onClick={onRetry}
        >

          <RefreshCw size={16} />

          Try again

        </button>

      </div>
    )
  }


  if (!explanation) {
    return null
  }


  const sections = [
    {
      key: 'problem',
      title: 'Research problem',
    },
    {
      key: 'key_concepts',
      title: 'Key concepts',
    },
    {
      key: 'methodology',
      title: 'Methodology',
    },
    {
      key: 'dataset',
      title: 'Dataset',
    },
    {
      key: 'results',
      title: 'Results',
    },
    {
      key: 'limitations',
      title: 'Limitations',
    },
  ]


  return (
    <div className="paper-explanation">

      <div className="explanation-intro">

        <span className="section-kicker">
          PAPER INTELLIGENCE
        </span>

        <h2>
          Understand the paper at a glance.
        </h2>

        <p>
          This explanation was generated from retrieved
          evidence in the selected paper. Citation labels
          identify the evidence used by the RAG pipeline.
        </p>

      </div>


      <div className="explanation-grid">

        {sections.map(
          (section) => {

            const data =
              explanation[
                section.key
              ]

            if (!data) {
              return null
            }

            return (

              <article
                className="explanation-card"
                key={
                  section.key
                }
              >

                <div className="explanation-card-header">

                  <span>
                    {section.title}
                  </span>

                  <BookOpen
                    size={16}
                  />

                </div>


                <p>
                  {data.content}
                </p>


                {data.citations?.length >
                  0 && (

                  <div className="citation-row">

                    {data.citations.map(
                      (citation) => (

                        <span
                          key={
                            citation
                          }
                        >
                          {citation}
                        </span>

                      )
                    )}

                  </div>

                )}

              </article>

            )
          }
        )}

      </div>


      {explanation.glossary?.length >
        0 && (

        <section className="glossary-section">

          <div className="section-heading">

            <div>

              <span className="section-kicker">
                GLOSSARY
              </span>

              <h2>
                Key terms
              </h2>

            </div>

          </div>


          <div className="glossary-grid">

            {explanation.glossary.map(
              (entry) => (

                <article
                  className="glossary-card"
                  key={
                    entry.term
                  }
                >

                  <strong>
                    {entry.term}
                  </strong>

                  <p>
                    {entry.definition}
                  </p>


                  {entry.citations?.length >
                    0 && (

                    <div className="citation-row">

                      {entry.citations.map(
                        (citation) => (

                          <span
                            key={
                              citation
                            }
                          >
                            {citation}
                          </span>

                        )
                      )}

                    </div>

                  )}

                </article>

              )
            )}

          </div>

        </section>

      )}


      <div className="explanation-actions">

        <button
          className="primary-button"
          onClick={() =>
            onAsk(
              'Explain the main contribution of this paper.'
            )
          }
        >

          <BrainCircuit size={16} />

          Ask about this paper

          <ArrowUpRight
            size={15}
          />

        </button>

      </div>

    </div>
  )
}


/* =========================================================
   CHAT
   ========================================================= */

function ChatView({
  messages,
  question,
  setQuestion,
  sending,
  error,
  onSend,
  onSuggestion,
}) {

  const suggestions = [
    'Explain the main contribution.',
    'What are the limitations?',
    'Explain the methodology.',
  ]


  return (
    <div className="chat-workspace">

      {messages.length === 0 ? (

        <div className="chat-empty">

          <div className="assistant-orb">

            <BrainCircuit
              size={38}
              strokeWidth={1.2}
            />

          </div>

          <span className="section-kicker">
            RESEARCHPILOT AI
          </span>

          <h2>
            Ask a question about the paper.
          </h2>

          <p>
            Your question will be answered using retrieved
            evidence from the selected document.
          </p>


          <div className="suggestion-row">

            {suggestions.map(
              (suggestion) => (

                <button
                  key={
                    suggestion
                  }
                  onClick={() =>
                    onSuggestion(
                      suggestion
                    )
                  }
                >
                  {suggestion}
                </button>

              )
            )}

          </div>

        </div>

      ) : (

        <div className="chat-messages">

          {messages.map(
            (message) => (

              <article
                className={`chat-message ${
                  message.role
                }`}
                key={
                  message.id
                }
              >

                <div className="chat-message-role">

                  {message.role ===
                  'user'
                    ? 'YOU'
                    : 'RESEARCHPILOT'}

                </div>


                <div className="chat-message-content">

                  {message.content}

                </div>


                {message.sources?.length >
                  0 && (

                  <div className="chat-sources">

                    <span className="section-kicker">
                      SOURCES
                    </span>

                    <div className="source-list">

                      {message.sources.map(
                        (source) => (

                          <div
                            className="source-item"
                            key={
                              source.citation_id
                            }
                          >

                            <strong>
                              {
                                source.label ||
                                `[C${source.citation_id}]`
                              }
                            </strong>

                            <span>

                              {source.page_number
                                ? `Page ${source.page_number}`
                                : 'Document evidence'}

                              {source.section
                                ? ` · ${source.section}`
                                : ''}

                              {source.subsection
                                ? ` · ${source.subsection}`
                                : ''}

                            </span>

                          </div>

                        )
                      )}

                    </div>

                  </div>

                )}

              </article>

            )
          )}

          {sending && (

            <article className="chat-message assistant">

              <div className="chat-message-role">
                RESEARCHPILOT
              </div>

              <div className="chat-message-content">

                <Activity
                  className="spin"
                  size={18}
                />

                Retrieving evidence and generating an
                answer…

              </div>

            </article>

          )}

        </div>

      )}


      {error && (

        <div className="upload-error">
          {error}
        </div>

      )}


      <div className="chat-input">

        <textarea
          value={question}
          onChange={(e) =>
            setQuestion(
              e.target.value
            )
          }
          onKeyDown={(e) => {

            if (
              e.key ===
              'Enter' &&
              !e.shiftKey
            ) {

              e.preventDefault()

              onSend()
            }

          }}
          placeholder="Ask a question about this paper…"
          rows={3}
          disabled={sending}
        />

        <button
          className="command-submit"
          onClick={onSend}
          disabled={
            sending ||
            !question.trim()
          }
          aria-label="Send question"
        >

          <Send size={18} />

        </button>

      </div>


      <small className="chat-disclaimer">
        Answers are grounded in retrieved evidence from
        the selected paper. If the evidence is insufficient,
        ResearchPilot may say so instead of inventing an answer.
      </small>

    </div>
  )
}


/* =========================================================
   EVALUATION
   ========================================================= */

function EvaluationPage() {

  return (
    <section className="simple-page">

      <div className="eyebrow">

        <FlaskConical size={13} />

        QUALITY & RELIABILITY

      </div>


      <h1>
        Evaluation lab.
      </h1>


      <p className="subheading">
        Measure whether ResearchPilot answers
        accurately, retrieves the right evidence, and
        supports its claims.
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

        <span className="section-kicker">
          NO BENCHMARK RUNS
        </span>


        <strong>
          Your evaluation workspace is ready.
        </strong>


        <p>
          Benchmarking will populate this area once
          the RAG pipeline evaluation suite is connected.
        </p>

      </div>

    </section>
  )
}


/* =========================================================
   COMPONENTS
   ========================================================= */

function ResearchRow({
  paper,
  number,
  onOpen,
}) {

  return (
    <article className="research-row">

      <div className="paper-number">
        {number}
      </div>


      <div
        className={`paper-mark ${
          paper.color
        }`}
      >

        <BookOpen
          size={19}
          strokeWidth={1.6}
        />

        <span>
          {paper.tag}
        </span>

      </div>


      <div className="research-row-content">

        <div className="paper-meta">

          {paper.authors}

          <span>
            ·
          </span>

          {paper.year}

        </div>


        <h3>
          {paper.title}
        </h3>


        <p>
          {paper.description}
        </p>


        <button
          className="text-link"
          onClick={onOpen}
        >

          Explore paper

          <ArrowUpRight
            size={13}
          />

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


function WorkflowStep({
  number,
  icon: Icon,
  title,
  text,
}) {

  return (
    <div className="workflow-step">

      <span className="workflow-number">
        {number}
      </span>


      <div className="workflow-icon">

        <Icon size={17} />

      </div>


      <div>

        <strong>
          {title}
        </strong>

        <span>
          {text}
        </span>

      </div>

    </div>
  )
}


function Metric({
  label,
  value,
  caption,
}) {

  return (
    <div className="metric-card">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

      <small>
        {caption}
      </small>

    </div>
  )
}


export default App