import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type ChartType = "bar" | "line" | "pie" | "none";

const COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#06b6d4", "#f97316", "#84cc16"];

function detectChart(columns: string[], rows: Record<string, unknown>[]): ChartType {
  if (rows.length < 2 || columns.length < 2) return "none";

  const numericCols = columns.filter((c) =>
    rows.slice(0, 5).every((r) => r[c] === null || typeof r[c] === "number" || !isNaN(Number(r[c])))
  );
  if (numericCols.length === 0) return "none";

  const labelCol = columns.find((c) => !numericCols.includes(c));
  if (!labelCol) return "none";

  // Pie: exactly 1 numeric, ≤10 rows, label col looks categorical
  if (numericCols.length === 1 && rows.length <= 10) return "pie";

  // Line: label col looks like a date/time/year
  if (/year|date|month|time|period/i.test(labelCol)) return "line";

  return "bar";
}

function prepareData(columns: string[], rows: Record<string, unknown>[]) {
  return rows.map((r) => {
    const out: Record<string, unknown> = {};
    for (const c of columns) {
      const v = r[c];
      out[c] = v === null ? null : isNaN(Number(v)) ? v : Number(v);
    }
    return out;
  });
}

interface Props {
  columns: string[];
  rows: Record<string, unknown>[];
}

export default function ResultChart({ columns, rows }: Props) {
  const chartType = detectChart(columns, rows);
  if (chartType === "none") return null;

  const numericCols = columns.filter((c) =>
    rows.slice(0, 5).every((r) => r[c] === null || !isNaN(Number(r[c])))
  );
  const labelCol = columns.find((c) => !numericCols.includes(c)) ?? columns[0];
  const data = prepareData(columns, rows);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">Chart</p>

      {chartType === "bar" && (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 4, right: 16, bottom: 40, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey={labelCol} tick={{ fontSize: 11, fill: "#94a3b8" }} angle={-30} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }} />
            {numericCols.length > 1 && <Legend wrapperStyle={{ fontSize: 12 }} />}
            {numericCols.map((col, i) => (
              <Bar key={col} dataKey={col} fill={COLORS[i % COLORS.length]} radius={[4, 4, 0, 0]} maxBarSize={48} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      )}

      {chartType === "line" && (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data} margin={{ top: 4, right: 16, bottom: 40, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey={labelCol} tick={{ fontSize: 11, fill: "#94a3b8" }} angle={-30} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }} />
            {numericCols.length > 1 && <Legend wrapperStyle={{ fontSize: 12 }} />}
            {numericCols.map((col, i) => (
              <Line key={col} type="monotone" dataKey={col} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={{ r: 3 }} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}

      {chartType === "pie" && (
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={data}
              dataKey={numericCols[0]}
              nameKey={labelCol}
              cx="50%"
              cy="50%"
              outerRadius={100}
              label={false}
              labelLine={false}
            >
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
