import { useEffect, useRef, useState } from "react";
import { askQuestion, fetchHealth } from "./api";
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
  const bottomRef = useRef(null);

  // one check on load, enough to tell the student the backend is down before
  // they type a question into a void
  useEffect(() => {
    fetchHealth()
      .then((data) => setHealth(data.status === "ok" ? "ok" : "down"))
      .catch(() => setHealth("down"));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pending]);

  async function send(text) {
    const question = text.trim();
    if (!question || pending) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setDraft("");
    setPending(true);

    try {
      const data = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: err.message, error: true },
      ]);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="page">
      <div className="app">
        <header className="header">
          {/* desktop: centered lockup, health status revealed as a tooltip on hover/focus */}
          <div className="header__desktop">
            <div className="brand" tabIndex={0}>
              <Logo />
              <span className="brand__name">UkAsk</span>
              <div className="health-tip">
                <Health status={health} />
              </div>
            </div>
            <span className="brand__tagline">
              دستیار آیین‌نامه‌های دانشگاه شهید باهنر کرمان
            </span>
          </div>

          {/* mobile: original split layout, no tagline, health status inline */}
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