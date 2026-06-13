export default function AuthLayout({ children, eyebrow, title, subtitle }) {
  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <div className="brand-mark">CID</div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="muted">{subtitle}</p>
        {children}
      </section>
      <aside className="auth-aside">
        <div>
          <p className="eyebrow">Personalized</p>
          <h2>Daily crypto context without the noise.</h2>
          <p>
            Track selected assets, read concise updates, get one educational insight,
            and keep the tone useful with feedback.
          </p>
        </div>
      </aside>
    </main>
  );
}
