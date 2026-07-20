import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Renders model markdown (lists, tables) instead of raw asterisks and pipes.
// remark-gfm adds table support; raw HTML stays off so output can't inject markup.
export default function Answer({ text }) {
  return (
    <div className="answer">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
    </div>
  );
}