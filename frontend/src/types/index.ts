export interface Dataset {
  id: number;
  name: string;
  filename: string;
  uploaded_at: string;
  row_count: number;
  columns: string[];
  description?: string;
}

export interface UploadResponse {
  dataset_id: number;
  name: string;
  row_count: number;
  columns: string[];
  preview: Record<string, unknown>[];
}

export interface AnalysisResponse {
  dataset_id: number;
  dataset_name: string;
  summary: {
    periods: string[];
    categories: string[];
    line_item_count: number;
    total_by_period: Record<string, number>;
  };
  ratios: Record<string, number | string>;
  trends: Trend[];
  anomalies: Anomaly[];
  period_comparison: PeriodComparison;
}

export interface Trend {
  line_item: string;
  category: string;
  values_by_period: Record<string, number>;
  period_changes: { from: string; to: string; change_pct: number | null }[];
  avg_change_pct: number;
  direction: "increasing" | "decreasing" | "stable";
}

export interface Anomaly {
  line_item: string;
  category: string;
  period: string;
  amount: number;
  mean: number;
  std_dev: number;
  z_score: number;
  severity: "high" | "medium";
  description: string;
}

export interface PeriodComparison {
  period_1: string;
  period_2: string;
  items: {
    line_item: string;
    period_1_value: number;
    period_2_value: number;
    absolute_change: number;
    percent_change: number | null;
  }[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  message: string;
  timestamp?: string;
  tools_used?: string[];
}
