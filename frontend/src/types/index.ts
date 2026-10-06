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

export interface DocumentMetadata {
  document_id: string;
  filename: string;
  file_type: string;
  page_count: number;
  chunk_count: number;
  file_size_bytes: number;
  created_at: string;
  status: string;
}

export type CheckStatus = 'PASS' | 'FAIL' | 'NOT_CHECKED' | 'NOT_APPLICABLE';

export interface VerificationResult {
  executed: CheckStatus;
  execution_success: CheckStatus;
  output_present: CheckStatus;
  output_valid: CheckStatus;
  expected_type_matched: CheckStatus;
  reproducible: CheckStatus;
  selected_datasets_used: CheckStatus;
  result_consistent: CheckStatus;
  quality_check_performed: boolean;
  quality_issues_found: boolean;
  critical_quality_issues: boolean;
  status: 'VERIFIED' | 'VERIFICATION_FAILED' | 'REFUSED' | 'UNVERIFIED';
  confidence_score: number;
  comparison_method: string;
  numeric_tolerance_difference: number;
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
  status: 'RECEIVED' | 'PLANNED' | 'CODE_GENERATED' | 'CODE_VALIDATED' | 'EXECUTING' | 'EXECUTION_FAILED' | 'VERIFYING' | 'VERIFIED' | 'VERIFICATION_FAILED' | 'REFUSED' | 'MODEL_NOT_CONFIGURED';
  code?: string;
  expected_result_type?: string;
  execution_result?: Record<string, any>;
  canonical_result?: {
    result: any;
    metric: string;
    unit?: string;
  };
  evidence: EvidenceItem[];
  verification?: VerificationResult;
  confidence: number;
  refusal_reason?: string;
  warnings: string[];
  error_message?: string;
}
