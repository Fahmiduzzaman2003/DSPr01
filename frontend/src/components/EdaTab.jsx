/**
 * The ydata-profiling report, embedded.
 *
 * `eda.html` lives in `public/`, so Vite copies it into `dist/` untouched and it
 * is served as a plain static file — no runtime dependency on ydata-profiling,
 * which cannot even be installed alongside the app's pandas 3.
 */
const REPORT_URL = `${import.meta.env.BASE_URL}eda.html`;

export default function EdaTab({ config }) {
  return (
    <>
      <div className="summary-card">
        Automated profile of the <strong>{config.datasetName}</strong> dataset —
        every column's distribution, missing values, correlations and outliers,
        generated with <strong>ydata-profiling</strong> before any model was
        trained.{" "}
        <a href={REPORT_URL} target="_blank" rel="noreferrer">
          Open the full report in a new tab ↗
        </a>
      </div>

      <div className="card eda-frame">
        <iframe src={REPORT_URL} title="Exploratory data analysis report" />
      </div>
    </>
  );
}
