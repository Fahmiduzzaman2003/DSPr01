import { useEffect, useState } from "react";
import { postPredict } from "../api.js";
import { formatTarget, rankColors } from "../theme.js";
import RankBarChart from "./RankBarChart.jsx";

/** Default form state: the median / most common value for every feature. */
function defaultValues(features) {
  return Object.fromEntries(features.map((f) => [f.name, f.default]));
}

function Field({ feature, value, onChange }) {
  if (feature.kind === "category") {
    return (
      <div className="field">
        <label className="field-label" htmlFor={feature.name}>
          {feature.label}
        </label>
        <select
          id={feature.name}
          value={value}
          onChange={(e) => onChange(feature.name, e.target.value)}
        >
          {feature.choices.map((choice) => (
            <option key={choice} value={choice}>
              {choice}
            </option>
          ))}
        </select>
      </div>
    );
  }

  const step = feature.integer ? 1 : 0.01;
  return (
    <div className="field">
      <label className="field-label" htmlFor={feature.name}>
        {feature.label}
      </label>
      <div className="slider-row">
        <input
          id={feature.name}
          type="range"
          min={feature.minimum}
          max={feature.maximum}
          step={step}
          value={value}
          onChange={(e) => onChange(feature.name, Number(e.target.value))}
        />
        <output htmlFor={feature.name}>
          {feature.integer ? value : Number(value).toFixed(2)}
        </output>
      </div>
      <div className="slider-bounds">
        <span>{feature.minimum}</span>
        <span>{feature.maximum}</span>
      </div>
    </div>
  );
}

export default function PredictTab({ config }) {
  const [values, setValues] = useState(() => defaultValues(config.features));
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const runPrediction = async (payload) => {
    setBusy(true);
    setError(null);
    try {
      setResult(await postPredict(payload));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  // Show a result for the default student instead of an empty panel.
  useEffect(() => {
    runPrediction(defaultValues(config.features));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const update = (name, value) => setValues((v) => ({ ...v, [name]: value }));

  const colors = rankColors(config.modelRanking.length, config.rankColors);
  const rows =
    result?.predictions.map((p, i) => ({
      name: p.model,
      value: p.value,
      label: `${formatTarget(p.value, config, { compact: true })}${i === 0 ? "  ·  best model" : ""}`,
      hover: `Predicted ${formatTarget(p.value, config)} · rank #${p.rank}`,
      color: colors[i],
    })) ?? [];

  return (
    <div className="predict-layout">
      <div className="card">
        {config.features.map((feature) => (
          <Field
            key={feature.name}
            feature={feature}
            value={values[feature.name]}
            onChange={update}
          />
        ))}
        <button
          className="predict-button"
          onClick={() => runPrediction(values)}
          disabled={busy}
        >
          {busy ? "Predicting…" : "Predict"}
        </button>
      </div>

      <div>
        {error && <div className="status error">Prediction failed: {error}</div>}

        {result && (
          <>
            <div className="result-card">
              <div>
                <span className="label">Predicted {config.targetLabel}:</span>
                <span className="value">{formatTarget(result.headline, config)}</span>
              </div>
              <p className="from">
                from <strong>{result.bestModel}</strong> — the most accurate model on
                the hold-out set (R² {config.metrics[result.bestModel].R2.toFixed(3)}).
              </p>
            </div>

            <RankBarChart
              title="Prediction by model"
              subtitle={`ranked by hold-out accuracy · dashed line = average (${formatTarget(result.mean, config)})`}
              rows={rows}
              referenceValue={result.mean}
            />

            <div className="card" style={{ marginTop: 16 }}>
              <p className="card-title">Every model's prediction (best to worst)</p>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Model</th>
                      <th>Prediction</th>
                      <th>R² (hold-out)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.predictions.map((p, i) => (
                      <tr key={p.model}>
                        {[
                          `#${p.rank}`,
                          p.model,
                          formatTarget(p.value, config),
                          p.r2.toFixed(4),
                        ].map(
                          (cell, c) => (
                            <td key={c} className="ranked" style={{ color: colors[i] }}>
                              {cell}
                            </td>
                          )
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
