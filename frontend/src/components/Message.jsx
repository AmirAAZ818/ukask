import Answer from "./Answer";
import SourceCard from "./SourceCard";

// A user turn is a bubble. An assistant turn is a short document, answer on top
// and the evidence it rests on underneath, so it gets a rail instead.
export default function Message({ message }) {
  if (message.role === "user") {
    return <div className="msg--user">{message.content}</div>;
  }

  return (
    <div className={`msg--assistant ${message.error ? "is-error" : ""}`}>
      {message.error ? (
        <p className="answer answer--error">{message.content}</p>
      ) : (
        <Answer text={message.content} />
      )}

      {message.sources?.length > 0 && (
        <div className="sources">
          <div className="sources__label">مستندات این پاسخ</div>
          <div className="sources__list">
            {message.sources.map((source, i) => (
              <SourceCard key={i} source={source} index={i + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}