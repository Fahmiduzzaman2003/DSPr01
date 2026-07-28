/** Design tokens shared by every chart and table.
 *
 * The rank ramp (green = best -> red = worst) is served by the API so backend
 * and frontend never drift; RANK_RAMP here is only the fallback used before
 * config loads. Every step clears 3:1 contrast on the light chart surface.
 */
export const RANK_RAMP = ["#1a7f37", "#2e9e4f", "#b8860b", "#e8702a", "#c62828"];

export const SURFACE = "#fcfcfb";
export const INK = "#0b0b0b";
export const INK_SECONDARY = "#52514e";
export const MUTED = "#898781";
export const GRID = "#e1e0d9";
export const AXIS = "#c3c2b7";

/**
 * Format a value in the target's units (e.g. `$163,000`).
 *
 * Targets range from a 0-5 grade to a six-figure price, so decimals and any
 * prefix come from the API rather than being hardcoded per chart.
 */
export function formatTarget(value, config, { compact = false } = {}) {
  const decimals = config.targetDecimals ?? 2;
  const text = compact && Math.abs(value) >= 10000
    ? `${Math.round(value / 1000)}k`
    : value.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      });
  return `${config.targetPrefix ?? ""}${text}`;
}

/** Sensible decimal count for a metric whose scale we don't know in advance. */
export function metricDecimals(value) {
  const magnitude = Math.abs(value);
  if (magnitude >= 1000) return 0;
  if (magnitude >= 1) return 2;
  return 4;
}

const hexToRgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
const rgbToHex = (rgb) =>
  "#" + rgb.map((v) => Math.round(v).toString(16).padStart(2, "0")).join("");

/**
 * `count` colours sampled along the ramp, best first.
 *
 * Interpolates between the ramp stops rather than snapping to them, so any
 * number of models gets a distinct colour — snapping hands two models the same
 * hue as soon as `count` exceeds the number of stops.
 */
export function rankColors(count, ramp = RANK_RAMP) {
  if (count <= 1) return [ramp[0]];

  const lastStop = ramp.length - 1;
  return Array.from({ length: count }, (_, i) => {
    const position = (i / (count - 1)) * lastStop;
    const lower = Math.floor(position);
    if (lower >= lastStop) return ramp[lastStop];

    const t = position - lower;
    const from = hexToRgb(ramp[lower]);
    const to = hexToRgb(ramp[lower + 1]);
    return rgbToHex(from.map((c, channel) => c + (to[channel] - c) * t));
  });
}
