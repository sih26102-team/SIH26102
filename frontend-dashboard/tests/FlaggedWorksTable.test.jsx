import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import FlaggedWorksTable from '../src/components/FlaggedWorksTable';

const sampleProject = {
  projectId: 'MPL-AP-1001',
  implementingAgency: 'District Rural Development Agency',
  district: 'Nellore',
  state: 'Andhra Pradesh',
  category: 'Road Connectivity',
  sanctionedAmount: 1200000,
  utilizationPct: 40,
  progressPct: 20,
  delayDays: 45,
  status: 'Delayed',
  riskScore: 82,
  riskLevel: 'HIGH',
  dataQuality: { completeness: 92, flags: [] },
};

function renderTable(props) {
  return render(
    <MemoryRouter>
      <FlaggedWorksTable projects={[]} loading={false} error={null} {...props} />
    </MemoryRouter>
  );
}

describe('FlaggedWorksTable', () => {
  it('shows a loading state', () => {
    renderTable({ loading: true });
    expect(screen.getByText(/loading flagged works/i)).toBeInTheDocument();
  });

  it('shows an error state', () => {
    renderTable({ error: 'Network error' });
    expect(screen.getByText(/couldn't load flagged works/i)).toBeInTheDocument();
    expect(screen.getByText('Network error')).toBeInTheDocument();
  });

  it('shows an empty state when there are no matching projects', () => {
    renderTable({ projects: [] });
    expect(screen.getByText(/no projects match these filters/i)).toBeInTheDocument();
  });

  it('renders a row per project with its risk score and never claims proven fraud', () => {
    renderTable({ projects: [sampleProject] });
    expect(screen.getByText('MPL-AP-1001')).toBeInTheDocument();
    expect(screen.getByText('Nellore')).toBeInTheDocument();
    expect(screen.queryByText(/fraud detected/i)).not.toBeInTheDocument();
  });
});
