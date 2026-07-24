export function getBMIStatus(category) {
  if (!category) return null;
  const cat = category.toLowerCase();
  if (cat.includes("well below")) return { color: "red", label: "High Risk" };
  if (cat.includes("below")) return { color: "amber", label: "Moderate Risk" };
  if (cat.includes("usual")) return { color: "green", label: "Low Risk" };
  if (cat.includes("above")) return { color: "amber", label: "Moderate Risk" };
  if (cat.includes("higher")) return { color: "red", label: "High Risk" };
  return null;
}
