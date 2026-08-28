export function formatSeverity(
  severity: string,
): string {
  const labels: Record<string, string> = {
    critical: "Crítica",
    high: "Alta",
    medium: "Media",
    low: "Baja",
    info: "Información",
  }

  return labels[severity] ?? severity
}

export function formatConfidence(
  confidence: string | null,
): string {
  if (!confidence) {
    return "No disponible"
  }

  const labels: Record<string, string> = {
    high: "Alta",
    medium: "Media",
    low: "Baja",
  }

  return labels[confidence] ?? confidence
}