import { formatTarget, metricDecimals, rankColors } from "../theme.js";
import RankBarChart from "./RankBarChart.jsx";

const CHART_ORDER = ["MAE", "MSE", "RMSE", "R2"];

/** Models sorted best-to-worst on one metric, with each one's gap to the winner. */
function rankForMetric(metric, config) {
  const spec = config.metricSpecs[metric];
  const entries = Object.entries(config.metrics).map(([model, scores]) => ({
    model,
    value: scores[metric],
  }));
  entries.sort((a, b) =>
    spec.lower_is_better ? a.value - b.value : b.value - a.value
  );

  const best = entries[0].value;
  const colors = rankColors(entries.length, config.rankColors);
  // MSE on a six-figure target runs to 10 digits; R² needs four decimals.
  const decimals = metricDecimals(best);
  const show = (v) =>
    v.toLocaleString(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });

  return entries.map((entry, i) => {
    const gap = Math.abs(entry.value - best) / Math.abs(best) * 100;
    return {
      name: entry.model,
      value: entry.value,
      label: `${show(entry.value)}${i === 0 ? "  ·  best" : `  ·  ${gap.toFixed(1)}% worse`}`,
      hover:
        i === 0
          ? `${metric} ${show(entry.value)} · best model`
          : `${metric} ${show(entry.value)} · ${gap.toFixed(1)}% worse than best`,
      color: colors[i],
    };
  });
}

export default function ComparisonTab({ config }) {
  const best = config.bestModel;
  const bestScores = config.metrics[best];
  const metricKeys = Object.keys(config.metricSpecs);

  return (
    <>
      <div className="summary-card">
        <strong>Best model: {best}</strong> — R² {bestScores.R2.toFixed(4)}, MAE{" "}
        {formatTarget(bestScores.MAE, config)}, RMSE{" "}
        {formatTarget(bestScores.RMSE, config)}. All figures are on the same{" "}
        {config.testSizePercent}% hold-out split. In every chart below,{" "}
        <strong>green is the best model and red the worst</strong>.
      </div>

      <div className="grid-2">
        {CHART_ORDER.map((metric) => {
          const spec = config.metricSpecs[metric];
          return (
            <RankBarChart
              key={metric}
              title={metric === "R2" ? spec.label : `${spec.label} (${metric})`}
              subtitle={`${spec.lower_is_better ? "lower" : "higher"} is better · green = best, red = worst · % = gap to the winner`}
              rows={rankForMetric(metric, config)}
            />
          );
        })}
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <p className="card-title">Metrics table — each column coloured by its own ranking</p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Model</th>
                {metricKeys.map((m) => (
                  <th key={m}>{m}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {config.modelRanking.map((model) => (
                <tr key={model}>
                  <td>{model}</td>
                  {metricKeys.map((metric) => {
                    // Colour by this model's position within this metric's own ranking.
                    const ranked = rankForMetric(metric, config);
                    const row = ranked.find((r) => r.name === model);
                    const value = config.metrics[model][metric];
                    const decimals = metricDecimals(value);
                    return (
                      <td key={metric} className="ranked" style={{ color: row.color }}>
                        {value.toLocaleString(undefined, {
                          minimumFractionDigits: decimals,
                          maximumFractionDigits: decimals,
                        })}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
