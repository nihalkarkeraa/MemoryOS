import axios from "axios";
import { formatDistanceToNow, parseISO } from "date-fns";

// Backend base URL — set via VITE_API_BASE_URL env var.
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});

// ---- helpers --------------------------------------------------------------

class ApiError extends Error {
  constructor(message) {
    super(message);
    this.name = "ApiError";
    this.isApiError = true;
  }
}

function firstOf(obj, keys) {
  if (!obj || typeof obj !== "object") return undefined;

  for (const k of keys) {
    if (obj[k] !== undefined && obj[k] !== null) {
      return obj[k];
    }
  }

  return undefined;
}

// Translate raw axios errors into human-readable messages.
function toFriendlyError(error, fallback) {
  if (!error) return fallback;

  // No response received → network / backend down.
  if (!error.response && error.request) {
    return "MemoryOS couldn't connect to the backend.";
  }

  if (error.response) {
    const data = error.response.data;

    const detail =
      typeof data === "string"
        ? data
        : data?.detail || data?.message || data?.error;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }

    if (error.response.status >= 500) {
      return "MemoryOS couldn't connect to the backend.";
    }
  }

  return fallback;
}

async function withError(promise, fallback) {
  try {
    return await promise;
  } catch (e) {
    throw new ApiError(toFriendlyError(e, fallback));
  }
}

function formatRelative(dateValue) {
  if (!dateValue) return "Recently";

  try {
    const d =
      typeof dateValue === "string" && /\d/.test(dateValue)
        ? parseISO(dateValue)
        : new Date(dateValue);

    if (isNaN(d.getTime())) {
      return String(dateValue);
    }

    return formatDistanceToNow(d, { addSuffix: false });
  } catch {
    return String(dateValue);
  }
}

function normalizeStatus(s) {
  if (!s) return "Ready";

  const v = String(s).toLowerCase();

  if (
    v.includes("process") ||
    v.includes("pending") ||
    v.includes("index")
  ) {
    return "Processing";
  }

  if (v.includes("fail") || v.includes("error")) {
    return "Error";
  }

  return "Ready";
}

function normalizeDocument(raw, index = 0) {
  const id = firstOf(raw, [
    "id",
    "document_id",
    "doc_id",
    "uuid",
  ]);

  const name =
    firstOf(raw, [
      "name",
      "filename",
      "file_name",
      "original_filename",
      "title",
    ]) || "Untitled document";

  const pages = firstOf(raw, [
    "pages",
    "page_count",
    "num_pages",
    "total_pages",
    "pages_count",
  ]);

  const dateValue = firstOf(raw, [
    "uploaded_at",
    "created_at",
    "upload_date",
    "created_date",
    "date",
    "timestamp",
  ]);

  return {
    id: id != null ? String(id) : String(index),
    name,
    pages: typeof pages === "number" ? pages : Number(pages) || 0,
    status: normalizeStatus(
      firstOf(raw, [
        "status",
        "state",
        "processing_status",
      ])
    ),
    date: formatRelative(dateValue),
  };
}

function normalizeSource(raw, index = 0) {
  const name =
    firstOf(raw, [
      "filename",
      "file_name",
      "name",
      "document_name",
      "source",
      "title",
    ]) || `Source ${index + 1}`;

  const page = firstOf(raw, [
    "page",
    "page_number",
    "page_num",
    "pageno",
  ]);

  const content =
    firstOf(raw, [
      "content",
      "text",
      "excerpt",
      "chunk_content",
      "passage",
      "snippet",
    ]) || "";

  const hybridScore = firstOf(raw, [
    "hybrid_score",
    "hybridScore",
    "score",
    "bm25_score",
    "vector_score",
  ]);

  const rerankerScore = firstOf(raw, [
    "reranker_score",
    "rerankerScore",
    "relevance_score",
    "cross_encoder_score",
  ]);

  return {
    id:
      firstOf(raw, [
        "id",
        "chunk_id",
        "source_id",
      ]) || String(index),

    name,
    page: page ?? null,
    excerpt: content,
    content,

    hybridScore:
      typeof hybridScore === "number"
        ? hybridScore
        : null,

    rerankerScore:
      typeof rerankerScore === "number"
        ? rerankerScore
        : null,

    matchPercent: null,
  };
}

/*
 * Convert raw reranker scores into a relative 0–100 relevance
 * percentage for display.
 *
 * IMPORTANT:
 * CrossEncoder scores are ranking scores, not probabilities.
 * Therefore this is intentionally called a "match percentage"
 * only as a relative display indicator among the results
 * returned for the current query.
 *
 * Min-max normalization:
 *
 *     (score - minimum)
 *     ------------------ × 100
 *     (maximum - minimum)
 *
 * Highest result = 100
 * Lowest result  = 0
 */
function normalizeSearchMatchPercent(results) {
  if (!Array.isArray(results) || results.length === 0) {
    return results;
  }

  const scores = results
    .map((result) => result.rerankerScore)
    .filter(
      (score) =>
        typeof score === "number" &&
        Number.isFinite(score)
    );

  if (scores.length === 0) {
    return results.map((result) => ({
      ...result,
      matchPercent: null,
    }));
  }

  const minimum = Math.min(...scores);
  const maximum = Math.max(...scores);

  // If every result has exactly the same score,
  // there is no relative difference between them.
  if (maximum === minimum) {
    return results.map((result) => ({
      ...result,
      matchPercent:
        typeof result.rerankerScore === "number"
          ? 100
          : null,
    }));
  }

  return results.map((result) => {
    if (
      typeof result.rerankerScore !== "number" ||
      !Number.isFinite(result.rerankerScore)
    ) {
      return {
        ...result,
        matchPercent: null,
      };
    }

    const normalized =
      ((result.rerankerScore - minimum) /
        (maximum - minimum)) *
      100;

    return {
      ...result,
      matchPercent: Math.round(
        Math.max(0, Math.min(100, normalized))
      ),
    };
  });
}

function toArray(v) {
  if (!v) return [];

  if (Array.isArray(v)) {
    return v.map(String);
  }

  if (typeof v === "string") {
    return v
      .split(/\n|•|-\s/)
      .map((s) => s.trim())
      .filter(Boolean);
  }

  return [];
}

// ---- public API -----------------------------------------------------------

export async function checkHealth() {
  try {
    const res = await api.get("/health", {
      timeout: 5000,
    });

    return res.status >= 200 && res.status < 300;
  } catch {
    return false;
  }
}

export async function getDocuments() {
  const res = await withError(
    api.get("/documents"),
    "MemoryOS couldn't load your documents."
  );

  const data = res.data;

  const list = Array.isArray(data)
    ? data
    : data?.documents ||
      data?.items ||
      data?.results ||
      [];

  return list.map((d, i) => normalizeDocument(d, i));
}

export async function getDocument(documentId) {
  const res = await withError(
    api.get(`/documents/${documentId}`),
    "MemoryOS couldn't load this document."
  );

  // Backend returns:
  // { document: {...}, storage: {...} }
  const data = res.data;
  const document = data?.document || data;

  return normalizeDocument(document, 0);
}

export async function uploadDocument(file, onProgress) {
  const form = new FormData();
  form.append("file", file);

  const res = await withError(
    api.post("/documents/upload", form, {
      headers: {
        "Content-Type": "multipart/form-data",
      },

      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(
            Math.round((e.loaded / e.total) * 100)
          );
        }
      },
    }),
    "The document could not be uploaded."
  );

  const data = res.data;

  const doc = Array.isArray(data)
    ? data[0]
    : data?.document || data;

  return normalizeDocument(doc || data, 0);
}

export async function deleteDocument(documentId) {
  await withError(
    api.delete(`/documents/${documentId}`),
    "The document could not be deleted."
  );

  return true;
}

export async function searchKnowledge(
  query,
  nResults = 5,
  documentIds = null
) {
  const res = await withError(
    api.post("/search", {
      query,
      n_results: nResults,
      document_ids: documentIds,
    }),
    "Search failed. Please try again."
  );

  const data = res.data;

  const list = Array.isArray(data)
    ? data
    : data?.results ||
      data?.items ||
      data?.chunks ||
      [];

  const normalizedResults = list.map((s, i) =>
    normalizeSource(s, i)
  );

  return normalizeSearchMatchPercent(
    normalizedResults
  );
}

export async function chat(
  question,
  nResults = 5,
  documentIds = null
) {
  const res = await withError(
    api.post("/chat", {
      question,
      n_results: nResults,
      document_ids: documentIds,
    }),
    "MemoryOS couldn't generate an answer."
  );

  const data = res.data;

  const answer =
    firstOf(data, [
      "answer",
      "response",
      "result",
      "output",
      "reply",
    ]) || "";

  const rawSources =
    firstOf(data, [
      "sources",
      "context",
      "chunks",
      "references",
      "citations",
    ]) || [];

  const sources = (
    Array.isArray(rawSources)
      ? rawSources
      : []
  ).map((s, i) => normalizeSource(s, i));

  return {
    answer,
    sources,
  };
}

export async function summarizeDocument(documentId) {
  const res = await withError(
    api.post(
      `/documents/${documentId}/summary`,
      {}
    ),
    "MemoryOS couldn't generate the summary."
  );

  const data = res.data;

  const summary = firstOf(data, [
    "summary",
    "result",
    "output",
    "response",
  ]);

  const overview =
    firstOf(data, [
      "overview",
      "summary_overview",
      "executive_summary",
    ]) ||
    (typeof summary === "string"
      ? summary
      : "");

  const keyConcepts = toArray(
    firstOf(data, [
      "key_concepts",
      "keyConcepts",
      "concepts",
      "main_concepts",
    ])
  );

  const importantPoints = toArray(
    firstOf(data, [
      "important_points",
      "importantPoints",
      "key_points",
      "key_takeaways",
      "highlights",
      "points",
    ])
  );

  return {
    overview,
    keyConcepts,
    importantPoints,
    raw: data,
  };
}

export async function compareDocuments(
  question,
  documentIds,
  nResults = 5
) {
  const res = await withError(
    api.post("/compare", {
      question,
      document_ids: documentIds,
      n_results: nResults,
    }),
    "MemoryOS couldn't complete the comparison."
  );

  const data = res.data;

  const answer =
    firstOf(data, [
      "answer",
      "response",
      "result",
      "comparison",
      "output",
    ]) || "";

  const rawSources =
    firstOf(data, [
      "sources",
      "context",
      "chunks",
      "references",
      "citations",
    ]) || [];

  const sources = (
    Array.isArray(rawSources)
      ? rawSources
      : []
  ).map((s, i) =>
    normalizeSource(s, i)
  );

  const similarities = toArray(
    firstOf(data, [
      "similarities",
      "shared",
      "common_points",
      "common",
    ])
  );

  const differences = toArray(
    firstOf(data, [
      "differences",
      "diff",
      "divergences",
    ])
  );

  const notEstablished = toArray(
    firstOf(data, [
      "not_established",
      "notEstablished",
      "gaps",
      "unknown",
    ])
  );

  return {
    answer,
    similarities,
    differences,
    notEstablished,
    sources,
  };
}