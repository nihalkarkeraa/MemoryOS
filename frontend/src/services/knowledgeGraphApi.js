import axios from "axios";
import { API_BASE_URL } from "@/services/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});

class KnowledgeGraphApiError extends Error {
  constructor(message) {
    super(message);
    this.name = "KnowledgeGraphApiError";
    this.isApiError = true;
  }
}

function getFriendlyError(error, fallback) {
  if (!error) {
    return fallback;
  }

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
  } catch (error) {
    throw new KnowledgeGraphApiError(
      getFriendlyError(error, fallback)
    );
  }
}

export async function getKnowledgeGraph() {
  const response = await withError(
    api.get("/knowledge-graph"),
    "Failed to load the knowledge graph."
  );

  const data = response?.data || {};

  return {
    nodes: Array.isArray(data.nodes) ? data.nodes : [],
    edges: Array.isArray(data.edges) ? data.edges : [],
    nodeCount:
      typeof data.node_count === "number"
        ? data.node_count
        : Array.isArray(data.nodes)
          ? data.nodes.length
          : 0,
    edgeCount:
      typeof data.edge_count === "number"
        ? data.edge_count
        : Array.isArray(data.edges)
          ? data.edges.length
          : 0,
  };
}

export async function getKnowledgeGraphConcept(conceptId) {
  if (!conceptId) {
    throw new KnowledgeGraphApiError(
      "A concept ID is required."
    );
  }

  const response = await withError(
    api.get(
      `/knowledge-graph/concepts/${encodeURIComponent(conceptId)}`
    ),
    "Failed to load concept details."
  );

  return response?.data || null;
}

export async function getDocumentKnowledgeGraphStatus(documentId) {
  if (!documentId) {
    throw new KnowledgeGraphApiError(
      "A document ID is required."
    );
  }

  const response = await withError(
    api.get(
      `/documents/${encodeURIComponent(
        documentId
      )}/knowledge-graph/status`
    ),
    "Failed to load knowledge graph status."
  );

  return response?.data || null;
}