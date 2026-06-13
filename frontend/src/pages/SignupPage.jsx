import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import AuthLayout from "../components/AuthLayout";

export default function SignupPage() {
  const navigate = useNavigate();
  const { isAuthenticated, login } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRedirectingToOnboarding, setIsRedirectingToOnboarding] = useState(false);

  if (isAuthenticated && !isSubmitting && !isRedirectingToOnboarding) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await api.register(form);
      try {
        await login({ email: form.email, password: form.password });
        setIsRedirectingToOnboarding(true);
        navigate("/onboarding", { replace: true, state: { skipPreferenceLoad: true } });
      } catch {
        setError("Account created, but automatic login failed. Please go to login and sign in manually.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthLayout
      eyebrow="Get started"
      title="Create your account"
      subtitle="Sign up, then complete a short onboarding flow."
    >
      {error ? <div className="notice error">{error}</div> : null}
      <form className="form-stack" onSubmit={handleSubmit}>
        <label>
          Name
          <input
            type="text"
            autoComplete="name"
            value={form.name}
            onChange={(event) => setForm({ ...form, name: event.target.value })}
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            autoComplete="email"
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            autoComplete="new-password"
            minLength={8}
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
            required
          />
        </label>
        <button className="button primary wide" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>
      </form>
      <p className="auth-link">
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </AuthLayout>
  );
}
