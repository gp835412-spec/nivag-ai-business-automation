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
                <span className="feature-icon">ϟ</span>

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
              <a
                href="mailto:nivagoffical@gmail.com"
                className="contact-button"
              >
                <span>Start a conversation</span>
                <span>↗</span>
              </a>

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