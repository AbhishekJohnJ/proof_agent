import { Dataset } from '../types';
import { INITIAL_DATASETS } from '../data/mockData';

let datasetsState: Dataset[] = [...INITIAL_DATASETS];

export async function getDatasets(): Promise<Dataset[]> {
  return Promise.resolve([...datasetsState]);
}

export async function getDatasetById(id: string): Promise<Dataset | undefined> {
  return Promise.resolve(datasetsState.find((d) => d.id === id || d.name === id));
}

export async function uploadDataset(file: File): Promise<Dataset> {
  const isPdf = file.name.endsWith('.pdf');
  const isXlsx = file.name.endsWith('.xlsx') || file.name.endsWith('.xls');

  const newDataset: Dataset = {
    id: `ds-${Date.now()}`,
    name: file.name,
    type: isPdf ? 'pdf' : isXlsx ? 'xlsx' : 'csv',
    rows: isPdf ? 14 : Math.floor(Math.random() * 8000) + 1200,
    columns: isPdf ? 0 : Math.floor(Math.random() * 10) + 6,
    size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
    updatedAt: 'Just now',
    status: 'ready',
    missingValuesPct: Number((Math.random() * 2).toFixed(1)),
    duplicateRows: Math.floor(Math.random() * 15),
    warningCount: 1,
    columnNames: [
      'ID',
      'Transaction_Date',
      'Customer_ID',
      'Product',
      'Category',
      'Region',
      'Revenue',
      'Cost',
      'Discount',
    ],
  };

  datasetsState = [newDataset, ...datasetsState];
  return Promise.resolve(newDataset);
}

export async function deleteDataset(id: string): Promise<boolean> {
  datasetsState = datasetsState.filter((d) => d.id !== id);
  return Promise.resolve(true);
}
