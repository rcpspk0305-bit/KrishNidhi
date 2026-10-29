import test from "node:test";
import assert from "node:assert/strict";
import {
  isLocale,
  messages,
  normalizeMessage,
  translate,
} from "../src/lib/i18n.ts";

test("every catalog entry has Telugu and Hindi text", () => {
  for (const [source, translations] of Object.entries(messages)) {
    assert.equal(translations.length, 2, source);
    assert.ok(translations[0].trim(), source);
    assert.ok(translations[1].trim(), source);
    const slots = (value) =>
      [...value.matchAll(/\{\d+\}/g)].map((match) => match[0]).sort();
    assert.deepEqual(slots(translations[0]), slots(source), source);
    assert.deepEqual(slots(translations[1]), slots(source), source);
  }
});

test("English remains unchanged and all supported languages are recognized", () => {
  assert.equal(translate("Temperature", "en"), "Temperature");
  assert.equal(translate("Temperature", "te"), "ఉష్ణోగ్రత");
  assert.equal(translate("Temperature", "hi"), "तापमान");
  assert.equal(isLocale("te"), true);
  assert.equal(isLocale("hi"), true);
  assert.equal(isLocale("invalid"), false);
});

test("dynamic state text translates without changing protocol values or quantities", () => {
  assert.equal(translate("12s ago", "te"), "12 సెకన్ల క్రితం");
  assert.equal(
    translate("Switching operating mode to MANUAL", "hi"),
    "मोड मैनुअल में बदल रहा है",
  );
  assert.equal(translate("31.2°C (warm)", "hi"), "31.2°C (गर्म)");
  assert.equal(translate("esp8266-plant-01", "te"), "esp8266-plant-01");
  assert.equal(
    normalizeMessage("Smart Plant &amp; Irrigation Station"),
    "Smart Plant & Irrigation Station",
  );
});
