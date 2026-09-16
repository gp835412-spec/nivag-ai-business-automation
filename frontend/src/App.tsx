import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import {
  apiRequest,
  createLead,
  getAccessToken,
  getLead,
  getLeads,
  saveAccessToken,
  updateLead,
} from './services/api'
import type { Lead } from './services/api'
import './App.css'

const capabilities = [
  'AI Automation',
  'Business Intelligence',
  'Workflow Systems',
  'CRM & Operations',
  'AI Assistants',
  'Custom Platforms',
]

const services = [
  {
    number: '01',
    title: 'AI Business Automation',
    description:
      'Intelligent workflows that connect business processes, data, decisions, and execution.',
    visual: 'automation',
  },
  {
    number: '02',
    title: 'AI Systems & Agents',
    description:
      'Purpose-built AI systems designed to assist teams, automate repetitive work, and improve operational speed.',
    visual: 'ai',
  },
  {
    number: '03',
    title: 'Custom Software',
    description:
      'Modern software products engineered around real business requirements instead of generic templates.',
    visual: 'software',
  },
]

function App() {
  const isCrmPage = window.location.pathname === '/crm'

  const [crmEmail, setCrmEmail] = useState('')
  const [crmPassword, setCrmPassword] = useState('')
  const [crmMessage, setCrmMessage] = useState('')
  const [crmAuthenticated, setCrmAuthenticated] = useState(
    Boolean(getAccessToken()),
  )
  const [crmLeads, setCrmLeads] = useState<Lead[]>([])
  const [crmLeadsTotal, setCrmLeadsTotal] = useState(0)
  const [crmLeadsLoading, setCrmLeadsLoading] = useState(false)
  const [crmLeadsMessage, setCrmLeadsMessage] = useState('')
  const [crmLeadView, setCrmLeadView] = useState<'pipeline' | 'table'>('pipeline')

  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [leadDetailsLoading, setLeadDetailsLoading] = useState(false)
  const [leadDetailsMessage, setLeadDetailsMessage] = useState('')

  const [isAddLeadOpen, setIsAddLeadOpen] = useState(false)
  const [leadSubmitting, setLeadSubmitting] = useState(false)
  const [leadFormMessage, setLeadFormMessage] = useState('')

const [leadForm, setLeadForm] = useState({
  title: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  company_name: '',
  job_title: '',
  source: '',
  status: 'new',
  estimated_value: '',
  currency: 'INR',
  description: '',
})

  const loadCrmLeads = async () => {
    const accessToken = getAccessToken()

    if (!accessToken) {
      setCrmAuthenticated(false)
      setCrmLeads([])
      setCrmLeadsTotal(0)
      return
    }

    setCrmLeadsLoading(true)
    setCrmLeadsMessage('')

    try {
      const response = await getLeads(accessToken, 100, 0)
      setCrmLeads(response.items)
      setCrmLeadsTotal(response.total)
    } catch (error) {
    const message =
    error instanceof Error
      ? error.message
      : 'Unable to load CRM leads.'

  setCrmLeads([])
  setCrmLeadsTotal(0)

  if (
  error instanceof Error &&
  'status' in error &&
  error.status === 401
) {
  handleCrmLogout()
  setCrmMessage('Your CRM session has expired. Please sign in again.')
  return
}

  setCrmLeadsMessage(message)
} finally {
  setCrmLeadsLoading(false)
}
 }
  const handleLeadStatusChange = async (
  leadId: string,
  status: string,
) => {
  const accessToken = getAccessToken()

  if (!accessToken) {
    setCrmAuthenticated(false)
    return
  }

  try {
    await updateLead(accessToken, leadId, { status })
    await loadCrmLeads()
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : 'Unable to update lead status.'

    setCrmLeadsMessage(message)
  }
}

const handleLeadDetails = async (leadId: string) => {
  const accessToken = getAccessToken()

  if (!accessToken) {
    setCrmAuthenticated(false)
    return
  }

  setLeadDetailsLoading(true)
  setLeadDetailsMessage('')

  try {
    const lead = await getLead(accessToken, leadId)
    setSelectedLead(lead)
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : 'Unable to load lead details.'

    if (
      error instanceof Error &&
      'status' in error &&
      error.status === 401
    ) {
      handleCrmLogout()
      setCrmMessage('Your CRM session has expired. Please sign in again.')
      return
    }

    setLeadDetailsMessage(message)
  } finally {
    setLeadDetailsLoading(false)
  }
}

  useEffect(() => {
    if (isCrmPage && crmAuthenticated) {
      void loadCrmLeads()
    }
  }, [isCrmPage, crmAuthenticated])


  const pipelineStages = [
    { key: 'new', label: 'New' },
    { key: 'contacted', label: 'Contacted' },
    { key: 'qualified', label: 'Qualified' },
    { key: 'proposal', label: 'Proposal' },
    { key: 'negotiation', label: 'Negotiation' },
    { key: 'won', label: 'Won' },
    { key: 'lost', label: 'Lost' },
  ] as const

  const handleCreateLead = async (event: FormEvent<HTMLFormElement>) => {
  event.preventDefault()

  const accessToken = getAccessToken()

  if (!accessToken) {
    setCrmAuthenticated(false)
    return
  }

  if (!leadForm.title.trim()) {
    setLeadFormMessage('Lead title is required.')
    return
  }

  setLeadSubmitting(true)
  setLeadFormMessage('')

  try {
    await createLead(accessToken, {
      title: leadForm.title.trim(),
      first_name: leadForm.first_name.trim() || undefined,
      last_name: leadForm.last_name.trim() || undefined,
      email: leadForm.email.trim() || undefined,
      phone: leadForm.phone.trim() || undefined,
      company_name: leadForm.company_name.trim() || undefined,
      job_title: leadForm.job_title.trim() || undefined,
      source: leadForm.source.trim() || 'CRM',
      status: leadForm.status,
      estimated_value: leadForm.estimated_value.trim() || undefined,
      currency: leadForm.currency,
      description: leadForm.description.trim() || undefined,
    })

    setLeadForm({
      title: '',
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      company_name: '',
      job_title: '',
      source: '',
      status: 'new',
      estimated_value: '',
      currency: 'INR',
      description: '',
    })

    setIsAddLeadOpen(false)
    await loadCrmLeads()
  } catch (error) {
    setLeadFormMessage(
      error instanceof Error
        ? error.message
        : 'Unable to create lead.',
    )
  } finally {
    setLeadSubmitting(false)
  }
}


  const handleCrmLogin = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    setCrmMessage('')

    try {
      const response = await apiRequest<{
        access_token: string
        token_type: string
        user: {
          id: string
          organization_id: string
          email: string
          first_name: string
          last_name: string | null
          phone: string | null
          role: string
          status: string
          is_email_verified: boolean
        }
      }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          organization_slug: 'nivag',
          email: crmEmail.trim(),
          password: crmPassword,
        }),
      })

      saveAccessToken(response.access_token)
      setCrmAuthenticated(true)
      setCrmPassword('')
      setCrmMessage('CRM login successful.')
    } catch (error) {
      setCrmAuthenticated(false)
      setCrmMessage(
        error instanceof Error
          ? error.message
          : 'CRM login failed.',
      )
    }
  }

  const handleCrmLogout = () => {
    localStorage.removeItem('nivag_access_token')
    setCrmAuthenticated(false)
    setCrmEmail('')
    setCrmPassword('')
    setCrmMessage('')
    setCrmLeads([])
    setCrmLeadsTotal(0)
    setCrmLeadsMessage('')
    setIsAddLeadOpen(false)
    setSelectedLead(null)
    setLeadDetailsMessage('')
    setLeadDetailsLoading(false)
  }


  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<
    'idle' | 'success' | 'error'
  >('idle')
  const [submitMessage, setSubmitMessage] = useState('')

  const handleInquirySubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    setIsSubmitting(true)
    setSubmitStatus('idle')
    setSubmitMessage('')

    const form = event.currentTarget
    const formData = new FormData(form)

    const payload = {
      first_name: String(formData.get('first_name') ?? '').trim(),
      last_name: String(formData.get('last_name') ?? '').trim(),
      email: String(formData.get('email') ?? '').trim(),
      phone: String(formData.get('phone') ?? '').trim(),
      company_name: String(formData.get('company_name') ?? '').trim(),
      job_title: String(formData.get('job_title') ?? '').trim(),
      title: String(formData.get('title') ?? '').trim(),
      description: String(formData.get('description') ?? '').trim(),
      source: 'NIVAG Portfolio',
    }

    try {
      await apiRequest('/public/inquiries', {
        method: 'POST',
        body: JSON.stringify(payload),
      })

      setSubmitStatus('success')
      setSubmitMessage(
        'Thank you. Your inquiry has been received. We will get back to you soon.',
      )
      form.reset()
          } catch (error) {
      setSubmitStatus('error')
      setSubmitMessage(
        error instanceof Error
          ? error.message
          : 'Something went wrong. Please try again.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isCrmPage) {
    return (
      <div className="crm-page">
        <div className="crm-page-shell">
          <div className="crm-page-header">
            <p className="eyebrow">NIVAG BUSINESS AUTOMATION</p>
            <h1>NIVAG CRM</h1>
            <p>
              Manage leads, customer relationships and business
              operations.
            </p>
          </div>

          {crmAuthenticated ? (
            <section className="crm-dashboard" aria-label="CRM leads">
             <div className="crm-dashboard-header">
  <div>
    <p className="eyebrow">LEADS</p>
    <h2>Lead pipeline</h2>
    <p>Manage real leads received through NIVAG business inquiries.</p>
  </div>

  <div className="crm-dashboard-actions">
    <button
      type="button"
      className="crm-add-lead-button"
      onClick={() => {
        setLeadFormMessage('')
        setIsAddLeadOpen(true)
      }}
    >
      + Add Lead
    </button>

    <button
      type="button"
      className="crm-refresh-button"
      onClick={() => void loadCrmLeads()}
      disabled={crmLeadsLoading}
    >
      {crmLeadsLoading ? 'Refreshing…' : 'Refresh'}
    </button>

    <button
      type="button"
      className="crm-logout-button"
      onClick={handleCrmLogout}
    >
      Logout
    </button>
  </div>
  </div>

              {crmLeadsMessage && (
                <div className="crm-leads-error" role="alert">
                  {crmLeadsMessage}
                </div>
              )}

              <div className="crm-view-switcher" role="tablist" aria-label="Lead views">
  <button
    type="button"
    className={`crm-view-tab ${
      crmLeadView === 'pipeline' ? 'crm-view-tab-active' : ''
    }`}
    onClick={() => setCrmLeadView('pipeline')}
    role="tab"
    aria-selected={crmLeadView === 'pipeline'}
  >
    Pipeline
  </button>

  <button
    type="button"
    className={`crm-view-tab ${
      crmLeadView === 'table' ? 'crm-view-tab-active' : ''
    }`}
    onClick={() => setCrmLeadView('table')}
    role="tab"
    aria-selected={crmLeadView === 'table'}
  >
    Table
  </button>
</div>


   {crmLeadsLoading && crmLeads.length === 0 ? (
  <div className="crm-leads-state">Loading leads…</div>
) : crmLeads.length === 0 ? (
  <div className="crm-leads-state">No leads found.</div>
) : crmLeadView === 'pipeline' ? (
  <div className="crm-pipeline">
    {pipelineStages.map((stage) => {
      const stageLeads = crmLeads.filter(
        (lead) => lead.status === stage.key,
      )

      return (
        <div className="crm-pipeline-column" key={stage.key}>
          <div className="crm-pipeline-column-header">
            <div>
              <span>{stage.label}</span>
              <small>{stageLeads.length}</small>
            </div>
          </div>

          <div className="crm-pipeline-cards">
            {stageLeads.length === 0 ? (
              <div className="crm-pipeline-empty">
                No leads
              </div>
            ) : (
              stageLeads.map((lead) => {
                const name = [lead.first_name, lead.last_name]
                  .filter(Boolean)
                  .join(' ')

                return (
                  <article
                    className="crm-pipeline-card"
                    key={lead.id}
                    onClick={() => void handleLeadDetails(lead.id)}
                  >
                    <div className="crm-pipeline-card-top">
  <select
    className="crm-pipeline-status-select"
    value={lead.status}
    onClick={(event) => event.stopPropagation()}
    onChange={(event) =>
      handleLeadStatusChange(
        lead.id,
        event.target.value,
      )
    }
    aria-label={`Change status for ${lead.title}`}
  >
    {pipelineStages.map((stage) => (
      <option
        key={stage.key}
        value={stage.key}
      >
        {stage.label}
      </option>
    ))}
  </select>

  <span className="crm-pipeline-date">
    {new Date(
      lead.created_at,
    ).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    })}
  </span>
</div>

                    <h3>{lead.title}</h3>

                    {name && (
                      <p className="crm-pipeline-contact">
                        {name}
                      </p>
                    )}

                    {lead.company_name && (
                      <p>{lead.company_name}</p>
                    )}

                    {lead.email && (
                      <p>{lead.email}</p>
                    )}

                    {lead.phone && (
                      <p>{lead.phone}</p>
                    )}

                    {lead.source && (
                      <span className="crm-pipeline-source">
                        {lead.source}
                      </span>
                    )}
                  </article>
                )
              })
            )}
          </div>
        </div>
      )
    })}
  </div>
) : (
  <div className="crm-table-wrap">
    <table className="crm-leads-table">
      <thead>
        <tr>
          <th>Title</th>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Company</th>
          <th>Source</th>
          <th>Status</th>
          <th>Created</th>
        </tr>
      </thead>

      <tbody>
        {crmLeads.map((lead) => {
          const name = [lead.first_name, lead.last_name]
            .filter(Boolean)
            .join(' ')

          return (
            <tr key={lead.id}>
              <td className="crm-lead-title">
                {lead.title}
              </td>
              <td>{name || '—'}</td>
              <td>{lead.email || '—'}</td>
              <td>{lead.phone || '—'}</td>
              <td>{lead.company_name || '—'}</td>
              <td>{lead.source || '—'}</td>
              <td>
                <span className="crm-status-badge">
                  {lead.status}
                </span>
              </td>
              <td>
                {new Date(
                  lead.created_at,
                ).toLocaleDateString(undefined, {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                })}
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  </div>
)}
              <div className="crm-dashboard-footer">
                <span>{crmLeadsTotal} total lead{crmLeadsTotal === 1 ? '' : 's'}</span>
              </div>

              {isAddLeadOpen && (
  <div className="crm-modal-backdrop">
    <div
      className="crm-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="add-lead-title"
    >
      <div className="crm-modal-header">
        <div>
          <p className="eyebrow">CRM</p>
          <h3 id="add-lead-title">Add Lead</h3>
          <p>Create a new lead in the NIVAG CRM.</p>
        </div>

        <button
          type="button"
          className="crm-modal-close"
          onClick={() => {
            if (!leadSubmitting) {
              setIsAddLeadOpen(false)
              setLeadFormMessage('')
            }
          }}
          disabled={leadSubmitting}
          aria-label="Close add lead form"
        >
          ×
        </button>
      </div>

      <form className="crm-lead-form" onSubmit={handleCreateLead}>
        <div className="crm-form-grid">
          <label>
            Lead title *
            <input
              type="text"
              value={leadForm.title}
              onChange={(event) =>
                setLeadForm((current) => ({
                  ...current,
                  title: event.target.value,
                }))
              }
              placeholder="e.g. CRM implementation inquiry"
              required
            />
          </label>

          <label>
            Company
            <input
              type="text"
              value={leadForm.company_name}
              onChange={(event) =>
                setLeadForm((current) => ({
                  ...current,
                  company_name: event.target.value,
                }))
              }
              placeholder="Company name"
            />
          </label>

          <label>
            First name
            <input
              type="text"
              value={leadForm.first_name}
              onChange={(event) =>
                setLeadForm((current) => ({
                  ...current,
                  first_name: event.target.value,
                }))
              }
              placeholder="First name"
            />
          </label>

          <label>
            Last name
            <input
              type="text"
              value={leadForm.last_name}
              onChange={(event) =>
                setLeadForm((current) => ({
                  ...current,
                  last_name: event.target.value,
                }))
              }
              placeholder="Last name"
            />
          </label>

          <label>
            Email
            <input
              type="email"
              value={leadForm.email}
              onChange={(event) =>
                setLeadForm((current) => ({
                  ...current,
                  email: event.target.value,
                }))
              }
              placeholder="name@company.com"
            />
          </label>

          <label>
            Phone
            <input
              type="tel"
              value={leadForm.phone}
              onChange={(event) =>
                setLeadForm((current) => ({
                  ...current,
                  phone: event.target.value,
                }))
              }
              placeholder="+91..."
            />
          </label>

          <label>
            Job title
            <input
              type="text"
              value={leadForm.job_title}
              onChange={(event) =>
                setLeadForm((current) => ({
                  ...current,
                  job_title: event.target.value,
                }))
              }
              placeholder="Decision maker / role"
            />
          </label>

          <label>
            Source
            <input
              type="text"
              value={leadForm.source}
              onChange={(event) =>
                setLeadForm((current) => ({
                  ...current,
                  source: event.target.value,
                }))
              }
              placeholder="Website, referral, CRM..."
            />
          </label>

          <label>
            Status
            <select
              value={leadForm.status}
              onChange={(event) =>
                setLeadForm((current) => ({
                  ...current,
                  status: event.target.value,
                }))
              }
            >
              <option value="new">New</option>
              <option value="contacted">Contacted</option>
              <option value="qualified">Qualified</option>
              <option value="proposal">Proposal</option>
              <option value="negotiation">Negotiation</option>
              <option value="won">Won</option>
              <option value="lost">Lost</option>
            </select>
          </label>

          <label>
            Estimated value (INR)
            <input
              type="number"
              min="0"
              step="0.01"
              value={leadForm.estimated_value}
              onChange={(event) =>
                setLeadForm((current) => ({
                  ...current,
                  estimated_value: event.target.value,
                }))
              }
              placeholder="0"
            />
          </label>
        </div>

        <label>
          Description
          <textarea
            value={leadForm.description}
            onChange={(event) =>
              setLeadForm((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="Add useful context about this lead..."
            rows={4}
          />
        </label>

        {leadFormMessage && (
          <p className="crm-form-message" role="alert">
            {leadFormMessage}
          </p>
        )}

        <div className="crm-modal-actions">
          <button
            type="button"
            className="crm-modal-cancel"
            onClick={() => {
              if (!leadSubmitting) {
                setIsAddLeadOpen(false)
                setLeadFormMessage('')
              }
            }}
            disabled={leadSubmitting}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="crm-add-lead-button"
            disabled={leadSubmitting}
          >
            {leadSubmitting ? 'Creating…' : 'Create Lead'}
          </button>
        </div>
      </form>
    </div>
  </div>
)}

              {selectedLead && (
                <div className="crm-modal-backdrop">
                  <div
                    className="crm-modal crm-lead-details-modal"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="lead-details-title"
                  >
                    <div className="crm-modal-header">
                      <div>
                        <p className="eyebrow">LEAD DETAILS</p>
                        <h3 id="lead-details-title">
                          {selectedLead.title}
                        </h3>
                        <p>
                          {leadDetailsLoading
                            ? 'Loading lead details…'
                            : 'Complete CRM lead information.'}
                        </p>
                      </div>

                      <button
                        type="button"
                        className="crm-modal-close"
                        onClick={() => {
                          setSelectedLead(null)
                          setLeadDetailsMessage('')
                        }}
                        aria-label="Close lead details"
                      >
                        ×
                      </button>
                    </div>

                    {leadDetailsMessage ? (
                      <p className="crm-form-message" role="alert">
                        {leadDetailsMessage}
                      </p>
                    ) : (
                      <div className="crm-lead-details-grid">
                        <div>
                          <span>Status</span>
                          <strong>{selectedLead.status}</strong>
                        </div>

                        <div>
                          <span>Source</span>
                          <strong>{selectedLead.source || '—'}</strong>
                        </div>

                        <div>
                          <span>First name</span>
                          <strong>{selectedLead.first_name || '—'}</strong>
                        </div>

                        <div>
                          <span>Last name</span>
                          <strong>{selectedLead.last_name || '—'}</strong>
                        </div>

                        <div>
                          <span>Email</span>
                          <strong>{selectedLead.email || '—'}</strong>
                        </div>

                        <div>
                          <span>Phone</span>
                          <strong>{selectedLead.phone || '—'}</strong>
                        </div>

                        <div>
                          <span>Company</span>
                          <strong>{selectedLead.company_name || '—'}</strong>
                        </div>

                        <div>
                          <span>Job title</span>
                          <strong>{selectedLead.job_title || '—'}</strong>
                        </div>

                        <div>
                          <span>Estimated value</span>
                          <strong>
                            {selectedLead.estimated_value
                              ? `${selectedLead.currency} ${selectedLead.estimated_value}`
                              : '—'}
                          </strong>
                        </div>

                        <div>
                          <span>Created</span>
                          <strong>
                            {new Date(
                              selectedLead.created_at,
                            ).toLocaleString()}
                          </strong>
                        </div>

                        <div>
                          <span>Updated</span>
                          <strong>
                            {new Date(
                              selectedLead.updated_at,
                            ).toLocaleString()}
                          </strong>
                        </div>

                        <div className="crm-lead-details-description">
                          <span>Description</span>
                          <p>
                            {selectedLead.description ||
                              'No description provided.'}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </section>
          ) : (
            <form
              className="crm-login-form"
              onSubmit={handleCrmLogin}
            >
              <input
                type="email"
                value={crmEmail}
                onChange={(event) =>
                  setCrmEmail(event.target.value)
                }
                placeholder="CRM email"
                autoComplete="email"
                required
              />

              <input
                type="password"
                value={crmPassword}
                onChange={(event) =>
                  setCrmPassword(event.target.value)
                }
                placeholder="CRM password"
                autoComplete="current-password"
                required
              />

              <button type="submit">
                Sign in
              </button>

              {crmMessage && (
                <p className="crm-login-message">
                  {crmMessage}
                </p>
              )}
            </form>
          )}
        </div>
      </div>
    )
  }


  return (
    <div className="site">
      {/* ================= HEADER ================= */}

      <header className="header">
        <a href="#top" className="logo" aria-label="NIVAG home">
          <span className="logo-box">N</span>
          <span className="logo-text">NIVAG</span>
        </a>

        <nav className="navigation" aria-label="Main navigation">
          <a href="#services">Services</a>
          <a href="#solutions">Solutions</a>
          <a href="#work">Work</a>
          <a href="#about">About</a>
          <a href="/crm">CRM</a>
        </nav>

        <a
          href="mailto:nivagoffical@gmail.com"
          className="header-cta"
        >
          <span>Start a Conversation</span>
          <span>→</span>
        </a>
      </header>

      <main id="top">
        {/* ================= HERO ================= */}

        <section className="hero">
          <div className="hero-content">
            <p className="eyebrow">
              AI • AUTOMATION • SOFTWARE
            </p>

            <h1 className="hero-title">
              Build smarter.
              <br />
              <span>Operate faster.</span>
            </h1>

            <p className="hero-description">
              NIVAG builds intelligent business systems that turn
              complex processes into clear, scalable digital
              operations.
            </p>

            <div className="hero-buttons">
              <a
                href="mailto:nivagoffical@gmail.com"
                className="button button-primary"
              >
                <span>Discuss your project</span>
                <span>→</span>
              </a>

              <a href="#work" className="button button-secondary">
                Explore NIVAG
              </a>
            </div>

            <div className="hero-features">
              <div className="hero-feature">
                <span className="feature-icon">▣</span>

                <div>
                  <strong>AI-First</strong>
                  <small>Technology approach</small>
                </div>
              </div>

              <div className="hero-feature">
                <span className="feature-icon">ϑ</span>

                <div>
                  <strong>Built for Business</strong>
                  <small>Practical automation</small>
                </div>
              </div>

              <div className="hero-feature">
                <span className="feature-icon">◇</span>

                <div>
                  <strong>Secure by Design</strong>
                  <small>Enterprise grade security</small>
                </div>
              </div>
            </div>
          </div>

          {/* IMPORTANT:
              Real photographic hero asset will be placed here.
              No CSS-generated humans.
          */}

          <div className="hero-visual">
            <div className="hero-photo">

              <div className="hero-product-label">
                NIVAG AI business automation
              </div>

              <div className="hero-overlay" />

              <div className="ai-interface">
                <div className="ai-core">
                  <span>N</span>
                </div>

                <div className="ai-label ai-label-left-top">
                  <strong>DATA</strong>
                  <span>INTELLIGENCE</span>
                </div>

                <div className="ai-label ai-label-left-middle">
                  <strong>PROCESS</strong>
                  <span>AUTOMATION</span>
                </div>

                <div className="ai-label ai-label-left-bottom">
                  <strong>PREDICTIVE</strong>
                  <span>ANALYTICS</span>
                </div>

                <div className="ai-label ai-label-right-top">
                  <strong>WORKFLOW</strong>
                  <span>SYSTEMS</span>
                </div>

                <div className="ai-label ai-label-right-middle">
                  <strong>AI AGENTS</strong>
                  <span>& ASSISTANTS</span>
                </div>

                <div className="ai-label ai-label-right-bottom">
                  <strong>BUSINESS</strong>
                  <span>GROWTH</span>
                </div>

                <div className="ai-title">
                  <strong>NIVAG AI</strong>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ================= CAPABILITY / METRICS ================= */}

        <section className="capability-section">
          <div className="capabilities">
            {capabilities.map((item) => (
              <div className="capability" key={item}>
                <span className="capability-dot" />
                <span>{item}</span>
              </div>
            ))}
          </div>

          <div className="metrics">
            <div className="metric">
              <strong>50+</strong>
              <span>Projects Delivered</span>
            </div>

            <div className="metric">
              <strong>99.9%</strong>
              <span>Uptime & Reliability</span>
            </div>

            <div className="metric">
              <strong>24/7</strong>
              <span>Support</span>
            </div>
          </div>
        </section>

        {/* ================= SERVICES ================= */}

        <section
          className="services-section"
          id="services"
        >
          <div className="section-heading centered">
            <p className="eyebrow">WHAT WE BUILD</p>

            <h2>
              Technology that{' '}
              <span>works for the business.</span>
            </h2>
          </div>

          <div className="service-grid">
            {services.map((service) => (
              <article
                className={`service-card service-${service.visual}`}
                key={service.number}
              >
                <div className="service-content">
                  <span className="service-number">
                    {service.number}
                  </span>

                  <h3>{service.title}</h3>

                  <p>{service.description}</p>

                  <span className="service-arrow">→</span>
                </div>

                <div
                  className="service-visual"
                  aria-hidden="true"
                >
                  {service.visual === 'automation' && (
                    <div className="automation-visual">
                      <div className="cube cube-main" />
                      <div className="cube cube-one" />
                      <div className="cube cube-two" />
                      <div className="cube cube-three" />
                      <div className="connection connection-one" />
                      <div className="connection connection-two" />
                      <div className="connection connection-three" />
                    </div>
                  )}

                  {service.visual === 'ai' && (
                    <div className="ai-chip-visual">
                      <div className="chip-core">AI</div>
                      <span className="chip-line line-1" />
                      <span className="chip-line line-2" />
                      <span className="chip-line line-3" />
                      <span className="chip-line line-4" />
                    </div>
                  )}

                  {service.visual === 'software' && (
                    <div className="software-visual">
                      <div className="software-window">
                        <div className="window-bar">
                          <i />
                          <i />
                          <i />
                        </div>

                        <div className="window-content">
                          <div className="window-sidebar" />

                          <div className="window-dashboard">
                            <span />
                            <span />
                            <span />
                            <span />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </article>
            ))}
          </div>
        </section>

        {/* ================= SOLUTIONS ================= */}

        <section
          className="solutions-section"
          id="solutions"
        >
          <div className="solutions-copy">
            <p className="eyebrow">INTELLIGENT OPERATIONS</p>

            <h2>
              One intelligent layer
              <br />
              <span>across your business.</span>
            </h2>

            <p>
              NIVAG connects people, processes, software and AI
              into a unified operating layer designed around the
              way your business actually works.
            </p>
          </div>

          <div className="solutions-diagram">
            <div className="diagram-node node-top">
              AI
            </div>

            <div className="diagram-node node-left">
              DATA
            </div>

            <div className="diagram-node node-right">
              CRM
            </div>

            <div className="diagram-node node-bottom">
              WORKFLOW
            </div>

            <div className="diagram-core">
              <span>N</span>
              <small>NIVAG AI</small>
            </div>
          </div>
        </section>

        {/* ================= WORK ================= */}

        <section
          className="work-section"
          id="work"
        >
          <div className="work-header">
            <div>
              <p className="eyebrow">FEATURED WORK</p>

              <h2>
                NIVAG AI
                <br />
                <span>Business Automation</span>
              </h2>
            </div>

            <p>
              A modular automation platform designed to connect
              business operations with intelligent event-driven
              workflows.
            </p>
          </div>

          <div className="work-platform">
            <div className="platform-sidebar">
              <strong>NIVAG AI</strong>

              <span>Dashboard</span>
              <span>Automation</span>
              <span>CRM</span>
              <span>Agents</span>
              <span>Analytics</span>
            </div>

            <div className="platform-main">
              <div className="platform-top">
                <span>Business Intelligence</span>
                <span>AI Automation</span>
              </div>

              <div className="dashboard-grid">
                <div className="dashboard-card large">
                  <small>Automation Activity</small>
                  <div className="chart">
                    <i />
                    <i />
                    <i />
                    <i />
                    <i />
                    <i />
                  </div>
                </div>

                <div className="dashboard-card">
                  <small>AI Operations</small>
                  <strong>94.8%</strong>
                  <span>Efficiency</span>
                </div>

                <div className="dashboard-card">
                  <small>Active Workflows</small>
                  <strong>128</strong>
                  <span>Running</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ================= ABOUT ================= */}

        <section
          className="about-section"
          id="about"
        >
          <div>
            <p className="eyebrow">ABOUT NIVAG</p>

            <h2>
              Technology built
              <br />
              <span>around real work.</span>
            </h2>
          </div>

          <div className="about-content">
            <p>
              NIVAG is an independent technology initiative focused
              on practical AI, automation and custom software
              solutions for modern businesses.
            </p>

            <p>
              We build systems around real operational requirements,
              with an emphasis on reliability, scalability,
              maintainability and measurable business value.
            </p>

            <div className="about-statements">
              <span>AI-first engineering</span>
              <span>Business process automation</span>
              <span>Scalable architecture</span>
              <span>Secure systems</span>
              <span>Custom software</span>
              <span>Long-term maintainability</span>
            </div>
          </div>
        </section>


        {/* ================= TECHNOLOGY STACK ================= */}

        <section className="technology-section" id="technology">
          <div className="technology-heading">
            <div>
              <p className="eyebrow">TECHNOLOGY STACK</p>

              <h2>
                Modern tools.
                <br />
                <span>Enterprise architecture.</span>
              </h2>
            </div>

            <p>
              NIVAG uses modern, production-ready technologies to
              build reliable AI systems, automation platforms and
              custom software.
            </p>
          </div>

          <div className="technology-grid">
            <article className="technology-card">
              <span className="technology-label">FRONTEND</span>
              <strong>React 19</strong>
              <span>TypeScript • Vite</span>
            </article>

            <article className="technology-card">
              <span className="technology-label">BACKEND</span>
              <strong>FastAPI</strong>
              <span>Python</span>
            </article>

            <article className="technology-card">
              <span className="technology-label">DATABASE</span>
              <strong>PostgreSQL</strong>
              <span>Redis</span>
            </article>

            <article className="technology-card">
              <span className="technology-label">AI / ML</span>
              <strong>OpenAI</strong>
              <span>LangChain</span>
            </article>

            <article className="technology-card">
              <span className="technology-label">MOBILE</span>
              <strong>Flutter</strong>
              <span>Cross-platform</span>
            </article>

            <article className="technology-card">
              <span className="technology-label">DEVOPS</span>
              <strong>Docker</strong>
              <span>GitHub Actions • AWS</span>
            </article>
          </div>
        </section>


        {/* ================= WHY CHOOSE NIVAG ================= */}

        <section className="why-section" id="why-nivag">
          <div className="why-heading">
           <div>
            <p className="eyebrow">WHY CHOOSE NIVAG?</p>

              <h2>
              Built for
              <br />
        <span>real business impact.</span>
      </h2>
    </div>

    <p>
      We combine AI-first engineering, practical automation and
      scalable software architecture to build systems that create
      measurable long-term value.
    </p>
  </div>

  <div className="why-grid">
    <article className="why-card">
      <div className="why-number">01</div>
      <h3>AI-First Engineering</h3>
      <p>
        AI is designed into the system where it creates genuine
        operational value.
      </p>
    </article>

    <article className="why-card">
      <div className="why-number">02</div>
      <h3>Scalable Architecture</h3>
      <p>
        Modular architecture designed to evolve with your business
        and future requirements.
      </p>
    </article>

    <article className="why-card">
      <div className="why-number">03</div>
      <h3>Business Process Automation</h3>
      <p>
        We automate repetitive workflows so teams can focus on
        higher-value work.
      </p>
    </article>

    <article className="why-card">
      <div className="why-number">04</div>
      <h3>Secure Systems</h3>
      <p>
        Security and reliability are considered throughout the
        architecture and implementation.
      </p>
    </article>

    <article className="why-card">
      <div className="why-number">05</div>
      <h3>Custom Software</h3>
      <p>
        Solutions are engineered around actual requirements rather
        than forcing the business into generic templates.
      </p>
    </article>

    <article className="why-card">
      <div className="why-number">06</div>
      <h3>Long-Term Maintainability</h3>
      <p>
        Clean, documented and maintainable systems built for
        continued improvement.
      </p>
    </article>
  </div>
</section>


      {/* ================= ENGAGEMENT MODELS ================= */}

<section className="engagement-section" id="engagement">
  <div className="engagement-heading">
    <div>
      <p className="eyebrow">ENGAGEMENT MODELS</p>

      <h2>
        Work the way
        <br />
        <span>your business needs.</span>
      </h2>
    </div>

    <p>
      Flexible engagement models designed around project scope,
      delivery requirements and long-term business needs.
    </p>
  </div>

  <div className="engagement-grid">
    <article className="engagement-card">
      <span className="engagement-number">01</span>
      <h3>Fixed Price Projects</h3>
      <p>
        Clear scope, timeline and cost for well-defined software
        and automation projects.
      </p>
      <span className="engagement-meta">Defined scope • Milestone delivery</span>
    </article>

    <article className="engagement-card">
      <span className="engagement-number">02</span>
      <h3>Hourly Basis</h3>
      <p>
        Flexible engineering support for evolving requirements,
        improvements and ongoing development.
      </p>
      <span className="engagement-meta">Flexible hours • On-demand work</span>
    </article>

    <article className="engagement-card">
      <span className="engagement-number">03</span>
      <h3>Monthly Retainer</h3>
      <p>
        Dedicated engineering capacity for continuous development,
        maintenance and operational improvements.
      </p>
      <span className="engagement-meta">Recurring support • Priority work</span>
    </article>

    <article className="engagement-card">
      <span className="engagement-number">04</span>
      <h3>Dedicated Team</h3>
      <p>
        A focused team working as an extension of your organization
        for long-term product development.
      </p>
      <span className="engagement-meta">Dedicated capacity • Long-term delivery</span>
    </article>
  </div>
</section>

        {/* ================= FINAL CTA / CONTACT ================= */}

        <section className="contact-section" id="contact">
          <div className="contact-content">
            <p className="eyebrow">LET'S BUILD</p>

            <h2>
              Have a business
              <br />
              <span>problem to solve?</span>
            </h2>

            <p className="contact-description">
              Tell us what you are trying to improve, automate, or
              build. NIVAG turns real business requirements into
              practical AI, automation and software solutions.
            </p>

            <div className="contact-actions">
              <form className="contact-form" onSubmit={handleInquirySubmit}>
                <div className="contact-form-row">
                 <input
                  type="text"
        name="first_name"
        placeholder="First name"
        required
        autoComplete="given-name"
      />

      <input
        type="text"
        name="last_name"
        placeholder="Last name"
        autoComplete="family-name"
      />
    </div>

    <div className="contact-form-row">
      <input
        type="email"
        name="email"
        placeholder="Work email"
        required
        autoComplete="email"
      />

      <input
        type="tel"
        name="phone"
        placeholder="Phone"
        autoComplete="tel"
      />
    </div>

    <div className="contact-form-row">
      <input
        type="text"
        name="company_name"
        placeholder="Company"
        autoComplete="organization"
      />

      <input
        type="text"
        name="job_title"
        placeholder="Your role"
        autoComplete="organization-title"
      />
    </div>

    <input
      type="text"
      name="title"
      placeholder="What would you like to build or improve?"
      required
    />

    <textarea
      name="description"
      placeholder="Tell us briefly about your requirement..."
      rows={5}
    />

    <button
      type="submit"
      className="contact-button"
      disabled={isSubmitting}
    >
      <span>
        {isSubmitting ? 'Sending...' : 'Send inquiry'}
      </span>
      <span>↗</span>
    </button>

    {submitStatus !== 'idle' && (
      <p
        className={
          submitStatus === 'success'
            ? 'contact-form-message success'
            : 'contact-form-message error'
        }
        role="status"
      >
        {submitMessage}
      </p>
    )}
  </form>

  <span className="contact-email">
    nivagoffical@gmail.com
  </span>
</div>
            <div className="contact-trust">
              <span>
                <i />
                AI • Automation • Software
              </span>

              <span>Independent Technology Initiative</span>
            </div>
          </div>
        </section>
      </main>

      {/* ================= FOOTER ================= */}

      <footer className="footer">
        <a href="#top" className="logo">
          <span className="logo-box">N</span>
          <span className="logo-text">NIVAG</span>
        </a>

        <span>AI • Automation • Software</span>

        <span>© 2026 NIVAG</span>
      </footer>
    </div>
  )
}

export default App
