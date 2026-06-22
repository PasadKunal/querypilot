interface Props {
  columns: string[];
  rows: Record<string, unknown>[];
  truncated: boolean;
}

export default function ResultsTable({ columns, rows, truncated }: Props) {
  if (rows.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 bg-white rounded-2xl border border-slate-200">
        <span className="text-3xl mb-2">📭</span>
        <p className="text-slate-500 text-sm">Query returned 0 rows</p>
      </div>
    );
  }

  return (
    <div>
      <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="border-b border-slate-100">
              {columns.map((col) => (
                <th key={col} className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {rows.map((row, i) => (
              <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                {columns.map((col) => (
                  <td key={col} className="px-4 py-3 text-slate-700 whitespace-nowrap font-mono text-xs">
                    {row[col] === null || row[col] === undefined ? (
                      <span className="text-slate-300 not-italic font-sans">null</span>
                    ) : (
                      String(row[col])
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {truncated && (
        <p className="text-amber-600 text-xs mt-2 flex items-center gap-1.5">
          <span>⚠</span> Results truncated at 1,000 rows.
        </p>
      )}
    </div>
  );
}
