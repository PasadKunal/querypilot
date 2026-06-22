import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Props { sql: string }

export default function SQLBlock({ sql }: Props) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div className="rounded-2xl overflow-hidden border border-slate-700 shadow-lg">
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-800 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-slate-600" />
            <span className="w-3 h-3 rounded-full bg-slate-600" />
            <span className="w-3 h-3 rounded-full bg-slate-600" />
          </div>
          <span className="text-slate-500 text-xs font-mono ml-2">query.sql</span>
        </div>
        <button
          onClick={copy}
          className={`text-xs px-2.5 py-1 rounded-md transition-all font-medium ${
            copied
              ? "bg-emerald-500/20 text-emerald-400"
              : "bg-slate-700 text-slate-400 hover:bg-slate-600 hover:text-white"
          }`}
        >
          {copied ? "✓ Copied" : "Copy"}
        </button>
      </div>
      <SyntaxHighlighter
        language="sql"
        style={vscDarkPlus}
        customStyle={{ margin: 0, borderRadius: 0, fontSize: "13px", lineHeight: "1.7", padding: "16px 20px" }}
        wrapLongLines
      >
        {sql}
      </SyntaxHighlighter>
    </div>
  );
}
