import { useEffect, useRef, useState } from "react";
import { login } from "../api";
import { setToken } from "../auth";

// Lock icon in the header. Closed/neutral by default, switches to unlocked
// once a valid session exists. Clicking it opens a small form for the access
// code, right there, no separate page.
export default function AuthControl({ authed, attention, onAuthed }) {
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const wrapRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    inputRef.current?.focus();
    function onDocClick(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false);
    }
    function onKeyDown(e) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onDocClick);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  async function submit(e) {
    e.preventDefault();
    if (!code.trim() || submitting) return;
    setSubmitting(true);
    setError("");
    try {
      const { token } = await login(code.trim());
      setToken(token);
      onAuthed();
      setOpen(false);
      setCode("");
    } catch {
      setError("کد نامعتبر است.");
    } finally {
      setSubmitting(false);
    }
  }

  const lockClass = authed
    ? "auth__lock auth__lock--open"
    : attention
    ? "auth__lock auth__lock--attention"
    : "auth__lock";

  return (
    <div className="auth" ref={wrapRef}>
      <button
        className={lockClass}
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label={authed ? "دسترسی فعال است" : "ورود با کد دسترسی"}
        title={authed ? "دسترسی فعال است" : "ورود با کد دسترسی"}
      >
        {authed ? <UnlockedIcon /> : <LockedIcon />}
      </button>

      {open && (
        <form className="auth__panel" onSubmit={submit}>
          <label className="auth__label" htmlFor="access-code">
            کد دسترسی
          </label>
          <input
            id="access-code"
            ref={inputRef}
            className="auth__input"
            type="password"
            maxLength={10}
            value={code}
            onChange={(e) => {
              setCode(e.target.value);
              setError("");
            }}
            placeholder="۱۰ نویسه"
            dir="ltr"
          />
          {error && <div className="auth__error">{error}</div>}
          <button className="auth__submit" type="submit" disabled={submitting}>
            {submitting ? "..." : "ورود"}
          </button>
        </form>
      )}
    </div>
  );
}

function LockedIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="5" y="10" width="14" height="10" rx="2.5" stroke="currentColor" strokeWidth="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function UnlockedIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="5" y="10" width="14" height="10" rx="2.5" stroke="currentColor" strokeWidth="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}