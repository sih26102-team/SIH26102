/**
 * Central place for anything that turns a raw risk score into UI meaning.
 * Keeping this in one file means the HIGH/MEDIUM/LOW thresholds only ever
 * live in one place - if the ml-engine team changes scoring bands, this is
 * the only file that needs to change.
 */

export const RISK_LEVELS = {
  HIGH: { label: 'High', min: 70 },
  MEDIUM: { label: 'Medium', min: 40 },
  LOW: { label: 'Low', min: 0 },
};

export function levelFromScore(score) {
  if (score >= RISK_LEVELS.HIGH.min) return 'HIGH';
  if (score >= RISK_LEVELS.MEDIUM.min) return 'MEDIUM';
  return 'LOW';
}

export function riskColorClasses(level) {
  switch (level) {
    case 'HIGH':
      return { text: 'text-risk-high', bg: 'bg-risk-high-bg', ring: '#C0392B' };
    case 'MEDIUM':
      return { text: 'text-risk-medium', bg: 'bg-risk-medium-bg', ring: '#C77D22' };
    default:
      return { text: 'text-risk-low', bg: 'bg-risk-low-bg', ring: '#2F7A4F' };
  }
}

export function recommendedAction(level) {
  switch (level) {
    case 'HIGH':
      return 'Prioritize for verification';
    case 'MEDIUM':
      return 'Include in routine review queue';
    default:
      return 'No immediate action - monitor';
  }
}
