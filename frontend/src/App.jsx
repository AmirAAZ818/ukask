import { useEffect, useRef, useState } from "react";
import { askQuestion, fetchHealth } from "./api";
import { clearToken, hasValidSession } from "./auth";
import AuthControl from "./components/AuthControl";
import Composer from "./components/Composer";
import EmptyState from "./components/EmptyState";
import Footer from "./components/Footer";
import Health from "./components/Health";
import Logo from "./components/Logo";
import Message from "./components/Message";
import Thinking from "./components/Thinking";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [health, setHealth] = useState("checking");
  const [authed, setAuthed] = useState(() => hasValidSession());
  const [authNotice, setAuthNotice] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    fetchHealth()
      .then((data) => setHealth(data.status === "ok" ? "ok" : "down"))
      .catch(() => setHealth("down"));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pending]);

  function handleAuthed() {
    setAuthed(true);
    setAuthNotice(false);
  }

  async function send(text) {
    const question = text.trim();
    if (!question || pending) return;

    // sending is gated, browsing and typing never are. Check first, before
    // touching any other state, so a blocked question stays right where it
    // was typed instead of getting swept into an optimistic message push.
    if (!hasValidSession()) {
      clearToken();
      setAuthed(false);
      setAuthNotice(true);
      setDraft(question);
      return;
    }

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setDraft("");
    setPending(true);
    setAuthNotice(false);

    try {
      const data = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      if (err.status === 401) {
        // stored token turned out to be dead, expired or otherwise, same
        // message either way, and the icon has to actually flip back to
        // locked or it keeps lying about the state
        clearToken();
        setAuthed(false);
        setAuthNotice(true);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: err.message, error: true },
        ]);
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="page">
      <div className="app">
        <header className="header">
          <AuthControl authed={authed} attention={authNotice} onAuthed={handleAuthed} />
          <div className="header__desktop">
            <div className="header__desktop-row">
              <div className="brand" tabIndex={0}>
                <Logo />
                <span className="brand__name">UkAsk</span>
                <div className="health-tip">
                  <Health status={health} />
                </div>
              </div>
            </div>
            <span className="brand__tagline">
              دستیار آیین‌نامه‌های دانشگاه شهید باهنر کرمان
            </span>
          </div>

          <div className="header__mobile">
            <div className="brand">
              <Logo size={26} />
              <span className="brand__name">UkAsk</span>
            </div>
            <Health status={health} />
          </div>
        </header>

        {health === "down" && (
          <div className="banner">
            سرور پاسخ نمی‌دهد. بررسی کنید که بک‌اند روی پورت ۸۰۰۰ در حال اجرا باشد.
          </div>
        )}

        <main className="transcript">
          {messages.length === 0 && !pending && <EmptyState onPick={send} />}

          {messages.map((message, i) => (
            <Message key={i} message={message} />
          ))}

          {pending && <Thinking />}
          <div ref={bottomRef} />
        </main>

        {authNotice && (
          <div className="auth-notice">
            برای ارسال پرسش، ابتدا با کد دسترسی وارد شوید.
          </div>
        )}

        <Composer
          value={draft}
          onChange={setDraft}
          onSend={() => send(draft)}
          disabled={pending}
        />
      </div>

      <Footer />
    </div>
  );
}