import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import LoadingScreen from "../components/LoadingScreen";
import ProtectedPage from "../components/ProtectedPage";

const REFRESH_SECONDS = 60;

function formatDateTime(value) {
  if (!value) return "Recently";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatCurrency(value) {
  if (value === null || value === undefined) return "Unavailable";
  return new Intl.NumberFormat("en", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: value >= 100 ? 0 : 4,
  }).format(value);
}

function sectionContentId(section) {
  if (section.content_id) return section.content_id;
  return section.items?.[0]?.content_id || null;
}

function ThumbIcon({ direction }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" focusable="false">
      <path
        d={
          direction === "up"
            ? "M7 10v10H4V10h3Zm4.2 10c-.9 0-1.6-.7-1.6-1.6V9.7l4.2-5.5c.4-.5 1.2-.2 1.2.5V9h4.1c1.1 0 1.9 1 1.6 2.1l-1.3 7.1c-.2 1-1 1.8-2.1 1.8h-6.1Z"
            : "M7 4v10H4V4h3Zm4.2 0h6.1c1.1 0 1.9.8 2.1 1.8l1.3 7.1c.3 1.1-.5 2.1-1.6 2.1H15v4.3c0 .7-.8 1-1.2.5L9.6 14.3V5.6c0-.9.7-1.6 1.6-1.6Z"
        }
      />
    </svg>
  );
}

function FeedbackControls({ section }) {
  const [selected, setSelected] = useState(null);
  const [status, setStatus] = useState("");
  const [isSending, setIsSending] = useState(false);

  async function vote(voteValue) {
    setIsSending(true);
    setStatus("");
    try {
      await api.sendFeedback({
        section_id: section.section_id,
        content_id: sectionContentId(section),
        vote: voteValue,
      });
      setSelected(voteValue);
      setStatus("Thanks for your feedback.");
    } catch (err) {
      setStatus(err.message);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="feedback-row">
      <button
        className={`icon-button ${selected === "thumbs_up" ? "selected" : ""}`}
        type="button"
        title="Helpful"
        aria-label="Vote thumbs up"
        disabled={isSending}
        onClick={() => vote("thumbs_up")}
      >
        <ThumbIcon direction="up" />
      </button>
      <button
        className={`icon-button ${selected === "thumbs_down" ? "selected" : ""}`}
        type="button"
        title="Not helpful"
        aria-label="Vote thumbs down"
        disabled={isSending}
        onClick={() => vote("thumbs_down")}
      >
        <ThumbIcon direction="down" />
      </button>
      {status ? <span className={`feedback-status ${status.startsWith("Thanks") ? "ok" : "error-text"}`}>{status}</span> : null}
    </div>
  );
}

function CardShell({ section, children, footer }) {
  return (
    <article className={`dashboard-card ${section.section_id}`}>
      <header className="card-header">
        <div>
          <h2>{section.title}</h2>
          <p className="source-line">{section.source?.replaceAll("_", " ") || "Dashboard source"}</p>
        </div>
        {section.is_fallback ? <span className="badge quiet">Curated</span> : null}
      </header>
      <div className="card-body">{children}</div>
      {footer}
      <FeedbackControls section={section} />
    </article>
  );
}

function MarketNewsCard({ section }) {
  const items = section.items || [];
  return (
    <CardShell section={section}>
      {items.length ? (
        <div className="news-list">
          {items.slice(0, 3).map((item) => (
            <a className="news-item" href={item.url || undefined} target="_blank" rel="noreferrer" key={item.content_id}>
              <span>{item.title}</span>
              <small>{item.source}{item.published_at ? ` · ${formatDateTime(item.published_at)}` : ""}</small>
              {item.summary ? <p>{item.summary}</p> : null}
            </a>
          ))}
        </div>
      ) : (
        <p className="empty-state">No market news is available right now.</p>
      )}
    </CardShell>
  );
}

function CoinPricesCard({ section }) {
  const items = section.items || [];
  return (
    <CardShell
      section={section}
      footer={<p className="updated-line">Updated at {formatDateTime(section.generated_at)}</p>}
    >
      {items.length ? (
        <div className="price-table">
          {items.map((item) => (
            <div className="price-row" key={item.content_id}>
              <div>
                <strong>{item.symbol}</strong>
                <span>{item.name}</span>
              </div>
              <div className="price-value">
                <strong>{formatCurrency(item.price_usd)}</strong>
                {item.change_24h_percent !== null && item.change_24h_percent !== undefined ? (
                  <span className={item.change_24h_percent >= 0 ? "positive" : "negative"}>
                    {item.change_24h_percent >= 0 ? "+" : ""}
                    {item.change_24h_percent.toFixed(2)}%
                  </span>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="empty-state">Price data is unavailable right now.</p>
      )}
    </CardShell>
  );
}

function AIInsightCard({ section }) {
  return (
    <CardShell section={section}>
      <p className="insight-text">{section.insight}</p>
      {section.disclaimer ? <p className="disclaimer">{section.disclaimer}</p> : null}
    </CardShell>
  );
}

function MemeCard({ section }) {
  return (
    <CardShell section={section}>
      <div className="meme-frame">
        {section.image_url ? (
          <img src={section.image_url} alt={section.alt_text || section.caption} />
        ) : (
          <div className="meme-placeholder">{section.caption}</div>
        )}
      </div>
      <p className="meme-caption">{section.caption}</p>
    </CardShell>
  );
}

function renderSection(section) {
  if (section.section_id === "market_news") return <MarketNewsCard section={section} key={section.section_id} />;
  if (section.section_id === "coin_prices") return <CoinPricesCard section={section} key={section.section_id} />;
  if (section.section_id === "ai_insight") return <AIInsightCard section={section} key={section.section_id} />;
  if (section.section_id === "crypto_meme") return <MemeCard section={section} key={section.section_id} />;
  return null;
}

function DashboardContent() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [secondsLeft, setSecondsLeft] = useState(REFRESH_SECONDS);

  const loadDashboard = useCallback(async ({ initial = false } = {}) => {
    if (initial) {
      setIsInitialLoading(true);
    } else {
      setIsRefreshing(true);
    }
    setError("");

    try {
      const preferences = await api.getPreferences();
      if (!preferences?.id) {
        navigate("/onboarding", { replace: true });
        return;
      }
      const data = await api.getDashboard();
      setDashboard(data);
      setSecondsLeft(REFRESH_SECONDS);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsInitialLoading(false);
      setIsRefreshing(false);
    }
  }, [navigate]);

  useEffect(() => {
    loadDashboard({ initial: true });
  }, [loadDashboard]);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setSecondsLeft((current) => {
        if (current <= 1) {
          loadDashboard();
          return REFRESH_SECONDS;
        }
        return current - 1;
      });
    }, 1000);

    return () => window.clearInterval(intervalId);
  }, [loadDashboard]);

  const sections = useMemo(() => {
    const byId = new Map((dashboard?.sections || []).map((section) => [section.section_id, section]));
    return ["market_news", "coin_prices", "ai_insight", "crypto_meme"]
      .map((sectionId) => byId.get(sectionId))
      .filter(Boolean);
  }, [dashboard]);

  if (isInitialLoading) {
    return <LoadingScreen label="Loading dashboard" />;
  }

  return (
    <main className="app-shell">
      <nav className="topbar">
        <div>
          <div className="brand-line">Crypto Investor Dashboard</div>
          <div className="subtle">{user?.name || user?.email}</div>
        </div>
        <div className="nav-actions">
          <button className="button secondary" type="button" onClick={() => navigate("/onboarding?mode=edit")}>
            Edit Preferences
          </button>
          <button className="button ghost" type="button" onClick={logout}>
            Logout
          </button>
        </div>
      </nav>

      <header className="dashboard-hero">
        <div>
          <p className="eyebrow">Today at a glance</p>
          <h1>Welcome{user?.name ? `, ${user.name}` : ""}</h1>
          <p>Your personalized daily crypto dashboard.</p>
        </div>
        <div className="refresh-panel">
          <button className="button primary" type="button" onClick={() => loadDashboard()} disabled={isRefreshing}>
            {isRefreshing ? "Refreshing..." : "Refresh now"}
          </button>
          <span>Next refresh in {secondsLeft}s</span>
        </div>
      </header>

      {error ? <div className="notice error dashboard-notice">{error}</div> : null}
      {isRefreshing ? <p className="refreshing-line">Refreshing dashboard data...</p> : null}

      <section className="dashboard-grid">{sections.map(renderSection)}</section>
    </main>
  );
}

export default function DashboardPage() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <ProtectedPage>
      <DashboardContent />
    </ProtectedPage>
  );
}
