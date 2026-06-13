import { useEffect, useMemo, useState } from "react";
import { Navigate, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import LoadingScreen from "../components/LoadingScreen";
import ProtectedPage from "../components/ProtectedPage";

const ASSETS = ["Bitcoin", "Ethereum", "Solana", "Cardano"];
const INVESTOR_TYPES = ["HODLer", "Day Trader", "NFT Collector"];
const CONTENT_TYPES = ["Market News", "Charts", "Social", "Fun"];

function toggleItem(values, item) {
  return values.includes(item) ? values.filter((value) => value !== item) : [...values, item];
}

function ChipGroup({ options, selected, onToggle, single = false }) {
  return (
    <div className="chip-grid">
      {options.map((option) => {
        const isSelected = single ? selected === option : selected.includes(option);
        return (
          <button
            className={`chip ${isSelected ? "selected" : ""}`}
            key={option}
            type="button"
            onClick={() => onToggle(option)}
          >
            {option}
          </button>
        );
      })}
    </div>
  );
}

function OnboardingContent() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { user, logout } = useAuth();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    crypto_assets: [],
    investor_type: "",
    content_preferences: [],
  });
  const isEditing = searchParams.get("mode") === "edit";
  const shouldSkipPreferenceLoad = location.state?.skipPreferenceLoad === true && !isEditing;

  useEffect(() => {
    let isMounted = true;

    if (shouldSkipPreferenceLoad) {
      setIsLoading(false);
      return () => {
        isMounted = false;
      };
    }

    async function loadPreferences() {
      try {
        const preferences = await api.getPreferences();
        if (!isMounted) return;
        if (preferences?.id) {
          setForm({
            crypto_assets: (preferences.crypto_assets || []).filter((asset) => ASSETS.includes(asset)),
            investor_type: preferences.investor_type || "",
            content_preferences: preferences.content_preferences || [],
          });
        }
      } catch (err) {
        if (isMounted) setError(err.message);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    loadPreferences();
    return () => {
      isMounted = false;
    };
  }, [shouldSkipPreferenceLoad]);

  const canContinue = useMemo(() => {
    if (step === 1) return form.crypto_assets.length > 0;
    if (step === 2) return Boolean(form.investor_type);
    return form.content_preferences.length > 0;
  }, [form, step]);

  if (isLoading) {
    return <LoadingScreen label="Loading preferences" />;
  }

  async function handleSave() {
    setError("");
    setIsSaving(true);
    try {
      await api.savePreferences(form);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSaving(false);
    }
  }

  function renderStep() {
    if (step === 1) {
      return (
        <>
          <p className="eyebrow">Step 1 of 3</p>
          <h1>Select crypto assets</h1>
          <p className="muted">Choose the coins you want your dashboard to follow.</p>
          <ChipGroup
            options={ASSETS}
            selected={form.crypto_assets}
            onToggle={(asset) =>
              setForm({ ...form, crypto_assets: toggleItem(form.crypto_assets, asset) })
            }
          />
        </>
      );
    }

    if (step === 2) {
      return (
        <>
          <p className="eyebrow">Step 2 of 3</p>
          <h1>Select investor type</h1>
          <p className="muted">This helps tune the tone of your daily context.</p>
          <ChipGroup
            options={INVESTOR_TYPES}
            selected={form.investor_type}
            single
            onToggle={(investorType) => setForm({ ...form, investor_type: investorType })}
          />
        </>
      );
    }

    return (
      <>
        <p className="eyebrow">Step 3 of 3</p>
        <h1>Select content preferences</h1>
        <p className="muted">Pick the formats you want to see most often.</p>
        <ChipGroup
          options={CONTENT_TYPES}
          selected={form.content_preferences}
          onToggle={(contentType) =>
            setForm({
              ...form,
              content_preferences: toggleItem(form.content_preferences, contentType),
            })
          }
        />
      </>
    );
  }

  return (
    <main className="app-shell compact-shell">
      <nav className="topbar">
        <div>
          <div className="brand-line">Crypto Investor Dashboard</div>
          <div className="subtle">{user?.name || user?.email}</div>
        </div>
        <button className="button ghost" type="button" onClick={logout}>
          Logout
        </button>
      </nav>

      <section className="onboarding-card">
        <div className="step-dots" aria-label="Onboarding progress">
          {[1, 2, 3].map((dot) => (
            <span className={dot === step ? "active" : ""} key={dot} />
          ))}
        </div>
        {isEditing ? <div className="badge">Editing preferences</div> : null}
        {error ? <div className="notice error">{error}</div> : null}
        {renderStep()}
        <div className="onboarding-actions">
          <button
            className="button secondary"
            type="button"
            onClick={() => setStep(Math.max(1, step - 1))}
            disabled={step === 1 || isSaving}
          >
            Back
          </button>
          {step < 3 ? (
            <button
              className="button primary"
              type="button"
              onClick={() => setStep(step + 1)}
              disabled={!canContinue}
            >
              Continue
            </button>
          ) : (
            <button className="button primary" type="button" onClick={handleSave} disabled={!canContinue || isSaving}>
              {isSaving ? "Saving..." : "Save preferences"}
            </button>
          )}
        </div>
      </section>
    </main>
  );
}

export default function OnboardingPage() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <ProtectedPage>
      <OnboardingContent />
    </ProtectedPage>
  );
}
