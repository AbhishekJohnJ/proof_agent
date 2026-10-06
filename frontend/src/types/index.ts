export interface QualityWarning {
  severity: 'warning' | 'critical' | 'info';
  type: string;
  message: string;
  affected_columns: string[];
}

export interface ColumnProfile {
  name: string;
  inferred_type: string;
  missing_count: number;
  missing_percentage: number;
  unique_count: number;
  sample_values: any[];
  has_mixed_units: boolean;
  is_constant: boolean;
}

export interface DatasetProfile {
  dataset_id: string;
  filename: string;
  rows: number;
  columns: number;
  column_names: string[];
  missing_values_total: number;
  duplicate_rows: number;
  column_profiles: ColumnProfile[];
  quality_status: 'good' | 'medium' | 'poor' | 'unprocessable';
  quality_warnings: QualityWarning[];
}

export interface VerificationResult {
  executed: boolean;
  execution_success: boolean;
  output_present: boolean;
  output_valid: boolean;
  reproducible: boolean;
  datasets_used: string[];
  filters_verified: boolean;
  data_quality_checked: boolean;
  answer_matches_output: boolean;
  status: 'verified' | 'unverified' | 'failed' | 'refused';
  confidence_score: number;
  errors: string[];
  warnings: string[];
}

export interface EvidenceItem {
  type: 'data' | 'document' | 'code' | 'execution' | 'verification';
  source: string;
  description: string;
  details: Record<string, any>;
  page_number?: number;
  chunk_id?: string;
  dataset_id?: string;
  columns_used?: string[];
}

export interface AnalysisResultData {
  analysis_id: string;
  question: string;
  answer: string;
  status: 'success' | 'refused' | 'error' | 'model_not_configured' | 'execution_failed';
  code?: string;
  expected_result_type?: string;
  execution_result?: Record<string, any>;
  evidence: EvidenceItem[];
  verification?: VerificationResult;
  confidence: number;
  refusal_reason?: string;
  warnings: string[];
}
