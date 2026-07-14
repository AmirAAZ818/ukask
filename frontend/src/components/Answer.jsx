import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// The model sometimes answers with lists or a small table (article text
// often has both), so this renders that markdown instead of dumping raw
// asterisks and pipes into the chat. remark-gfm adds table support, no raw
// HTML is ever rendered, that stays off by default so model output can't
// inject markup.
export default function Answer({ text }) {
  return (
    <div className="answer">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
    </div>
  );
}