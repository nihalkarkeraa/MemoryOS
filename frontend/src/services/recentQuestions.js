// Local store of recent questions asked from the Home workspace.
// Backed by localStorage — real (user-generated) data, never fabricated.
const KEY = "memoryos:recentQuestions";

export function getRecentQuestions() {
  try {
    const raw = localStorage.getItem(KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

export function addRecentQuestion(question, answer = "") {
  if (!question) return getRecentQuestions();
  try {
    const list = getRecentQuestions();
    const entry = {
      question,
      preview: (answer || "").slice(0, 180),
      ts: Date.now(),
    };
    const next = [
      entry,
      ...list.filter((q) => q.question !== question),
    ].slice(0, 6);
    localStorage.setItem(KEY, JSON.stringify(next));
    return next;
  } catch {
    return getRecentQuestions();
  }
}