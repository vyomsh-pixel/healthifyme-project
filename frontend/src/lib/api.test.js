import { describe, it, expect } from "vitest";
import { normalizeErrorMessage } from "./api";

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
