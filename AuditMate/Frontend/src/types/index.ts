/* Frontend types */

export type SourceType = "pr" | "code_snippet" | "code_flow" | "doc" | "screenshot" | "approval" | "commit";
export type Screen = "audit" | "collect" | "preview" | "ask";

export interface AuditPoint {
  id: string;
  text: string;
  category?: string;
}

export interface EvidenceItem {
  id: string;
  type: SourceType;
  summary: string;
  content?: string;
  image?: string;
  checks?: Record<string, string>;
  audit_points?: string[];
  provenance?: {
    system: string;
    method: string;
    ref?: string;
    line?: number;
  };
}

export interface EvidenceSet {
  request_id: string;
  instruction: string;
  items: EvidenceItem[];
  counts: Record<string, number>;
  narrative?: string;
  document_path?: string;
}

export interface Citation {
  label: string;
  ref?: string;
  kind: string;
}

export interface QnAAnswer {
  answer: string;
  routed_to: string;
  citations: Citation[];
  table?: Record<string, any>[];
  unsupported?: boolean;
}

export interface KPIs {
  open_vulnerabilities: number;
  audit_items_due_30d: number;
  high_severity_siis: number;
  remediations_on_track_pct: number;
}
