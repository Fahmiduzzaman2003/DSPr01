import {
  Bar,
  BarChart,
  CartesianGrid,
  Label,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { AXIS, GRID, INK_SECONDARY, MUTED, SURFACE } from "../theme.js";

const tooltipStyle = {
  background: SURFACE,
  border: `1px solid ${AXIS}`,
  borderRadius: 8,
  fontSize: 12,
};

const axisTick = { fill: MUTED, fontSize: 11 };
const axisLabel = { fill: MUTED, fontSize: 12 };

/** Predictions against ground truth, with a dashed perfect-fit reference. */
export function ActualVsPredicted({ points, model, color }) {
  const values = points.flatMap((p) => [p.actual, p.predicted]);
  const low = Math.min(...values);
  const high = Math.max(...values);
  const pad = (high - low) * 0.04;
  const domain = [low - pad, high + pad];
  // Two endpoints are enough to draw the y = x reference.
  const reference = [
    { actual: domain[0], predicted: domain[0] },
    { actual: domain[1], predicted: domain[1] },
  ];

  return (
    <div className="card">
      <p className="card-title">Actual vs predicted — {model}</p>
      <p className="card-subtitle">dashed line = perfect prediction · hold-out set</p>
      <ResponsiveContainer width="100%" height={340}>
        <ScatterChart margin={{ top: 8, right: 16, bottom: 24, left: 12 }}>
          <CartesianGrid stroke={GRID} />
          <XAxis
            type="number"
            dataKey="actual"
            domain={domain}
            tickFormatter={(v) => v.toFixed(1)}
            tick={axisTick}
            axisLine={{ stroke: AXIS }}
            tickLine={false}
          >
            <Label value="Actual" position="bottom" offset={4} style={axisLabel} />
          </XAxis>
          <YAxis
            type="number"
            dataKey="predicted"
            domain={domain}
            tickFormatter={(v) => v.toFixed(1)}
            tick={axisTick}
            axisLine={{ stroke: AXIS }}
            tickLine={false}
          >
            <Label
              value="Predicted"
              angle={-90}
              position="insideLeft"
              style={{ ...axisLabel, textAnchor: "middle" }}
            />
          </YAxis>
          <ZAxis range={[42, 42]} />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            contentStyle={tooltipStyle}
            formatter={(value, name) => [Number(value).toFixed(2), name]}
          />
          <Scatter
            data={reference}
            line={{ stroke: MUTED, strokeWidth: 2, strokeDasharray: "6 4" }}
            shape={() => null}
            isAnimationActive={false}
            legendType="none"
          />
          <Scatter
            name={model}
            data={points}
            fill={color}
            fillOpacity={0.55}
            stroke={SURFACE}
            strokeWidth={1}
            isAnimationActive={false}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

/** Prediction errors; a centred, narrow shape is the good case. */
export function ResidualHistogram({ bins, model, mean, std, color }) {
  return (
    <div className="card">
      <p className="card-title">Residuals — {model}</p>
      <p className="card-subtitle">
        predicted − actual · mean {mean >= 0 ? "+" : ""}
        {mean.toFixed(3)} · std {std.toFixed(3)}
      </p>
      <ResponsiveContainer width="100%" height={340}>
        <BarChart data={bins} margin={{ top: 8, right: 16, bottom: 24, left: 12 }}>
          <CartesianGrid vertical={false} stroke={GRID} />
          <XAxis
            dataKey="error"
            type="number"
            domain={["dataMin", "dataMax"]}
            tickFormatter={(v) => v.toFixed(2)}
            tick={axisTick}
            axisLine={{ stroke: AXIS }}
            tickLine={false}
          >
            <Label value="Prediction error" position="bottom" offset={4} style={axisLabel} />
          </XAxis>
          <YAxis
            tick={axisTick}
            axisLine={{ stroke: AXIS }}
            tickLine={false}
          >
            <Label
              value="Count"
              angle={-90}
              position="insideLeft"
              style={{ ...axisLabel, textAnchor: "middle" }}
            />
          </YAxis>
          <Tooltip
            cursor={{ fill: "rgba(0,0,0,0.04)" }}
            contentStyle={tooltipStyle}
            labelFormatter={(v) => `Error ${Number(v).toFixed(3)}`}
            formatter={(value) => [value, "predictions"]}
          />
          <ReferenceLine x={0} stroke={INK_SECONDARY} strokeWidth={2} strokeDasharray="6 4" />
          <Bar dataKey="count" fill={color} isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
