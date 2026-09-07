import { riskColorClasses } from '../utils/riskUtils';

/**
 * The one visual motif this product is meant to be recognized by: every
 * score, everywhere in the app, is a ring - never a bare number, never a
 * plain colored pill. The ring's fill fraction *is* the score, so scanning
 * a page of rings reads like scanning a page of gauges, which is the
 * point: investigators are triaging, not reading digits one at a time.
 */
export default function RiskScoreRing({ score, level, size = 56, strokeWidth = 5, showLabel = true }) {
  const { ring, text } = riskColorClasses(level);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="inline-flex items-center gap-2" role="img" aria-label={`Risk score ${score} out of 100, ${level} risk`}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#E2E6EA"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={ring}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="central"
          transform={`rotate(90 ${size / 2} ${size / 2})`}
          className={`font-mono font-semibold ${text}`}
          style={{ fontSize: size * 0.3 }}
        >
          {score}
        </text>
      </svg>
      {showLabel && (
        <span className={`font-sans text-xs font-semibold uppercase tracking-wide ${text}`}>
          {level}
        </span>
      )}
    </div>
  );
}
