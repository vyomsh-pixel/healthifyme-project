import { describe, it, expect } from "vitest";
import { normalizeErrorMessage, formatDate } from "./api";
import { getBMIStatus } from "./bmi";

describe("normalizeErrorMessage", () => {
  it("returns string details directly", () => {
    expect(normalizeErrorMessage("bad request")).toBe("bad request");
  });

  it("extracts nested detail objects", () => {
    expect(normalizeErrorMessage({ detail: { message: "token expired" } })).toBe("token expired");
  });

  it("joins detail arrays", () => {
    expect(normalizeErrorMessage({ detail: [{ msg: "one" }, { message: "two" }] })).toBe("one • two");
  });
});

describe("formatDate", () => {
  it("returns fallback for empty or invalid values", () => {
    expect(formatDate(null)).toBe("—");
    expect(formatDate("", "Not yet")).toBe("Not yet");
    expect(formatDate("not-a-date", "—")).toBe("—");
  });

  it("normalizes SQLite space-separated timestamps without Invalid Date", () => {
    const formatted = formatDate("2026-10-11 08:30:00");
    expect(formatted).not.toBe("—");
    expect(formatted).not.toContain("Invalid Date");
    expect(formatted).toContain("2026");
  });

  it("formats ISO-8601 Z and timezone offset strings cleanly", () => {
    expect(formatDate("2026-10-11T08:30:00Z")).toContain("2026");
    expect(formatDate("2026-10-11T14:00:00+05:30")).toContain("2026");
  });
});

describe("getBMIStatus non-clinical labels", () => {
  it("maps BMI categories to neutral self-tracking phrasing", () => {
    expect(getBMIStatus("Well below usual range")).toEqual({
      color: "red",
      label: "Attention Needed",
    });
    expect(getBMIStatus("Below usual range")).toEqual({
      color: "amber",
      label: "Outside Typical Range",
    });
    expect(getBMIStatus("Within usual range")).toEqual({
      color: "green",
      label: "Within Typical Range",
    });
    expect(getBMIStatus("Above usual range")).toEqual({
      color: "amber",
      label: "Outside Typical Range",
    });
    expect(getBMIStatus("Higher than usual range")).toEqual({
      color: "red",
      label: "Attention Needed",
    });
    expect(getBMIStatus(null)).toBeNull();
  });
});
