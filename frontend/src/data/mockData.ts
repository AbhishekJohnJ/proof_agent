import { Dataset, Analysis, IndexedDocument, DataQualityReport } from '../types';

export const INITIAL_DATASETS: Dataset[] = [
  {
    id: 'ds-1',
    name: 'sales_data.csv',
    type: 'csv',
    rows: 10482,
    columns: 12,
    size: '12.4 MB',
    updatedAt: '2 hours ago',
    status: 'ready',
    missingValuesPct: 2.4,
    duplicateRows: 37,
    warningCount: 3,
    columnNames: [
      'Order_ID',
      'Order_Date',
      'Customer_ID',
      'Product',
      'Category',
      'Region',
      'Quantity',
      'Unit_Price',
      'Discount',
      'Revenue',
      'Cost',
      'Salesperson',
    ],
  },
  {
    id: 'ds-2',
    name: 'customers_q4.xlsx',
    type: 'xlsx',
    rows: 3450,
    columns: 8,
    size: '4.8 MB',
    updatedAt: 'Yesterday',
    status: 'ready',
    missingValuesPct: 0.8,
    duplicateRows: 12,
    warningCount: 1,
    columnNames: ['Customer_ID', 'Customer_Name', 'Region', 'Segment', 'Signup_Date', 'Lifetime_Value', 'Status', 'Account_Owner'],
  },
  {
    id: 'ds-3',
    name: 'Annual_Report_2025.pdf',
    type: 'pdf',
    rows: 42, // pages
    columns: 0,
    size: '18.2 MB',
    updatedAt: '3 days ago',
    status: 'ready',
    missingValuesPct: 0,
    duplicateRows: 0,
    warningCount: 0,
    columnNames: [],
  },
];

export const INITIAL_DOCUMENTS: IndexedDocument[] = [
  {
    id: 'doc-1',
    filename: 'Annual_Report_2025.pdf',
    fileType: 'pdf',
    pages: 42,
    indexedChunks: 124,
    status: 'Indexed',
    uploadedAt: '3 days ago',
    sections: [
      { title: 'Executive Summary', page: 4, snippet: 'Q4 revenue closed at ₹14.7L representing an 18.6% sequential QoQ growth over Q3.' },
      { title: 'Regional Operational Breakdown', page: 18, snippet: 'The Western and Northern sales divisions outperformed targets driven by enterprise renewals.' },
      { title: 'Q4 Financial Highlights', page: 42, snippet: 'Revenue increased during Q4 to ₹14.7L compared to ₹12.4L in Q3. Gross margin remained steady at 41.2%.' },
    ],
  },
  {
    id: 'doc-2',
    filename: 'Financial_Results_Q4.pdf',
    fileType: 'pdf',
    pages: 28,
    indexedChunks: 82,
    status: 'Indexed',
    uploadedAt: '1 week ago',
    sections: [
      { title: 'Revenue by Line of Business', page: 12, snippet: 'Software subscriptions accounted for ₹9.2L of total revenue, up 22% year-over-year.' },
      { title: 'Audit Notes', page: 26, snippet: 'All calculations verified against primary transaction logs without material variance.' },
    ],
  },
];

export const SAMPLE_QUALITY_REPORT: DataQualityReport = {
  requiredColumnsPresent: true,
  numericFieldsValid: true,
  noRelevantMissingValues: true,
  duplicateRowsCount: 37,
  duplicateRowsDetected: true,
  currencyMismatch: false,
  missingValuesMap: {
    Customer_ID: 0.0,
    Revenue: 0.0,
    Discount: 3.2,
    Salesperson: 1.1,
    Order_Date: 0.0,
  },
  warnings: [
    {
      id: 'w-1',
      severity: 'warning',
      type: 'Missing Values',
      message: '3.2% of discount values are missing',
      affectedColumns: ['Discount'],
    },
    {
      id: 'w-2',
      severity: 'warning',
      type: 'Ambiguous Dates',
      message: '14 records contain ambiguous dates in Order_Date column',
      affectedColumns: ['Order_Date'],
    },
    {
      id: 'w-3',
      severity: 'info',
      type: 'Outliers Detected',
      message: '7 records contain unusually high revenue values (> 3 std dev above mean)',
      affectedColumns: ['Revenue'],
    },
  ],
  impactOnAnswer: 'Low impact. The detected duplicate records do not affect the selected Q3/Q4 revenue calculation because duplicates belong to unconfirmed draft orders in Q1.',
  impactLevel: 'low',
};

export const INITIAL_ANALYSES: Analysis[] = [
  {
    id: 'res-1',
    question: 'What was the revenue growth between Q3 and Q4?',
    datasetId: 'ds-1',
    datasetName: 'sales_data.csv',
    status: 'verified',
    confidence: 'high',
    answer: 'Revenue increased by 18.6%',
    date: 'Today',
    timestamp: '10:42 AM',
    explanation: `Q3 revenue was calculated as ₹12.4L and Q4 revenue as ₹14.7L based on the Order_Date and Revenue columns in sales_data.csv.\n\nIncrease = ₹14.7L − ₹12.4L = ₹2.3L\nGrowth = (₹2.3L / ₹12.4L) × 100 = 18.548% ≈ 18.6%`,
    kpis: [
      { label: 'Q3 Revenue', value: '₹12.4L' },
      { label: 'Q4 Revenue', value: '₹14.7L' },
      { label: 'Increase', value: '₹2.3L' },
      { label: 'Growth Rate', value: '18.6%' },
    ],
    calculation: {
      formula: '(Q4_Revenue - Q3_Revenue) / Q3_Revenue * 100',
      inputs: {
        'Q3 Revenue': '₹12,40,000',
        'Q4 Revenue': '₹14,70,000',
        'Filtered Rows (Q3)': 2410,
        'Filtered Rows (Q4)': 2890,
      },
      steps: [
        { label: 'Sum Q3 Revenue', expression: 'SUM(Revenue WHERE Quarter = Q3)', result: '1,240,000' },
        { label: 'Sum Q4 Revenue', expression: 'SUM(Revenue WHERE Quarter = Q4)', result: '1,470,000' },
        { label: 'Absolute Difference', expression: '1,470,000 - 1,240,000', result: '230,000' },
        { label: 'Relative Growth %', expression: '(230,000 / 1,240,000) * 100', result: '18.548387...' },
      ],
      result: '18.6%',
      validations: {
        numericResultValidated: true,
        requiredFieldsPresent: true,
        calculationSuccessful: true,
      },
    },
    codeDetails: {
      code: `import pandas as pd

# Load dataset
df = pd.read_csv('sales_data.csv')

# Parse date and derive quarter
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Quarter'] = df['Order_Date'].dt.to_period('Q')

# Calculate totals
q3_revenue = df[df['Quarter'] == '2025Q3']['Revenue'].sum()
q4_revenue = df[df['Quarter'] == '2025Q4']['Revenue'].sum()

# Growth calculation
growth_pct = ((q4_revenue - q3_revenue) / q3_revenue) * 100

print(f"Q3 Revenue: {q3_revenue:,.2f}")
print(f"Q4 Revenue: {q4_revenue:,.2f}")
print(f"Growth: {growth_pct:.1f}%")`,
      executionStatus: 'Successful',
      executionTime: '0.82s',
      environment: 'Sandboxed Python 3.11',
      outputType: 'Numeric',
      reproducible: true,
      stdout: 'Q3 Revenue: 1,240,000.00\nQ4 Revenue: 1,470,000.00\nGrowth: 18.6%',
    },
    evidence: [
      {
        id: 'ev-1',
        document: 'Annual_Report_2025.pdf',
        page: 42,
        section: 'Q4 Financial Highlights',
        excerpt: 'Revenue increased during Q4 to ₹14.7L compared to ₹12.4L in Q3, driven by expansion in enterprise accounts.',
        relevance: 0.98,
        fileType: 'pdf',
      },
    ],
    dataQuality: SAMPLE_QUALITY_REPORT,
    trace: [
      { timestamp: '10:42:01', step: 'Question received & parsed', status: 'completed', details: 'Parsed metric: revenue growth, filter: Q3 to Q4' },
      { timestamp: '10:42:02', step: 'Question classified as comparative analysis', status: 'completed', details: 'Intent: percentage difference between two time periods' },
      { timestamp: '10:42:03', step: 'sales_data.csv selected', status: 'completed', details: 'Required columns found: Order_Date, Revenue' },
      { timestamp: '10:42:04', step: 'Analysis plan & code generated', status: 'completed', details: 'Deterministic pandas aggregation logic created' },
      { timestamp: '10:42:05', step: 'Sandbox execution completed', status: 'completed', details: 'Exit code 0, execution runtime 0.82s' },
      { timestamp: '10:42:06', step: 'Numerical result verified', status: 'completed', details: 'Verified against independent mathematical parser' },
      { timestamp: '10:42:06', step: 'Reproducibility check passed', status: 'completed', details: 'Secondary run produced identical value (18.548387%)' },
      { timestamp: '10:42:07', step: 'Document evidence cross-checked', status: 'completed', details: 'Matched Annual_Report_2025.pdf Page 42 excerpt' },
      { timestamp: '10:42:07', step: 'Final answer generated with proof', status: 'completed', details: 'Proof certificate generated' },
    ],
    verification: {
      executionSuccessful: true,
      reproducible: true,
      requiredFieldsPresent: true,
      dataQualityPassed: true,
      sourceConflicts: false,
      confidenceReason: [
        'Calculation executed successfully in sandboxed runtime',
        'Required columns (Order_Date, Revenue) 100% complete',
        'Result verified independently via 2 separate algorithms',
        'External document evidence matches calculated result (Annual_Report_2025.pdf)',
      ],
    },
    charts: {
      type: 'monthly_growth',
      title: 'Monthly Revenue Progression (Q3 vs Q4)',
      subtitle: 'Consistent month-over-month expansion culminating in Q4 peak',
    },
  },
  {
    id: 'res-2',
    question: 'Which region generated the highest revenue in Q4?',
    datasetId: 'ds-1',
    datasetName: 'sales_data.csv',
    status: 'verified',
    confidence: 'high',
    answer: 'North Region generated highest revenue (₹5.8L, 39.5%)',
    date: 'Yesterday',
    timestamp: '03:15 PM',
    explanation: 'Revenue was aggregated by Region for Q4 orders (Order_Date in Oct-Dec 2025). North region achieved ₹5.8L out of total Q4 revenue ₹14.7L.',
    kpis: [
      { label: 'Top Region', value: 'North' },
      { label: 'North Revenue', value: '₹5.8L' },
      { label: 'Share of Total', value: '39.5%' },
      { label: 'Runner-up', value: 'West (₹4.2L)' },
    ],
    calculation: {
      formula: 'MAX(SUM(Revenue) GROUP BY Region)',
      inputs: {
        'North Revenue': '₹5,80,000',
        'West Revenue': '₹4,20,000',
        'South Revenue': '₹2,90,000',
        'East Revenue': '₹1,80,000',
      },
      steps: [
        { label: 'Filter Q4 Rows', expression: 'WHERE Order_Date BETWEEN 2025-10-01 AND 2025-12-31', result: '2,890 rows' },
        { label: 'Group & Sum', expression: 'GROUP BY Region SUM(Revenue)', result: 'North: 5.8L, West: 4.2L...' },
        { label: 'Rank Regions', expression: 'SORT DESC BY Revenue', result: 'Rank 1: North' },
      ],
      result: 'North (₹5,80,000)',
      validations: {
        numericResultValidated: true,
        requiredFieldsPresent: true,
        calculationSuccessful: true,
      },
    },
    codeDetails: {
      code: `import pandas as pd
df = pd.read_csv('sales_data.csv')
q4_df = df[pd.to_datetime(df['Order_Date']).dt.quarter == 4]
regional_rev = q4_df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)
print(regional_rev)`,
      executionStatus: 'Successful',
      executionTime: '0.45s',
      environment: 'Sandboxed Python 3.11',
      outputType: 'Table',
      reproducible: true,
    },
    verification: {
      executionSuccessful: true,
      reproducible: true,
      requiredFieldsPresent: true,
      dataQualityPassed: true,
      sourceConflicts: false,
      confidenceReason: [
        'All regional records present and validated',
        'Zero missing values in Region or Revenue columns',
        'Calculation verified across all 4 geographical regions',
      ],
    },
    charts: {
      type: 'regional_revenue',
      title: 'Q4 Revenue Breakdown by Region',
      subtitle: 'North leads with 39.5% share followed by West region',
    },
  },
  {
    id: 'res-3',
    question: 'What is the average customer retention rate across quarters?',
    datasetId: 'ds-2',
    datasetName: 'customers_q4.xlsx',
    status: 'warning',
    confidence: 'medium',
    answer: 'Estimated retention rate is 74.2%',
    date: 'Yesterday',
    timestamp: '05:40 PM',
    explanation: 'Calculation completed, but 3.2% missing discount data and 14 records with ambiguous date formats were detected.',
    kpis: [
      { label: 'Est. Retention', value: '74.2%' },
      { label: 'Active Cohort', value: '2,560' },
      { label: 'Quality Warning', value: '14 Ambiguous Dates' },
    ],
    verification: {
      executionSuccessful: true,
      reproducible: true,
      requiredFieldsPresent: true,
      dataQualityPassed: false,
      sourceConflicts: false,
      confidenceReason: [
        'Calculation executed successfully',
        'Warning: 14 ambiguous date entries required fallback parsing',
        'Result reproducible within 0.5% tolerance',
      ],
    },
  },
  {
    id: 'res-refused',
    question: 'What is customer satisfaction by region?',
    datasetId: 'ds-1',
    datasetName: 'sales_data.csv',
    status: 'refused',
    confidence: 'low',
    date: 'Today',
    timestamp: '11:10 AM',
    refusalDetails: {
      reason: 'Missing Required Column in Dataset',
      availableFields: [
        'Order_ID',
        'Order_Date',
        'Customer_ID',
        'Product',
        'Category',
        'Region',
        'Quantity',
        'Unit_Price',
        'Discount',
        'Revenue',
        'Cost',
        'Salesperson',
      ],
      missingFields: ['Customer Satisfaction (CSAT)', 'NPS Score', 'Feedback Rating'],
      whyStopped:
        'ProofAI adheres to strict verification principles. Providing an estimated or hallucinatory answer would violate data provenance requirements since no customer satisfaction metrics exist in the selected dataset.',
    },
    trace: [
      { timestamp: '11:10:01', step: 'Question received', status: 'completed', details: 'Target metric: Customer Satisfaction' },
      { timestamp: '11:10:02', step: 'Schema audit performed', status: 'warning', details: 'Scanning 12 columns in sales_data.csv' },
      { timestamp: '11:10:03', step: 'Missing column flagged', status: 'failed', details: 'No match for CSAT / Satisfaction score' },
      { timestamp: '11:10:04', step: 'Intelligent Refusal Triggered', status: 'completed', details: 'Analysis safely stopped to prevent hallucination' },
    ],
    verification: {
      executionSuccessful: false,
      reproducible: false,
      requiredFieldsPresent: false,
      dataQualityPassed: false,
      sourceConflicts: false,
      confidenceReason: [
        'Refused due to absent schema columns',
        'No synthetic or estimated metrics generated',
      ],
    },
  },
  {
    id: 'res-conflict',
    question: 'Compare Q4 revenue between financial report and sales dataset',
    datasetId: 'ds-1',
    datasetName: 'sales_data.csv',
    status: 'warning',
    confidence: 'medium',
    date: '2 days ago',
    timestamp: '02:00 PM',
    conflictDetails: {
      conflictType: 'Source Discrepancy (3.4% variance)',
      sourceA: { name: 'Annual_Report_2025.pdf (Page 42)', val: '₹14.7L (₹14,70,000)' },
      sourceB: { name: 'sales_data.csv (Raw Transactions)', val: '₹15.2L (₹15,20,000)' },
      explanation:
        'ProofAI detected a discrepancy between audited Annual Report text (₹14.7L) and unadjusted sales_data.csv row aggregating to ₹15.2L (due to ₹50k pending returns). ProofAI will not arbitrarily choose between conflicting sources without user preference.',
    },
    trace: [
      { timestamp: '02:00:01', step: 'Question received', status: 'completed' },
      { timestamp: '02:00:02', step: 'Multi-source analysis initiated', status: 'completed' },
      { timestamp: '02:00:03', step: 'Extracted PDF figure ₹14.7L', status: 'completed' },
      { timestamp: '02:00:04', step: 'Calculated CSV sum ₹15.2L', status: 'completed' },
      { timestamp: '02:00:05', step: 'Conflict resolution flag raised', status: 'warning', details: 'Variance exceeds 1% tolerance threshold' },
    ],
    verification: {
      executionSuccessful: true,
      reproducible: true,
      requiredFieldsPresent: true,
      dataQualityPassed: false,
      sourceConflicts: true,
      confidenceReason: [
        'Source discrepancy detected between document and raw dataset',
        'Requires user selection of authoritative source',
      ],
    },
  },
];
