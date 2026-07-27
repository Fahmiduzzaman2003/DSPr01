import { useEffect, useState } from "react";
import { fetchDiagnostics } from "../api.js";
import { rankColors } from "../theme.js";
import { ActualVsPredicted, ResidualHistogram } from "./DiagnosticCharts.jsx";

export default function DiagnosticsTab({ config }) {
  const [model, setModel] = useState(config.bestModel);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    fetchDiagnostics(model)
      .then((d) => !cancelled && setData(d))
      .catch((e) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [model]);

  // Each model keeps the colour it has on the leaderboard.
  const colors = rankColors(config.modelRanking.length, config.rankColors);
  const color = colors[config.modelRanking.indexOf(model)];

  return (
    <>
      <div className="card model-picker">
        <label htmlFor="model-picker">
          <strong>Model</strong>
        </label>
        <select
          id="model-picker"
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

      {error && <div className="status error">Could not load diagnostics: {error}</div>}
      {!data && !error && <div className="status">Loading diagnostics…</div>}

      {data && (
        <div className="grid-2">
          <ActualVsPredicted points={data.points} model={data.model} color={color} />
          <ResidualHistogram
            bins={data.residualBins}
            model={data.model}
            mean={data.residualMean}
            std={data.residualStd}
            color={color}
          />
        </div>
      )}
    </>
  );
}
