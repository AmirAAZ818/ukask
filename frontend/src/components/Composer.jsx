import { useRef, useEffect } from "react";

export default function Composer({ value, onChange, onSend, disabled }) {
  const ref = useRef(null);

  // grow the textarea with its content instead of scrolling a fixed box
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, [value]);

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  }

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <div className="composer">
      <div className="composer__field">
        <textarea
          ref={ref}
          className="composer__input"
          rows={1}
          value={value}
          placeholder="پرسش خود را دربارهٔ آیین‌نامه‌ها بنویسید"
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
        />
        <button
          className="composer__send"
          onClick={onSend}
          disabled={!canSend}
          aria-label="ارسال پرسش"
        >
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M20 12H4M4 12l6-6M4 12l6 6"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
      <div className="composer__hint">
        برای ارسال Enter و برای خط جدید Shift + Enter را بزنید.
      </div>
    </div>
  );
}