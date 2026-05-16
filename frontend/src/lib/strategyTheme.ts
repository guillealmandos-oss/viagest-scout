import type { Strategy } from "@/types/travel";

export type StrategyType = Strategy["strategy_type"];

export interface StrategyThemeTokens {
  borderClass: string;
  badgeClass: string;
  accent: string;
  muted: string;
  border: string;
  text: string;
}

export const strategyTheme: Record<StrategyType, StrategyThemeTokens> = {
  savings: {
    borderClass: "strategy-savings",
    badgeClass: "badge-savings",
    accent: "var(--strategy-savings-accent)",
    muted: "var(--strategy-savings-muted)",
    border: "var(--strategy-savings-border)",
    text: "var(--strategy-savings-text)",
  },
  experience: {
    borderClass: "strategy-experience",
    badgeClass: "badge-experience",
    accent: "var(--strategy-experience-accent)",
    muted: "var(--strategy-experience-muted)",
    border: "var(--strategy-experience-border)",
    text: "var(--strategy-experience-text)",
  },
  miles: {
    borderClass: "strategy-miles",
    badgeClass: "badge-miles",
    accent: "var(--strategy-miles-accent)",
    muted: "var(--strategy-miles-muted)",
    border: "var(--strategy-miles-border)",
    text: "var(--strategy-miles-text)",
  },
};
