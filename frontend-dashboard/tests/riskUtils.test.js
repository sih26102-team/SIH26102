import { describe, it, expect } from 'vitest';
import { levelFromScore, recommendedAction } from '../src/utils/riskUtils';

describe('levelFromScore', () => {
  it('classifies scores at and above 70 as HIGH', () => {
    expect(levelFromScore(70)).toBe('HIGH');
    expect(levelFromScore(95)).toBe('HIGH');
  });

  it('classifies scores between 40 and 69 as MEDIUM', () => {
    expect(levelFromScore(40)).toBe('MEDIUM');
    expect(levelFromScore(69)).toBe('MEDIUM');
  });

  it('classifies scores below 40 as LOW', () => {
    expect(levelFromScore(0)).toBe('LOW');
    expect(levelFromScore(39)).toBe('LOW');
  });
});

describe('recommendedAction', () => {
  it('recommends prioritized verification for HIGH risk', () => {
    expect(recommendedAction('HIGH')).toMatch(/prioritize/i);
  });

  it('recommends monitoring for LOW risk', () => {
    expect(recommendedAction('LOW')).toMatch(/monitor/i);
  });
});
