const MESSAGES = {
  es: {
    duffelUnauthorized:
      "Duffel rechazó las credenciales (401). Revisá que DUFFEL_API_TOKEN sea un token live válido y que la cuenta esté activada.",
    duffelMissingToken: "Falta DUFFEL_API_TOKEN en el backend. Sin token live no hay inventario real.",
    amadeusMissing: "Faltan credenciales de Amadeus (AMADEUS_API_KEY / AMADEUS_API_SECRET).",
    unauthorized: "{provider} rechazó las credenciales. Revisá la configuración del proveedor.",
    missingCredentials: "Faltan credenciales para {provider}.",
    forbidden: "{provider} denegó el acceso (403).",
    timeout: "{provider} no respondió a tiempo. Probá de nuevo en unos minutos.",
    rateLimited: "{provider} limitó las consultas (429). Esperá un momento.",
    network: "No hubo conexión estable con {provider}.",
    generic: "No pudimos consultar {provider}. Revisá la configuración del backend.",
  },
  en: {
    duffelUnauthorized:
      "Duffel rejected the credentials (401). Check that DUFFEL_API_TOKEN is a valid live token and the account is activated.",
    duffelMissingToken: "DUFFEL_API_TOKEN is missing on the backend. Without a live token there is no real inventory.",
    amadeusMissing: "Amadeus credentials are missing (AMADEUS_API_KEY / AMADEUS_API_SECRET).",
    unauthorized: "{provider} rejected the credentials. Check the provider configuration.",
    missingCredentials: "Credentials for {provider} are missing.",
    forbidden: "{provider} denied access (403).",
    timeout: "{provider} timed out. Try again in a few minutes.",
    rateLimited: "{provider} rate-limited requests (429). Wait a moment.",
    network: "Could not reach {provider} reliably.",
    generic: "We could not query {provider}. Check the backend configuration.",
  },
} as const;

type Locale = keyof typeof MESSAGES;

function providerFromText(text: string): string {
  const match = text.match(/^([a-z]+)\s+search failed:/i);
  if (match) {
    return match[1].charAt(0).toUpperCase() + match[1].slice(1);
  }
  return "Proveedor";
}

export function formatProviderError(
  raw: string | null | undefined,
  locale: Locale = "es",
  providerHint?: string,
): string | null {
  if (!raw?.trim()) {
    return null;
  }

  const text = raw.trim();
  const lowered = text.toLowerCase();
  const provider = providerHint ?? providerFromText(text);
  const copy = MESSAGES[locale] ?? MESSAGES.es;

  if (lowered.includes("token is missing") && lowered.includes("duffel")) {
    return copy.duffelMissingToken;
  }
  if (lowered.includes("credentials are missing") && lowered.includes("amadeus")) {
    return copy.amadeusMissing;
  }
  if (lowered.includes("401") || lowered.includes("unauthorized")) {
    if (provider.toLowerCase() === "duffel" || lowered.includes("duffel")) {
      return copy.duffelUnauthorized;
    }
    return copy.unauthorized.replace("{provider}", provider);
  }
  if (lowered.includes("403") || lowered.includes("forbidden")) {
    return copy.forbidden.replace("{provider}", provider);
  }
  if (lowered.includes("timeout") || lowered.includes("timed out")) {
    return copy.timeout.replace("{provider}", provider);
  }
  if (lowered.includes("429") || lowered.includes("rate limit")) {
    return copy.rateLimited.replace("{provider}", provider);
  }
  if (lowered.includes("connection") || lowered.includes("network")) {
    return copy.network.replace("{provider}", provider);
  }

  if (text.length > 160 || lowered.includes("for url") || lowered.includes("client error")) {
    return copy.generic.replace("{provider}", provider);
  }

  return text;
}
