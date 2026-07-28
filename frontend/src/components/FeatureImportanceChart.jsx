import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AXIS, GRID, INK_SECONDARY, MUTED, SURFACE } from "../theme.js";

/**
 * Horizontal bars of permutation importance, most important first.
 *
 * One hue for the whole series — the bar length already encodes magnitude, so
 * colouring by value would burn the only free channel on information the chart
 * shows twice. The hue is the model's rank colour, matching the leaderboard.
 */
export default function FeatureImportanceChart({
  title,
  subtitle,
  rows,
  color,
  height,
}) {
  // A negative score means shuffling the column *improved* the fit — noise, not
  // an effect. Plot it as zero so the bar and its label stay on the axis, while
  // the tooltip still reports the measured value.
  const data = rows.map((row) => ({ ...row, plotted: Math.max(row.importance, 0) }));
  const max = Math.max(...data.map((r) => r.plotted), 0.0001);
  const decimals = max < 0.1 ? 4 : max < 1 ? 3 : 2;

  return (
    <div className="card">
      <p className="card-title">{title}</p>
      <p className="card-subtitle">{subtitle}</p>
      <ResponsiveContainer width="100%" height={height ?? data.length * 34 + 44}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 4, right: 108, bottom: 4, left: 4 }}
        >
          <CartesianGrid horizontal={false} stroke={GRID} />
          <XAxis
            type="number"
            domain={[0, max * 1.18]}
            tickFormatter={(v) => Number(v).toFixed(decimals)}
            tick={{ fill: MUTED, fontSize: 11 }}
            axisLine={{ stroke: AXIS }}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={168}
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
            formatter={(_v, _n, item) => [
              `${item.payload.importance.toFixed(4)} R² lost · ${item.payload.share.toFixed(1)}% of total`,
              item.payload.label,
            ]}
          />
          <Bar
            dataKey="plotted"
            barSize={18}
            radius={[0, 6, 6, 0]}
            isAnimationActive={false}
          >
            {data.map((row) => (
              <Cell
                key={row.feature}
                fill={color}
                stroke={SURFACE}
                strokeWidth={2}
                // Near-zero contributors recede rather than reading as real signal.
                fillOpacity={row.share < 0.5 ? 0.35 : 1}
              />
            ))}
            <LabelList
              dataKey="share"
              position="right"
              offset={10}
              formatter={(v) => (v < 0.05 ? "~0%" : `${v.toFixed(1)}%`)}
              style={{ fill: INK_SECONDARY, fontSize: 12 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
