// Search API layer — keeps backend communication separate from UI.
// Future endpoint: POST /search
//
// Request shape:
// {
//   "query": "database indexing",
//   "n_results": 5,
//   "document_ids": null   // null = all documents; otherwise an array of ids
// }
//
// Expected response (when wired):
// { results: [{ id, name, page, excerpt, score }] }

export async function searchKnowledge({ query, nResults, documentIds }) {
  // Placeholder — real implementation will POST /search via the SDK client.
  // We deliberately do not fabricate results here.
  throw new Error("Search endpoint not yet implemented");
}

export function buildSearchPayload({ query, nResults, scope, documents }) {
  const documentIds =
    scope && scope !== "all" ? [scope] : null;
  return {
    query,
    n_results: nResults,
    document_ids: documentIds,
  };
}