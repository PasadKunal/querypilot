import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Props {
  sql: string;
}

export default function SQLBlock({ sql }: Props) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="relative rounded-xl overflow-hidden border border-slate-200">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800">
        <span className="text-slate-400 text-xs font-mono uppercase tracking-wider">SQL</span>
        <button
          onClick={copy}
          className="text-slate-400 hover:text-white text-xs transition-colors"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <SyntaxHighlighter
        language="sql"
        style={vscDarkPlus}
        customStyle={{ margin: 0, borderRadius: 0, fontSize: "13px", lineHeight: "1.6" }}
        wrapLongLines
      >
        {sql}
      </SyntaxHighlighter>
    </div>
  );
}
