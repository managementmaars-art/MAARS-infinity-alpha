import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const MarkdownRenderer = ({ content, className = "" }) => {
  if (!content) return null;

  return (
    <div className={`prose prose-invert prose-sm max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <h1 className="text-lg font-bold text-white mt-3 mb-2">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-semibold text-white mt-3 mb-1.5">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-semibold text-zinc-200 mt-2 mb-1">{children}</h3>,
          p: ({ children }) => <p className="text-sm leading-relaxed mb-2 last:mb-0">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-2 text-sm">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-2 text-sm">{children}</ol>,
          li: ({ children }) => <li className="text-sm leading-relaxed">{children}</li>,
          strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
          em: ({ children }) => <em className="italic text-zinc-300">{children}</em>,
          code: ({ inline, children }) =>
            inline ? (
              <code className="px-1.5 py-0.5 bg-white/10 rounded text-xs font-mono text-emerald-400">{children}</code>
            ) : (
              <pre className="bg-zinc-900/80 border border-white/10 rounded-lg p-3 overflow-x-auto my-2">
                <code className="text-xs font-mono text-emerald-300 leading-relaxed">{children}</code>
              </pre>
            ),
          pre: ({ children }) => <>{children}</>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-indigo-500/50 pl-3 my-2 text-zinc-400 italic">{children}</blockquote>
          ),
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline underline-offset-2">
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-2">
              <table className="min-w-full text-sm border border-white/10 rounded">{children}</table>
            </div>
          ),
          th: ({ children }) => <th className="px-3 py-1.5 bg-white/5 text-left text-xs font-medium text-zinc-300 border-b border-white/10">{children}</th>,
          td: ({ children }) => <td className="px-3 py-1.5 text-xs text-zinc-400 border-b border-white/5">{children}</td>,
          hr: () => <hr className="border-white/10 my-3" />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
