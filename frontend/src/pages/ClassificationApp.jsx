import { Link } from "react-router-dom";

/**
 * Placeholder until the heart failure notebook and its dataset are added.
 *
 * Once they are, this becomes the classification equivalent of RegressionApp:
 * the same three tabs, backed by /api/classification/* instead.
 */
export default function ClassificationApp() {
  return (
    <div className="page">
      <Link to="/" className="back-link">
        ← All algorithms
      </Link>

      <header className="app-header">
        <h1>Heart Failure Predictor</h1>
        <p>Classification models trained on clinical measurements.</p>
      </header>

      <div className="status">
        Not built yet — the heart failure notebook and its dataset still need to be
        added to the project.
      </div>
    </div>
  );
}
