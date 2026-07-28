import { Link } from "react-router-dom";

/** Landing page: pick which family of algorithms to explore. */
const SECTIONS = [
  {
    to: "/regression",
    kind: "Regression",
    title: "HSC Result Predictor",
    blurb:
      "Predicts a continuous grade from a student's family background, schooling and habits.",
    detail: "Six models compared on MAE, MSE, RMSE and R².",
    accent: "#1a7f37",
    ready: true,
  },
  {
    to: "/classification",
    kind: "Classification",
    title: "Heart Failure Predictor",
    blurb:
      "Predicts a yes/no outcome from clinical measurements rather than a number.",
    detail: "Compared on accuracy, precision, recall, F1 and ROC-AUC.",
    accent: "#2563eb",
    ready: false,
  },
];

export default function Home() {
  return (
    <div className="page">
      <header className="app-header">
        <h1>Machine Learning Explorer</h1>
        <p>
          Choose an algorithm type. Each section trains several models on a real
          dataset and compares how they perform.
        </p>
      </header>

      <div className="choice-grid">
        {SECTIONS.map((section) => (
          <Link
            key={section.to}
            to={section.to}
            className="choice-card"
            style={{ "--card-accent": section.accent }}
          >
            <span className="choice-kind">{section.kind}</span>
            <h2>{section.title}</h2>
            <p>{section.blurb}</p>
            <p className="choice-detail">{section.detail}</p>
            <span className="choice-cta">
              {section.ready ? "Open →" : "Coming soon"}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
