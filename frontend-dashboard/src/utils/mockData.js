
const AGENCIES = [
  'District Rural Development Agency',
  'Public Works Division',
  'Municipal Engineering Cell',
  'State Construction Corporation',
  'Panchayati Raj Engineering Wing',
];

const CATEGORIES = [
  'Drinking Water',
  'Road Connectivity',
  'School Infrastructure',
  'Sanitation',
  'Community Hall',
  'Electrification',
  'Irrigation Support',
];

const STATUSES = ['Ongoing', 'Delayed', 'Completed', 'Not Started', 'Stalled'];

const STATES = [
  { state: 'Andhra Pradesh', districts: ['Nellore', 'Guntur', 'Visakhapatnam'] },
  { state: 'Karnataka', districts: ['Belagavi', 'Mysuru', 'Ballari'] },
  { state: 'Uttar Pradesh', districts: ['Varanasi', 'Kanpur Nagar', 'Meerut'] },
  { state: 'Maharashtra', districts: ['Nashik', 'Aurangabad', 'Kolhapur'] },
  { state: 'Tamil Nadu', districts: ['Madurai', 'Coimbatore', 'Salem'] },
  { state: 'West Bengal', districts: ['Howrah', 'Malda', 'Bardhaman'] },
];

// Rough representative lat/lng per district, for FlaggedMap - illustrative only.
const DISTRICT_COORDS = {
  Nellore: [14.4426, 79.9865],
  Guntur: [16.3067, 80.4365],
  Visakhapatnam: [17.6868, 83.2185],
  Belagavi: [15.8497, 74.4977],
  Mysuru: [12.2958, 76.6394],
  Ballari: [15.1394, 76.9214],
  Varanasi: [25.3176, 82.9739],
  'Kanpur Nagar': [26.4499, 80.3319],
  Meerut: [28.9845, 77.7064],
  Nashik: [19.9975, 73.7898],
  Aurangabad: [19.8762, 75.3433],
  Kolhapur: [16.705, 74.2433],
  Madurai: [9.9252, 78.1198],
  Coimbatore: [11.0168, 76.9558],
  Salem: [11.6643, 78.146],
  Howrah: [22.5958, 88.2636],
  Malda: [25.0108, 88.1411],
  Bardhaman: [23.2324, 87.8615],
};

function seededRandom(seed) {
  let value = seed;
  return () => {
    value = (value * 9301 + 49297) % 233280;
    return value / 233280;
  };
}

function pick(rand, arr) {
  return arr[Math.floor(rand() * arr.length)];
}

function buildReasons(rand, spendProgressGap, delayDays, utilization) {
  const reasons = [];
  if (spendProgressGap > 35) {
    reasons.push({
      code: 'SPEND_PROGRESS_MISMATCH',
      text: `Expenditure is ${spendProgressGap}% ahead of reported physical progress`,
    });
  }
  if (delayDays > 180) {
    reasons.push({
      code: 'PROJECT_DELAY',
      text: `Project is ${delayDays} days past its expected completion date`,
    });
  }
  if (utilization < 25) {
    reasons.push({
      code: 'FUND_PARKING',
      text: `Only ${utilization}% of released funds have been utilized`,
    });
  }
  if (rand() > 0.7) {
    reasons.push({
      code: 'AGENCY_CONCENTRATION',
      text: 'Implementing agency handles an unusually high share of this MP\'s sanctioned works',
    });
  }
  if (rand() > 0.85) {
    reasons.push({
      code: 'COST_OVERRUN',
      text: 'Final expenditure trend exceeds sanctioned amount at current burn rate',
    });
  }
  if (reasons.length === 0) {
    reasons.push({
      code: 'WITHIN_NORMAL_RANGE',
      text: 'No individual signal crossed its threshold; flagged only for routine sampling',
    });
  }
  return reasons;
}

function scoreToLevel(score) {
  if (score >= 70) return 'HIGH';
  if (score >= 40) return 'MEDIUM';
  return 'LOW';
}

function generateProject(index) {
  const rand = seededRandom(index * 7919 + 13);
  const { state, districts } = pick(rand, STATES);
  const district = pick(rand, districts);
  const category = pick(rand, CATEGORIES);
  const agency = pick(rand, AGENCIES);
  const status = pick(rand, STATUSES);

  const sanctioned = Math.round((5 + rand() * 45) * 100000); // 5L - 50L
  const released = Math.round(sanctioned * (0.3 + rand() * 0.7));
  const expenditure = Math.round(released * (0.1 + rand() * 1.05));
  const utilization = Math.round((expenditure / released) * 100);

  const progressPct = Math.round(rand() * 100);
  const spendPct = Math.round((expenditure / sanctioned) * 100);
  const spendProgressGap = Math.max(0, spendPct - progressPct);

  const startYear = 2023 + Math.floor(rand() * 2);
  const startMonth = 1 + Math.floor(rand() * 12);
  const startDate = new Date(startYear, startMonth - 1, 1 + Math.floor(rand() * 27));
  const expectedDays = 180 + Math.floor(rand() * 270);
  const expectedCompletion = new Date(startDate.getTime() + expectedDays * 86400000);

  const today = new Date('2026-08-23');
  const delayDays =
    status === 'Completed'
      ? 0
      : Math.max(0, Math.round((today - expectedCompletion) / 86400000));

  const actualCompletion =
    status === 'Completed'
      ? new Date(expectedCompletion.getTime() + (rand() > 0.6 ? delayDays : -20) * 86400000)
      : null;

  let riskScore = Math.round(
    spendProgressGap * 0.5 +
      Math.min(delayDays / 4, 30) +
      (utilization < 25 ? 20 : 0) +
      rand() * 15
  );
  riskScore = Math.max(2, Math.min(98, riskScore));

  const coords = DISTRICT_COORDS[district] || [22.9734, 78.6569];
  const jitter = () => (rand() - 0.5) * 0.6;

  return {
    id: `MPL-${state.slice(0, 2).toUpperCase()}-${(1000 + index).toString()}`,
    isSynthetic: true,
    projectId: `MPL-${state.slice(0, 2).toUpperCase()}-${(1000 + index).toString()}`,
    constituency: `${district} Constituency`,
    district,
    state,
    sanctionedAmount: sanctioned,
    releasedAmount: released,
    expenditure,
    utilizationPct: utilization,
    progressPct,
    status,
    startDate: startDate.toISOString().slice(0, 10),
    expectedCompletionDate: expectedCompletion.toISOString().slice(0, 10),
    actualCompletionDate: actualCompletion ? actualCompletion.toISOString().slice(0, 10) : null,
    implementingAgency: agency,
    category,
    delayDays,
    riskScore,
    riskLevel: scoreToLevel(riskScore),
    reasons: buildReasons(rand, spendProgressGap, delayDays, utilization),
    dataQuality: {
      completeness: Math.round(80 + rand() * 20),
      lastUpdated: new Date(today.getTime() - Math.floor(rand() * 20) * 86400000)
        .toISOString()
        .slice(0, 10),
      flags:
        rand() > 0.85
          ? ['Missing actual-completion field on source record']
          : [],
    },
    lat: coords[0] + jitter(),
    lng: coords[1] + jitter(),
  };
}

export const MOCK_PROJECTS = Array.from({ length: 42 }, (_, i) => generateProject(i + 1));

export function buildMockTrend() {
  // Monthly aggregate: total flagged vs. high-risk count, last 9 months.
  const months = [
    'Dec 25', 'Jan 26', 'Feb 26', 'Mar 26', 'Apr 26',
    'May 26', 'Jun 26', 'Jul 26', 'Aug 26',
  ];
  const rand = seededRandom(4242);
  let base = 18;
  return months.map((month) => {
    base += Math.round(rand() * 6 - 2);
    base = Math.max(10, base);
    const high = Math.max(1, Math.round(base * (0.2 + rand() * 0.15)));
    return { month, flagged: base, highRisk: high };
  });
}

export const MOCK_CASES = MOCK_PROJECTS.filter((p) => p.riskLevel !== 'LOW')
  .slice(0, 14)
  .map((p, i) => ({
    caseId: `CASE-${(2026000 + i).toString()}`,
    isSynthetic: true,
    projectId: p.projectId,
    status: pick(seededRandom(i * 31 + 5), ['Open', 'Under Review', 'Escalated', 'Closed - No Action', 'Closed - Action Taken']),
    assignedTo: pick(seededRandom(i * 17 + 3), ['R. Sharma', 'A. Iyer', 'M. Fernandes', 'Unassigned']),
    openedOn: p.dataQuality.lastUpdated,
    auditTrail: [
      { at: p.startDate, actor: 'System', action: 'Project ingested from source data' },
      { at: p.dataQuality.lastUpdated, actor: 'Risk Engine', action: `Flagged with risk score ${p.riskScore} (${p.riskLevel})` },
    ],
  }));
