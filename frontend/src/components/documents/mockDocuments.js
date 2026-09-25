// Visual-development placeholder data. Replace with real API data later.
export const mockDocuments = [
  { id: "1", name: "system-design-primer.pdf", pages: 42, date: "2 hours ago", status: "Ready" },
  { id: "2", name: "distributed-systems-notes.pdf", pages: 18, date: "Yesterday", status: "Ready" },
  { id: "3", name: "research-paper-llms.pdf", pages: 27, date: "3 days ago", status: "Processing" },
  { id: "4", name: "architecture-decision-records.pdf", pages: 9, date: "Last week", status: "Ready" },
];

export const getDocumentById = (id) => mockDocuments.find((d) => String(d.id) === String(id));

// Page navigation placeholder (1..pages), trimmed for display.
export const getPages = (doc) =>
  Array.from({ length: doc?.pages || 0 }, (_, i) => i + 1);