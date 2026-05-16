import { AppLocale } from "./config";

export interface AppDictionary {
  header: {
    eyebrow: string;
    title: string;
    description: string;
    languageLabel: string;
    localeNames: Record<AppLocale, string>;
  };
  home: {
    hero: {
      eyebrow: string;
      title: string;
      description: string;
      optimizeLabel: string;
      optimizeValue: string;
      highlights: string[];
    };
    mvp: {
      eyebrow: string;
      title: string;
      subtitle: string;
      items: string[];
    };
  };
  searchForm: {
    eyebrow: string;
    title: string;
    subtitle: string;
    fields: {
      origin: string;
      destination: string;
      departureDate: string;
      returnDate: string;
      flexibleDays: string;
      budgetUsd: string;
      passengers: string;
      cabinClass: string;
      nationality: string;
      residenceCountry: string;
      riskTolerance: string;
      preferredStrategy: string;
      validVisas: string;
      maxStops: string;
      loyaltyProgram: string;
      loyaltyBalance: string;
      loyaltyBank: string;
      transferPartners: string;
      notes: string;
      email: string;
      displayName: string;
    };
    placeholders: {
      validVisas: string;
      loyaltyProgram: string;
      loyaltyBank: string;
      transferPartners: string;
      notes: string;
    };
    options: {
      cabinClass: Record<"ECONOMY" | "PREMIUM_ECONOMY" | "BUSINESS" | "FIRST", string>;
      riskTolerance: Record<"low" | "medium" | "high", string>;
      preferredStrategy: Record<"savings" | "balanced" | "comfort" | "experience" | "miles", string>;
    };
    toggles: {
      checkedBagRequired: string;
      stopoverInterest: string;
    };
    footer: string;
    submitIdle: string;
    submitLoading: string;
    errorFallback: string;
  };
  searchResult: {
    eyebrowPrefix: string;
    title: string;
    subtitle: string;
    newSearch: string;
    adjustContext: string;
    assumptionsTitle: string;
    assumptionsEmpty: string;
    confidenceLabel: string;
    confidenceValues: Record<"low" | "medium" | "high", string>;
    scopeLabels: Record<string, string>;
  };
  strategyCard: {
    recommended: string;
    metrics: {
      price: string;
      duration: string;
      stops: string;
      flexibility: string;
      score: string;
      route: string;
    };
    scoreLabels: Record<string, string>;
    actions: {
      showDetails: string;
      hideDetails: string;
      save: string;
      saved: string;
    };
    externalSearch: {
      openGoogleFlights: string;
      disclaimer: string;
    };
    sections: {
      tradeoffs: string;
      tradeoffsEmpty: string;
      opportunities: string;
      opportunitiesEmpty: string;
      migration: string;
      migrationEmpty: string;
      operationalRisk: string;
      operationalRiskEmpty: string;
      segments: string;
      sliceOutbound: string;
      sliceInbound: string;
      sliceOther: string;
      connectionPrefix: string;
      technicalStopPrefix: string;
      sliceSummaryDirect: string;
      sliceSummaryWithStops: string;
      operatedBy: string;
      longConnectionNote: string;
    };
    segmentSchedule: {
      departLocalLabel: string;
      arriveLocalLabel: string;
      utcReferenceLabel: string;
      departUtc: string;
      arriveUtc: string;
      utcFootnote: string;
    };
    severityLabels: Record<"low" | "medium" | "high", string>;
  };
  feedback: {
    eyebrow: string;
    title: string;
    subtitle: string;
    placeholder: string;
    footer: string;
    submitIdle: string;
    submitLoading: string;
    submitSuccess: string;
  };
  analytics: {
    eyebrow: string;
    title: string;
    subtitle: string;
    unavailable: string;
    metrics: {
      searches: string;
      events: string;
      strategiesOpened: string;
      saves: string;
      feedback: string;
    };
    recentFeedbackTitle: string;
    recentFeedbackEmpty: string;
    providerHealthTitle: string;
    providerHealthEmpty: string;
    lastStatusPrefix: string;
    successRateSuffix: string;
    miniMetrics: {
      attempts: string;
      latencyMs: string;
      offers: string;
    };
    externalIds: {
      requestId: string;
      correlationId: string;
    };
    lastErrorPrefix: string;
    providerStatuses: {
      success: string;
      failed: string;
    };
  };
  notFound: {
    eyebrow: string;
    title: string;
    description: string;
    cta: string;
  };
}

const dictionaries: Record<AppLocale, AppDictionary> = {
  es: {
    header: {
      eyebrow: "Viagest Scout",
      title: "Descubrimiento y estrategia inteligente de vuelos con IA",
      description:
        "Capa de inteligencia de Viagest para descubrir mejores rutas, comparar tradeoffs y transformar opciones complejas en pocas estrategias accionables.",
      languageLabel: "Idioma",
      localeNames: {
        es: "Español",
        en: "Inglés",
      },
    },
    home: {
      hero: {
        eyebrow: "Viagest Scout",
        title: "No muestra 1000 vuelos. Devuelve 3 estrategias inteligentes para decidir mejor.",
        description:
          "Viagest Scout combina precio, tiempo, equipaje, riesgo operativo, millas y restricciones migratorias para sugerir rutas con criterio de strategist humano.",
        optimizeLabel: "Lo que optimiza",
        optimizeValue: "Costo, experiencia, millas y fricción real.",
        highlights: [
          "Visas y conexiones riesgosas",
          "Stopovers con costo marginal bajo",
          "Uso más inteligente de programas loyalty",
        ],
      },
      mvp: {
        eyebrow: "Roadmap implementado",
        title: "Qué ya cubre este MVP",
        subtitle:
          "La arquitectura aterriza todos los sprints del plan en piezas separadas, sin concentrarlo todo en una sola pantalla o archivo.",
        items: [
          "Backend con proveedor desacoplado, normalización, scoring, reglas migratorias y generación de estrategias.",
          "Frontend con intake inteligente, comparación de estrategias, guardado y feedback.",
          "Persistencia local lista para evolucionar a PostgreSQL y proveedor real vía Duffel como base del MVP.",
        ],
      },
    },
    searchForm: {
      eyebrow: "Sprint 1 + 2",
      title: "Captura de contexto del viajero",
      subtitle:
        "La búsqueda ya entra con preferencias, restricciones, equipaje y perfil loyalty. Eso permite ranquear con criterio en vez de solo listar vuelos.",
      fields: {
        origin: "Origen",
        destination: "Destino",
        departureDate: "Salida",
        returnDate: "Regreso",
        flexibleDays: "Flexibilidad (días)",
        budgetUsd: "Presupuesto USD",
        passengers: "Pasajeros",
        cabinClass: "Cabina",
        nationality: "Nacionalidad",
        residenceCountry: "Residencia",
        riskTolerance: "Riesgo tolerado",
        preferredStrategy: "Estrategia preferida",
        validVisas: "Visas vigentes o autorizaciones",
        maxStops: "Máximo de escalas",
        loyaltyProgram: "Programa de millas",
        loyaltyBalance: "Saldo de millas / puntos",
        loyaltyBank: "Banco o tarjeta principal",
        transferPartners: "Transfer partners",
        notes: "Contexto adicional",
        email: "Email (opcional)",
        displayName: "Nombre (opcional)",
      },
      placeholders: {
        validVisas: "US, CANADA, ESTA",
        loyaltyProgram: "Smiles, LATAM Pass, Iberia Plus",
        loyaltyBank: "Santander, Itaú, BBVA",
        transferPartners: "Gol, Air France, Iberia",
        notes: "Ejemplo: prefiero evitar Canadá, quiero equipaje incluido y no me molesta una escala larga si suma un destino.",
      },
      options: {
        cabinClass: {
          ECONOMY: "Economy",
          PREMIUM_ECONOMY: "Premium economy",
          BUSINESS: "Business",
          FIRST: "First",
        },
        riskTolerance: {
          low: "Bajo",
          medium: "Medio",
          high: "Alto",
        },
        preferredStrategy: {
          savings: "Ahorro",
          balanced: "Balanceada",
          comfort: "Comodidad",
          experience: "Experiencia",
          miles: "Millas",
        },
      },
      toggles: {
        checkedBagRequired: "Necesito equipaje despachado incluido.",
        stopoverInterest: "Estoy abierto a stopovers si el costo marginal es razonable.",
      },
      footer:
        "El backend persiste el contexto del viajero, consulta proveedor de vuelos, normaliza itinerarios y devuelve tres estrategias con scoring, explicación y flags de riesgo.",
      submitIdle: "Generar 3 estrategias",
      submitLoading: "Analizando viaje...",
      errorFallback: "No se pudo generar la estrategia.",
    },
    searchResult: {
      eyebrowPrefix: "Proveedor activo:",
      title: "Resumen ejecutivo",
      subtitle: "El motor ya ranqueó itinerarios, aplicó reglas y transformó el inventario en estrategias explicadas.",
      newSearch: "Nueva búsqueda",
      adjustContext: "Ajustar contexto",
      assumptionsTitle: "Supuestos y cobertura",
      assumptionsEmpty: "No hizo falta declarar supuestos especiales para esta búsqueda.",
      confidenceLabel: "confianza",
      confidenceValues: {
        low: "baja",
        medium: "media",
        high: "alta",
      },
      scopeLabels: {
        provider: "proveedor",
        migration: "migración",
      },
    },
    strategyCard: {
      recommended: "Recomendada",
      metrics: {
        price: "Precio",
        duration: "Tiempo en ruta (ida+vuelta)",
        stops: "Escalas",
        flexibility: "Flexibilidad",
        score: "Score",
        route: "Ruta",
      },
      scoreLabels: {
        price: "Precio",
        duration: "Duración",
        convenience: "Conveniencia",
        flexibility: "Flexibilidad",
        experience: "Experiencia",
        miles: "Millas",
        migration: "Migración",
        risk: "Riesgo",
      },
      actions: {
        showDetails: "Ver detalle",
        hideDetails: "Ocultar detalle",
        save: "Guardar estrategia",
        saved: "Guardada",
      },
      externalSearch: {
        openGoogleFlights: "Buscar ruta en Google Flights",
        disclaimer:
          "Enlace externo solo para orientarte: no reproducimos la misma tarifa ni la disponibilidad del proveedor de esta estrategia.",
      },
      sections: {
        tradeoffs: "Tradeoffs",
        tradeoffsEmpty: "No hay tradeoffs relevantes detectados.",
        opportunities: "Oportunidades detectadas",
        opportunitiesEmpty: "No surgió una oportunidad oculta dominante en esta opción.",
        migration: "Restricciones migratorias",
        migrationEmpty: "No se detectó una restricción migratoria dominante con las reglas soportadas.",
        operationalRisk: "Riesgo operativo",
        operationalRiskEmpty: "No se detectaron flags operativos fuertes en esta alternativa.",
        segments: "Vuelos y conexiones",
        sliceOutbound: "Ida",
        sliceInbound: "Vuelta",
        sliceOther: "Pierna {n}",
        connectionPrefix: "Conexión",
        technicalStopPrefix: "Escala",
        sliceSummaryDirect: "{duration} · directo",
        sliceSummaryWithStops: "{duration} · {count} escalas · {airports}",
        operatedBy: "Operado por {carrier}",
        longConnectionNote: " · conexión larga",
      },
      segmentSchedule: {
        departLocalLabel: "Salida · hora local en {code}",
        arriveLocalLabel: "Llegada · hora local en {code}",
        utcReferenceLabel: "UTC",
        departUtc: "Salida (UTC)",
        arriveUtc: "Llegada (UTC)",
        utcFootnote:
          "La hora local usa la zona horaria del aeropuerto (catálogo IATA→IANA). Debajo se muestra UTC como referencia fija. Si no hay zona para ese código IATA, solo verás la línea en UTC.",
      },
      severityLabels: {
        low: "Bajo",
        medium: "Medio",
        high: "Alto",
      },
    },
    feedback: {
      eyebrow: "Sprint 6",
      title: "Capturar feedback",
      subtitle: "El MVP ya persiste comentarios y deja una traza de uso para la beta cerrada.",
      placeholder: "Ejemplo: me sorprendió el stopover en Lisboa, pero me gustaría ver hotel o reglas de visa más detalladas.",
      footer: "El evento queda disponible en el panel de telemetría para medir valor percibido.",
      submitIdle: "Enviar feedback",
      submitLoading: "Enviando...",
      submitSuccess: "Feedback enviado",
    },
    analytics: {
      eyebrow: "Sprint 6",
      title: "Telemetría beta",
      subtitle: "Panel inicial para ver si el MVP genera interacción, guardados y feedback real.",
      unavailable: "No se pudo cargar el resumen de analytics todavía. Levantá el backend y generá una búsqueda para poblar el panel.",
      metrics: {
        searches: "Búsquedas",
        events: "Eventos",
        strategiesOpened: "Estrategias abiertas",
        saves: "Guardados",
        feedback: "Feedback",
      },
      recentFeedbackTitle: "Feedback reciente",
      recentFeedbackEmpty: "Todavía no hay feedback capturado. La app ya expone el endpoint para comenzar una beta cerrada.",
      providerHealthTitle: "Salud de proveedores",
      providerHealthEmpty: "Todavía no hay suficientes eventos de proveedores para mostrar salud agregada.",
      lastStatusPrefix: "último estado:",
      successRateSuffix: "% éxito",
      miniMetrics: {
        attempts: "Intentos",
        latencyMs: "Latencia ms",
        offers: "Offers",
      },
      externalIds: {
        requestId: "Request ID",
        correlationId: "Correlation ID",
      },
      lastErrorPrefix: "Último error:",
      providerStatuses: {
        success: "exitoso",
        failed: "fallido",
      },
    },
    notFound: {
      eyebrow: "Búsqueda no encontrada",
      title: "No pudimos recuperar esa estrategia",
      description: "Puede que el backend no esté corriendo o que el identificador de búsqueda ya no exista en la base local.",
      cta: "Volver al planner",
    },
  },
  en: {
    header: {
      eyebrow: "Viagest Scout",
      title: "AI-powered flight discovery and strategy",
      description:
        "Viagest's intelligence layer to uncover better routes, compare tradeoffs, and turn complex options into a few actionable strategies.",
      languageLabel: "Language",
      localeNames: {
        es: "Spanish",
        en: "English",
      },
    },
    home: {
      hero: {
        eyebrow: "Viagest Scout",
        title: "It does not show 1,000 flights. It returns 3 smart strategies so you can decide faster.",
        description:
          "Viagest Scout combines price, time, baggage, operational risk, miles, and immigration constraints to suggest routes with a senior travel strategist mindset.",
        optimizeLabel: "What it optimizes",
        optimizeValue: "Cost, experience, miles, and real-world friction.",
        highlights: [
          "Visas and risky connections",
          "Low-marginal-cost stopovers",
          "Smarter use of loyalty programs",
        ],
      },
      mvp: {
        eyebrow: "Roadmap delivered",
        title: "What this MVP already covers",
        subtitle:
          "The architecture lands every sprint from the plan into separate pieces instead of concentrating everything into one screen or file.",
        items: [
          "Backend with a decoupled provider layer, normalization, scoring, migration rules, and strategy generation.",
          "Frontend with smart intake, strategy comparison, save actions, and feedback.",
          "Local persistence ready to evolve to PostgreSQL and a live Duffel provider as the MVP baseline.",
        ],
      },
    },
    searchForm: {
      eyebrow: "Sprint 1 + 2",
      title: "Traveler context intake",
      subtitle:
        "The search already includes preferences, restrictions, baggage, and loyalty profile so ranking can be strategic instead of just listing flights.",
      fields: {
        origin: "Origin",
        destination: "Destination",
        departureDate: "Departure",
        returnDate: "Return",
        flexibleDays: "Flexibility (days)",
        budgetUsd: "Budget USD",
        passengers: "Passengers",
        cabinClass: "Cabin",
        nationality: "Nationality",
        residenceCountry: "Residence",
        riskTolerance: "Risk tolerance",
        preferredStrategy: "Preferred strategy",
        validVisas: "Valid visas or authorizations",
        maxStops: "Maximum stops",
        loyaltyProgram: "Loyalty program",
        loyaltyBalance: "Miles / points balance",
        loyaltyBank: "Main bank or card",
        transferPartners: "Transfer partners",
        notes: "Additional context",
        email: "Email (optional)",
        displayName: "Name (optional)",
      },
      placeholders: {
        validVisas: "US, CANADA, ESTA",
        loyaltyProgram: "Smiles, LATAM Pass, Iberia Plus",
        loyaltyBank: "Santander, Itau, BBVA",
        transferPartners: "Gol, Air France, Iberia",
        notes: "Example: I'd rather avoid Canada, I want checked baggage included, and I don't mind a long stop if it adds another destination.",
      },
      options: {
        cabinClass: {
          ECONOMY: "Economy",
          PREMIUM_ECONOMY: "Premium economy",
          BUSINESS: "Business",
          FIRST: "First",
        },
        riskTolerance: {
          low: "Low",
          medium: "Medium",
          high: "High",
        },
        preferredStrategy: {
          savings: "Savings",
          balanced: "Balanced",
          comfort: "Comfort",
          experience: "Experience",
          miles: "Miles",
        },
      },
      toggles: {
        checkedBagRequired: "I need checked baggage included.",
        stopoverInterest: "I am open to stopovers if the marginal cost is reasonable.",
      },
      footer:
        "The backend persists traveler context, queries flight providers, normalizes itineraries, and returns three strategies with scoring, explanations, and risk flags.",
      submitIdle: "Generate 3 strategies",
      submitLoading: "Analyzing trip...",
      errorFallback: "We couldn't generate the strategy.",
    },
    searchResult: {
      eyebrowPrefix: "Active provider:",
      title: "Executive summary",
      subtitle: "The engine already ranked itineraries, applied rules, and turned the inventory into explained strategies.",
      newSearch: "New search",
      adjustContext: "Adjust context",
      assumptionsTitle: "Assumptions and coverage",
      assumptionsEmpty: "No special assumptions were needed for this search.",
      confidenceLabel: "confidence",
      confidenceValues: {
        low: "low",
        medium: "medium",
        high: "high",
      },
      scopeLabels: {
        provider: "provider",
        migration: "migration",
      },
    },
    strategyCard: {
      recommended: "Recommended",
      metrics: {
        price: "Price",
        duration: "Flight time (out + return)",
        stops: "Stops",
        flexibility: "Flexibility",
        score: "Score",
        route: "Route",
      },
      scoreLabels: {
        price: "Price",
        duration: "Duration",
        convenience: "Convenience",
        flexibility: "Flexibility",
        experience: "Experience",
        miles: "Miles",
        migration: "Migration",
        risk: "Risk",
      },
      actions: {
        showDetails: "Show details",
        hideDetails: "Hide details",
        save: "Save strategy",
        saved: "Saved",
      },
      externalSearch: {
        openGoogleFlights: "Search route on Google Flights",
        disclaimer:
          "External link for reference only: it does not reproduce this strategy's fare or availability from our flight provider.",
      },
      sections: {
        tradeoffs: "Tradeoffs",
        tradeoffsEmpty: "No meaningful tradeoffs were detected.",
        opportunities: "Detected opportunities",
        opportunitiesEmpty: "No hidden standout opportunity surfaced in this option.",
        migration: "Migration constraints",
        migrationEmpty: "No dominant migration constraint was detected with the supported rules.",
        operationalRisk: "Operational risk",
        operationalRiskEmpty: "No strong operational flags were detected in this option.",
        segments: "Flights & connections",
        sliceOutbound: "Outbound",
        sliceInbound: "Return",
        sliceOther: "Leg {n}",
        connectionPrefix: "Connection",
        technicalStopPrefix: "Stop",
        sliceSummaryDirect: "{duration} · nonstop",
        sliceSummaryWithStops: "{duration} · {count} stops · {airports}",
        operatedBy: "Operated by {carrier}",
        longConnectionNote: " · long connection",
      },
      segmentSchedule: {
        departLocalLabel: "Departure · local time at {code}",
        arriveLocalLabel: "Arrival · local time at {code}",
        utcReferenceLabel: "UTC",
        departUtc: "Departure (UTC)",
        arriveUtc: "Arrival (UTC)",
        utcFootnote:
          "Local time uses the airport time zone (IATA→IANA catalog). UTC is shown below as a fixed reference. If there is no zone for that IATA code, only the UTC line appears.",
      },
      severityLabels: {
        low: "Low",
        medium: "Medium",
        high: "High",
      },
    },
    feedback: {
      eyebrow: "Sprint 6",
      title: "Capture feedback",
      subtitle: "The MVP already persists comments and leaves a usage trace for the closed beta.",
      placeholder: "Example: the Lisbon stopover surprised me, but I'd like to see hotel options or more detailed visa rules.",
      footer: "The event becomes available in the telemetry panel to measure perceived value.",
      submitIdle: "Send feedback",
      submitLoading: "Sending...",
      submitSuccess: "Feedback sent",
    },
    analytics: {
      eyebrow: "Sprint 6",
      title: "Beta telemetry",
      subtitle: "Initial panel to see whether the MVP is generating engagement, saves, and real feedback.",
      unavailable: "We couldn't load the analytics summary yet. Start the backend and generate a search to populate the panel.",
      metrics: {
        searches: "Searches",
        events: "Events",
        strategiesOpened: "Strategies opened",
        saves: "Saves",
        feedback: "Feedback",
      },
      recentFeedbackTitle: "Recent feedback",
      recentFeedbackEmpty: "No feedback has been captured yet. The app already exposes the endpoint to start a closed beta.",
      providerHealthTitle: "Provider health",
      providerHealthEmpty: "There are not enough provider events yet to show aggregated health.",
      lastStatusPrefix: "last status:",
      successRateSuffix: "% success",
      miniMetrics: {
        attempts: "Attempts",
        latencyMs: "Latency ms",
        offers: "Offers",
      },
      externalIds: {
        requestId: "Request ID",
        correlationId: "Correlation ID",
      },
      lastErrorPrefix: "Last error:",
      providerStatuses: {
        success: "successful",
        failed: "failed",
      },
    },
    notFound: {
      eyebrow: "Search not found",
      title: "We couldn't recover that strategy",
      description: "The backend may not be running, or the search identifier may no longer exist in the local database.",
      cta: "Back to planner",
    },
  },
};

export function getDictionary(locale: AppLocale): AppDictionary {
  return dictionaries[locale];
}
