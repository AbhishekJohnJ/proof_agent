import { IndexedDocument } from '../types';
import { INITIAL_DOCUMENTS } from '../data/mockData';

let documentsState: IndexedDocument[] = [...INITIAL_DOCUMENTS];

export async function getDocuments(): Promise<IndexedDocument[]> {
  return Promise.resolve([...documentsState]);
}

export async function searchEvidence(query: string): Promise<IndexedDocument[]> {
  if (!query.trim()) return Promise.resolve([...documentsState]);
  const q = query.toLowerCase();
  const filtered = documentsState.filter(
    (doc) =>
      doc.filename.toLowerCase().includes(q) ||
      doc.sections.some((s) => s.title.toLowerCase().includes(q) || s.snippet.toLowerCase().includes(q))
  );
  return Promise.resolve(filtered);
}
