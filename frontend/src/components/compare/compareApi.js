
import { compareDocuments as compareBackend } from "@/services/api";

// Adapter between the Compare UI API and the existing backend service.
export async function compareDocuments({
  question,
  documentIds,
  nResults = 5,
}) {
  return compareBackend(question, documentIds, nResults);
}

export function buildComparePayload({
  question,
  documentIds,
  nResults,
}) {
  return {
    question,
    document_ids: documentIds,
    n_results: nResults,
  };
}