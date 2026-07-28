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
