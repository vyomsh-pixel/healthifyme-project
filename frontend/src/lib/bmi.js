export function getBMIStatus(category) {
  if (!category) return null;
  const cat = category.toLowerCase();
  if (cat.includes("well below")) return { color: "red", label: "Attention Needed" };
  if (cat.includes("below")) return { color: "amber", label: "Outside Typical Range" };
  if (cat.includes("usual") && !cat.includes("above") && !cat.includes("higher")) return { color: "green", label: "Within Typical Range" };
  if (cat.includes("above")) return { color: "amber", label: "Outside Typical Range" };
  if (cat.includes("higher")) return { color: "red", label: "Attention Needed" };
  return null;
}
