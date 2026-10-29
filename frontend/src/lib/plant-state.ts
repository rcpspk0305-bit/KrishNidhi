/** SQLite returns UTC datetimes without an offset. Preserve UTC on every client. */
export function utcTimestamp(value?: string | null): number {
  if (!value) return Number.NaN;
  const withZone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(value) ? value : `${value}Z`;
  return Date.parse(withZone);
}

export function isFresh(
  value: string | null | undefined,
  now: number,
  maxAge = 30_000,
): boolean {
  const timestamp = utcTimestamp(value);
  return (
    Number.isFinite(timestamp) &&
    now > 0 &&
    timestamp <= now + 5000 &&
    now - timestamp <= maxAge
  );
}

/** Merge persisted samples with live samples without losing either during a poll. */
export function mergeHistory<T extends { timestamp: string }>(stored: T[], live: T[]): T[] {
  const samples = new Map<number, T>();
  for (const sample of [...stored, ...live]) {
    const timestamp = utcTimestamp(sample.timestamp);
    if (Number.isFinite(timestamp)) samples.set(timestamp, sample);
  }
  return [...samples.entries()].sort(([a], [b]) => a - b).slice(-500).map(([, sample]) => sample);
}
