import { useEffect, useState } from "react";
import { fetchImportance } from "../api.js";
import { rankColors } from "../theme.js";
import FeatureImportanceChart from "./FeatureImportanceChart.jsx";

export default function InterpretabilityTab({ config }) {
  const [model, setModel] = useState(config.bestModel);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    fetchImportance(model)
      .then((d) => !cancelled && setData(d))
      .catch((e) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [model]);

  const colors = rankColors(config.modelRanking.length, config.rankColors);
  const color = colors[config.modelRanking.indexOf(model)];

  const top = data?.features[0];
  // One feature carries almost everything, so a single linear chart renders the
  // rest as invisible slivers. The second chart drops the leader and rescales.
  const rest = data?.features.slice(1) ?? [];

  return (
    <>
      <div className="card model-picker">
        <label htmlFor="importance-model">
          <strong>Model</strong>
        </label>
        <select
          id="importance-model"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        >
          {config.modelRanking.map((name, i) => (
            <option key={name} value={name}>
              #{i + 1} — {name}
            </option>
          ))}
        </select>
      </div>

      {error && <div className="status error">Could not load importance: {error}</div>}
      {!data && !error && <div className="status">Measuring feature importance…</div>}

      {data && (
        <>
          <div className="summary-card">
            <strong>{top.label}</strong> alone accounts for{" "}
            <strong>{top.share.toFixed(1)}%</strong> of what {data.model} uses to
            predict. Importance is measured by <strong>permutation</strong> — each
            column is shuffled in turn and the drop in R² recorded, so every model
            is scored the same way regardless of how it works internally.
          </div>

          <div className="grid-2">
            <FeatureImportanceChart
              title="All features"
              subtitle="R² lost when the column is shuffled · % of total importance"
              rows={data.features}
              color={color}
            />
            <FeatureImportanceChart
              title={`Excluding ${top.label}`}
              subtitle="the same data rescaled, so the remaining features are readable"
              rows={rest}
              color={color}
            />
          </div>
        </>
      )}
    </>
  );
}
