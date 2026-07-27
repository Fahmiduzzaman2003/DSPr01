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

/** `count` colours from the ramp, best first, evenly spaced when count < 5. */
export function rankColors(count, ramp = RANK_RAMP) {
  if (count <= 1) return [ramp[0]];
  const steps = ramp.length - 1;
  return Array.from({ length: count }, (_, i) =>
    ramp[Math.round((i * steps) / (count - 1))]
  );
}
