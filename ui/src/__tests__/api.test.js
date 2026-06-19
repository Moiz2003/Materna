/**
 * ui/src/__tests__/api.test.js — T11: Frontend API client tests.
 * Mocks fetch; verifies endpoint URLs, method, error handling.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// We need to re-import api after mocking
let api;
beforeEach(async () => {
  vi.resetModules();
  mockFetch.mockReset();
  // Re-import fresh after reset
  api = await import('../api');
});

describe('getCase', () => {
  it('calls GET /cases/{id}', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ case_id: 'C-0001', status: 'RECEIVED' }) });
    await api.getCase('C-0001');
    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toContain('/cases/C-0001');
    expect(opts.method || 'GET').toBe('GET');
  });

  it('throws on non-200', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 404, json: () => Promise.resolve({ detail: 'Not found' }) });
    await expect(api.getCase('NONEXISTENT')).rejects.toThrow('Not found');
  });
});

describe('submitDecision', () => {
  it('calls POST /cases/{id}/decision with body', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ verdict: 'approve' }) });
    await api.submitDecision('C-0001', { verdict: 'approve', note: 'Looks good', reviewer: 'Dr. Test' });
    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toContain('/cases/C-0001/decision');
    expect(opts.method).toBe('POST');
    const body = JSON.parse(opts.body);
    expect(body.verdict).toBe('approve');
  });
});

describe('getPacketUrl', () => {
  it('returns correct URL', () => {
    const url = api.getPacketUrl('C-0001');
    expect(url).toContain('/cases/C-0001/packet');
  });
});

describe('getAudit', () => {
  it('calls GET /cases/{id}/audit', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ verified: true, entries: [] }) });
    await api.getAudit('C-0001');
    expect(mockFetch).toHaveBeenCalledTimes(1);
    expect(mockFetch.mock.calls[0][0]).toContain('/cases/C-0001/audit');
  });
});

describe('getRoom', () => {
  it('calls GET /cases/{id}/room', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ messages: [] }) });
    await api.getRoom('C-0001');
    expect(mockFetch).toHaveBeenCalledTimes(1);
    expect(mockFetch.mock.calls[0][0]).toContain('/cases/C-0001/room');
  });
});
