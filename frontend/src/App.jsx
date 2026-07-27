import { useEffect, useState } from "react";
import { fetchConfig } from "./api.js";
import ComparisonTab from "./components/ComparisonTab.jsx";
import DiagnosticsTab from "./components/DiagnosticsTab.jsx";
import PredictTab from "./components/PredictTab.jsx";

const TABS = [
  { id: "predict", label: "Predict", Component: PredictTab },
  { id: "comparison", label: "Model comparison", Component: ComparisonTab },
  { id: "diagnostics", label: "Diagnostics", Component: DiagnosticsTab },
];

export default function App() {
  const [config, setConfig] = useState(null);
  const [error, setError] = useState(null);
  const [active, setActive] = useState(TABS[0].id);

  useEffect(() => {
    fetchConfig().then(setConfig).catch((e) => setError(e.message));
  }, []);

  const Active = TABS.find((t) => t.id === active).Component;

  return (
    <div className="page">
      <header className="app-header">
        <h1>HSC Result Predictor</h1>
        <p>
          Five regression models trained on student background data — predict a result
          and compare how the models perform.
        </p>
      </header>

      {error && (
        <div className="status error">
          Could not reach the API: {error}
          <br />
          Check that the backend is running and <code>VITE_API_URL</code> points at it.
        </div>
      )}
      {!config && !error && <div className="status">Loading models…</div>}

      {config && (
        <>
          <nav className="tabs" role="tablist">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                role="tab"
                aria-selected={active === tab.id}
                onClick={() => setActive(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </nav>
          <Active config={config} />
        </>
      )}
    </div>
  );
}
