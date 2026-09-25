const scenarioFamilies = [
  "NOC provided · clean intake",
  "NOC not provided · record found",
  "NOC not provided · record missing",
  "NOC provided · GC conflict",
  "Bond provided · clean intake",
  "Bond not provided · record found",
  "Bond not provided · record missing",
  "Bond provided · GC conflict",
  "Complete job address",
  "Incomplete job address",
  "Customer address mismatch",
  "GC provided · clean intake",
  "GC not provided",
  "Subcontractor only",
  "Direct owner mislabeled as GC",
  "Direct owner · correct role",
  "NOC provided · no GC",
  "Bond provided · no GC",
  "NOC and address missing",
  "Owner-builder role unclear",
];

export const requestQueue = scenarioFamilies.flatMap((scenario, familyIndex) =>
  Array.from({ length: 5 }, (_, variantIndex) => {
    const number = 121 + familyIndex * 5 + variantIndex;
    return {
      id: `SYN-WO-${String(number).padStart(6, "0")}`,
      scenario,
      variant: variantIndex + 1,
    };
  }),
);
