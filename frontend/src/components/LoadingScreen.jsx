export default function LoadingScreen({ label = "Loading" }) {
  return (
    <main className="screen-center">
      <div className="loader-card">
        <span className="spinner" aria-hidden="true" />
        <p>{label}</p>
      </div>
    </main>
  );
}
