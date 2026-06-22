interface Props {
  columns: string[];
  rows: Record<string, unknown>[];
  truncated: boolean;
}

export default function ResultsTable({ columns, rows, truncated }: Props) {
  if (rows.length === 0) {
    return (
      <p className="text-slate-400 text-sm py-4 text-center">
        Query returned 0 rows.
      </p>
    );
  }

  return (
    <div>
      <div className="overflow-x-auto rounded-xl border border-slate-200">
        <table className="w-full text-sm text-left">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              {columns.map((col) => (
                <th key={col} className="px-4 py-3 font-semibold text-slate-600 whitespace-nowrap">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map((row, i) => (
              <tr key={i} className="hover:bg-slate-50 transition-colors">
                {columns.map((col) => (
                  <td key={col} className="px-4 py-3 text-slate-700 whitespace-nowrap font-mono text-xs">
                    {row[col] === null || row[col] === undefined
                      ? <span className="text-slate-300">null</span>
                      : String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {truncated && (
        <p className="text-amber-600 text-xs mt-2">
          Results truncated at 1,000 rows.
        </p>
      )}
    </div>
  );
}
