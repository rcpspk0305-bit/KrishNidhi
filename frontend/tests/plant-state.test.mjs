import test from "node:test";
import assert from "node:assert/strict";
import { isFresh, mergeHistory, utcTimestamp } from "../src/lib/plant-state.ts";

test("SQLite timestamps are UTC, including on an India-local client", () => {
  process.env.TZ = "Asia/Kolkata";
  assert.equal(
    utcTimestamp("2026-10-28T10:30:00"),
    Date.parse("2026-10-28T10:30:00Z"),
  );
  assert.equal(
    utcTimestamp("2026-10-28T16:00:00+05:30"),
    Date.parse("2026-10-28T10:30:00Z"),
  );
});

test("freshness rejects stale, missing, invalid, and implausibly future readings", () => {
  const now = Date.parse("2026-10-28T10:30:30Z");
  assert.equal(isFresh("2026-10-28T10:30:00", now), true);
  assert.equal(isFresh("2026-10-28T10:29:59Z", now), false);
  assert.equal(isFresh("2026-10-28T10:31:30Z", now), false);
  assert.equal(isFresh(null, now), false);
  assert.equal(isFresh("invalid", now), false);
  assert.equal(isFresh("2026-10-28T10:30:00Z", 0), false);
});

test("a slow historical response keeps older records and newer SSE samples", () => {
  const stored = [{ timestamp: "2026-10-28T10:00:00", value: 20 }, { timestamp: "2026-10-28T10:30:00Z", value: 26 }];
  const live = [{ timestamp: "2026-10-28T10:30:00Z", value: 27 }, { timestamp: "2026-10-28T10:30:01Z", value: 31 }];
  assert.deepEqual(mergeHistory(stored, live).map((sample) => sample.value), [20, 27, 31]);
  assert.equal(mergeHistory([], live).length, 2);
  assert.equal(mergeHistory(stored, []).length, 2);
});
