import {
  Bar,
  BarChart,
  Cell,
  CartesianGrid,
  LabelList,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AXIS, GRID, INK_SECONDARY, MUTED, SURFACE } from "../theme.js";

/**
 * Horizontal bars, best at the top, coloured green -> red down the ranking.
 *
 * `rows` arrive best-first as { name, value, label, hover, color }. Bars start
 * at zero — the scores differ in the third decimal, so each carries a label
 * showing its gap to the winner, which is where the real separation shows.
 */
export default function RankBarChart({
  title,
  subtitle,
  rows,
  referenceValue,
  height = 300,
}) {
  const max = Math.max(...rows.map((r) => r.value));
  // Enough significant digits to tell the ticks apart without printing raw floats.
  const decimals = max < 0.1 ? 4 : max < 10 ? 2 : 0;
  const formatTick = (v) => Number(v).toFixed(decimals);

  return (
    <div className="card">
      <p className="card-title">{title}</p>
      <p className="card-subtitle">{subtitle}</p>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={rows}
          layout="vertical"
          margin={{ top: 4, right: 132, bottom: 4, left: 4 }}
          barCategoryGap="45%"
        >
          <CartesianGrid horizontal={false} stroke={GRID} />
          <XAxis
            type="number"
            domain={[0, max * 1.12]}
            tickFormatter={formatTick}
            tick={{ fill: MUTED, fontSize: 11 }}
            axisLine={{ stroke: AXIS }}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={128}
            tick={{ fill: INK_SECONDARY, fontSize: 12 }}
            axisLine={{ stroke: AXIS }}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(0,0,0,0.04)" }}
            contentStyle={{
              background: SURFACE,
              border: `1px solid ${AXIS}`,
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(value, _n, item) => [item.payload.hover, item.payload.name]}
          />
          {referenceValue != null && (
            <ReferenceLine
              x={referenceValue}
              stroke={INK_SECONDARY}
              strokeWidth={2}
              strokeDasharray="6 4"
            />
          )}
          <Bar
            dataKey="value"
            barSize={24}
            radius={[0, 6, 6, 0]}
            isAnimationActive={false}
          >
            {rows.map((row) => (
              <Cell key={row.name} fill={row.color} stroke={SURFACE} strokeWidth={2} />
            ))}
            <LabelList
              dataKey="label"
              position="right"
              offset={10}
              style={{ fill: INK_SECONDARY, fontSize: 12 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
