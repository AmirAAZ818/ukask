import { useState } from "react";
import { toPersianDigits, toPercent } from "../format";

// One retrieved chunk: collapsed shows where the answer came from, expanded
// shows the regulation text verbatim so the student can check it themselves.
export default function SourceCard({ source, index }) {
  const [open, setOpen] = useState(false);

  const article = source.article_numbers
    ? `مادهٔ ${toPersianDigits(source.article_numbers)}`
    : "بدون شمارهٔ ماده";

  return (
    <div className="source">
      <button
        className="source__head"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        <span className="source__index">{toPersianDigits(index)}</span>

        <span className="source__body">
          {source.title && <span className="source__title">{source.title}</span>}

          <span className="source__meta">
            <span
              className={
                source.article_numbers
                  ? "source__article"
                  : "source__article source__article--none"
              }
            >
              {article}
            </span>
            {source.page != null && <span>صفحهٔ {toPersianDigits(source.page)}</span>}
            {source.chunk_type === "table" && <span className="source__tag">جدول</span>}
            {source.source_file && (
              <span className="source__file">{source.source_file}</span>
            )}
          </span>
        </span>

        <span className="source__score">
          <span className="source__percent">٪{toPercent(source.similarity)}</span>
          <span className="source__bar">
            <span style={{ width: `${Math.round(source.similarity * 100)}%` }} />
          </span>
        </span>
      </button>

      {open && <p className="source__text">{source.text}</p>}
    </div>
  );
}
