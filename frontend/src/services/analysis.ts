import { Analysis } from '../types';
import { INITIAL_ANALYSES, SAMPLE_QUALITY_REPORT } from '../data/mockData';

let analysesState: Analysis[] = [...INITIAL_ANALYSES];

export async function getAnalyses(): Promise<Analysis[]> {
  return Promise.resolve([...analysesState]);
}

export async function getAnalysisById(id: string): Promise<Analysis | undefined> {
  // If id is res-1, res-2, res-3, res-refused, res-conflict return directly
  const found = analysesState.find((a) => a.id === id);
  if (found) return Promise.resolve(found);
  // Default fallback to first analysis
  return Promise.resolve(analysesState[0]);
}

export async function createAnalysis(
  question: string,
  datasetId: string,
  datasetName: string
): Promise<Analysis> {
  const isRefusal = question.toLowerCase().includes('satisfaction') || question.toLowerCase().includes('nps');
  const isConflict = question.toLowerCase().includes('annual report') || question.toLowerCase().includes('compare');

  const newId = `res-${Date.now()}`;

  let newAnalysis: Analysis;

  if (isRefusal) {
    newAnalysis = {
      id: newId,
      question,
      datasetId,
      datasetName,
      status: 'refused',
      confidence: 'low',
      date: 'Today',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
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
        missingFields: ['Customer Satisfaction (CSAT)', 'NPS Score'],
        whyStopped:
          'ProofAI strictly validates dataset schemas. Providing an estimated or hallucinatory answer would violate data provenance requirements since no customer satisfaction metrics exist in the selected dataset.',
      },
      trace: [
        { timestamp: 'Just now', step: 'Question received & parsed', status: 'completed' },
        { timestamp: 'Just now', step: 'Schema audit performed', status: 'warning' },
        { timestamp: 'Just now', step: 'Missing column flagged', status: 'failed' },
        { timestamp: 'Just now', step: 'Intelligent Refusal Triggered', status: 'completed' },
      ],
      verification: {
        executionSuccessful: false,
        reproducible: false,
        requiredFieldsPresent: false,
        dataQualityPassed: false,
        sourceConflicts: false,
        confidenceReason: ['Refused due to missing schema columns'],
      },
    };
  } else if (isConflict) {
    newAnalysis = {
      id: newId,
      question,
      datasetId,
      datasetName,
      status: 'warning',
      confidence: 'medium',
      date: 'Today',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      conflictDetails: {
        conflictType: 'Source Discrepancy (3.4% variance)',
        sourceA: { name: 'Annual_Report_2025.pdf (Page 42)', val: '₹14.7L' },
        sourceB: { name: 'sales_data.csv (Raw Transactions)', val: '₹15.2L' },
        explanation:
          'ProofAI detected a discrepancy between audited Annual Report text (₹14.7L) and raw sales_data.csv calculations (₹15.2L). ProofAI will not arbitrarily choose between conflicting sources without user direction.',
      },
      verification: {
        executionSuccessful: true,
        reproducible: true,
        requiredFieldsPresent: true,
        dataQualityPassed: false,
        sourceConflicts: true,
        confidenceReason: ['Source conflict detected between document and raw dataset'],
      },
    };
  } else {
    // Standard verified analysis
    newAnalysis = {
      id: newId,
      question,
      datasetId,
      datasetName,
      status: 'verified',
      confidence: 'high',
      answer: 'Total calculated metric: ₹14.7L (Verified)',
      date: 'Today',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      explanation: `Analysis executed on ${datasetName}. Calculated sum of Revenue across filtered records.\n\nResult = ₹14.7L with zero calculation error.`,
      kpis: [
        { label: 'Primary Result', value: '₹14.7L' },
        { label: 'Records Evaluated', value: '10,482' },
        { label: 'Execution Runtime', value: '0.64s' },
        { label: 'Reproducibility', value: '100%' },
      ],
      calculation: {
        formula: 'SUM(Revenue WHERE Status = "Completed")',
        inputs: {
          Dataset: datasetName,
          'Total Rows': 10482,
          'Column Evaluated': 'Revenue',
        },
        steps: [
          { label: 'Filter Active Rows', expression: 'Status == "Completed"', result: '10,482 rows' },
          { label: 'Sum Values', expression: 'SUM(Revenue)', result: '14,70,000' },
          { label: 'Format Result', expression: 'CurrencyFormat(INR)', result: '₹14.7L' },
        ],
        result: '₹14.7L',
        validations: {
          numericResultValidated: true,
          requiredFieldsPresent: true,
          calculationSuccessful: true,
        },
      },
      codeDetails: {
        code: `import pandas as pd
df = pd.read_csv('${datasetName}')
total = df['Revenue'].sum()
print(f"Verified Result: ₹{total:,.2f}")`,
        executionStatus: 'Successful',
        executionTime: '0.64s',
        environment: 'Sandboxed Python 3.11',
        outputType: 'Numeric',
        reproducible: true,
        stdout: 'Verified Result: ₹1,470,000.00',
      },
      dataQuality: SAMPLE_QUALITY_REPORT,
      evidence: [
        {
          id: `ev-${Date.now()}`,
          document: 'Annual_Report_2025.pdf',
          page: 42,
          section: 'Q4 Financial Highlights',
          excerpt: 'Q4 Revenue reached ₹14.7L driven by western enterprise sales.',
          relevance: 0.96,
          fileType: 'pdf',
        },
      ],
      trace: [
        { timestamp: '10:42:01', step: 'Question received & parsed', status: 'completed' },
        { timestamp: '10:42:02', step: 'Dataset selected & validated', status: 'completed' },
        { timestamp: '10:42:03', step: 'Analysis plan & code generated', status: 'completed' },
        { timestamp: '10:42:04', step: 'Sandbox execution completed', status: 'completed' },
        { timestamp: '10:42:05', step: 'Numerical result verified', status: 'completed' },
        { timestamp: '10:42:06', step: 'Reproducibility check passed', status: 'completed' },
        { timestamp: '10:42:07', step: 'Final answer generated with proof', status: 'completed' },
      ],
      verification: {
        executionSuccessful: true,
        reproducible: true,
        requiredFieldsPresent: true,
        dataQualityPassed: true,
        sourceConflicts: false,
        confidenceReason: [
          'Calculation executed in isolated Python sandbox',
          'Required dataset columns validated',
          'Result reproduced across dual math engines',
          'Cross-verified with indexed PDF documents',
        ],
      },
    };
  }

  analysesState = [newAnalysis, ...analysesState];
  return Promise.resolve(newAnalysis);
}
