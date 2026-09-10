
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

function buildReasons(rand, spendProgressGap, delayDays, utilization, progressPct, expenditure) {
  const reasons = [];

  if (expenditure > 0 && progressPct < 5) {
    reasons.push({
      code: 'GHOST_PROJECT_RISK',
      text: 'High financial disbursement recorded alongside near-zero (<5%) physical progress on-site',
    });
  }

  if (spendProgressGap > 30) {
    reasons.push({
      code: 'SPEND_PROGRESS_MISMATCH',
      text: `Disbursed funds are ${spendProgressGap}% ahead of verified physical progress`,
    });
  }

  if (delayDays > 120) {
    reasons.push({
      code: 'SLA_TIMELINE_BREACH',
      text: `Project is ${delayDays} days overdue beyond statutory completion timeline (Para 3.2.12)`,
    });
  }

  if (utilization < 25) {
    reasons.push({
      code: 'FUND_PARKING',
      text: `Only ${utilization}% of released funds utilized; capital parked idle at Implementing Agency`,
    });
  }

  if (rand() > 0.65) {
    reasons.push({
      code: 'MISSING_GEOTAG_PROOF',
      text: 'Mandatory geo-tagged and timestamped milestone site photographs missing from eSAKSHI portal',
    });
  }

  if (rand() > 0.75) {
    reasons.push({
      code: 'MISSING_TPI_REPORT',
      text: 'Statutory Third-Party Inspection (TPI) report not submitted prior to financial clearance (Para 4.7)',
    });
  }

  if (rand() > 0.85) {
    reasons.push({
      code: 'MISSING_UC_BILLS',
      text: 'Itemized contractor measurement book (MB) bills and Utilisation Certificates (UC) pending submission',
    });
  }

  if (rand() > 0.90) {
    reasons.push({
      code: 'AGENCY_CONCENTRATION',
      text: 'Implementing agency handles an unusually high share (>40%) of constituency allocations',
    });
  }

  if (reasons.length === 0) {
    reasons.push({
      code: 'WITHIN_NORMAL_RANGE',
      text: 'No individual signal crossed statutory threshold; flagged only for routine supervisory audit',
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
  const released = Math.round(sanctioned * (0.35 + rand() * 0.65)); // released <= sanctioned
  // In real PFMS accounting, expenditure never exceeds released or sanctioned
  const expenditure = Math.min(released, Math.round(released * (0.15 + rand() * 0.80)));
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

  const reasons = buildReasons(rand, spendProgressGap, delayDays, utilization, progressPct, expenditure);
  const hasCriticalFlag = reasons.some(r => r.code === 'GHOST_PROJECT_RISK' || r.code === 'MISSING_TPI_REPORT' || r.code === 'MISSING_GEOTAG_PROOF');

  let riskScore = Math.round(
    spendProgressGap * 0.45 +
      Math.min(delayDays / 3.5, 35) +
      (utilization < 25 ? 18 : 0) +
      (hasCriticalFlag ? 20 : 0) +
      rand() * 12
  );
  riskScore = Math.max(5, Math.min(98, riskScore));

  const coords = DISTRICT_COORDS[district] || [22.9734, 78.6569];
  const jitter = () => (rand() - 0.5) * 0.6;

  const missingFlags = [];
  if (reasons.some(r => r.code === 'MISSING_GEOTAG_PROOF')) missingFlags.push('Missing geo-tagged site photographs on eSAKSHI');
  if (reasons.some(r => r.code === 'MISSING_TPI_REPORT')) missingFlags.push('Third-Party Inspection (TPI) report not uploaded');
  if (reasons.some(r => r.code === 'MISSING_UC_BILLS')) missingFlags.push('Itemized contractor bills & UC unverified');
  if (missingFlags.length === 0 && rand() > 0.7) missingFlags.push('Missing actual-completion audit signoff');

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
    reasons,
    dataQuality: {
      completeness: Math.round(75 + rand() * 25),
      lastUpdated: new Date(today.getTime() - Math.floor(rand() * 20) * 86400000)
        .toISOString()
        .slice(0, 10),
      flags: missingFlags,
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
