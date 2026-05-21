/**
 * Thin fetch wrapper for the FastAPI backend.
 * Uses same-origin `/api` when Vite proxy is configured.
 */
const API_BASE = import.meta.env.VITE_API_URL ?? "";

function parseErrorDetail(text) {
	try {
		const j = JSON.parse(text);
		if (typeof j.detail === "string") return j.detail;
		if (Array.isArray(j.detail)) {
			return j.detail.map((d) => d.msg || JSON.stringify(d)).join("; ");
		}
		if (j.detail) return JSON.stringify(j.detail);
	} catch {
		/* ignore */
	}
	return text || "Request failed";
}

export async function api(path, options = {}) {
	const url = `${API_BASE}${path}`;
	const headers = {
		Accept: "application/json",
		...(options.headers || {}),
	};
	if (options.body && !headers["Content-Type"]) {
		headers["Content-Type"] = "application/json";
	}
	const res = await fetch(url, { ...options, headers });
	const text = await res.text();
	if (!res.ok) {
		throw new Error(parseErrorDetail(text));
	}
	if (!text) return null;
	try {
		return JSON.parse(text);
	} catch {
		return text;
	}
}

export const endpoints = {
	health: () => api("/api/health"),
	projects: () => api("/api/projects"),
	project: (id) => api(`/api/projects/${id}`),
	createProject: (name) =>
		api("/api/projects", { method: "POST", body: JSON.stringify({ name }) }),
	deleteProject: (id) => api(`/api/projects/${id}`, { method: "DELETE" }),
	exportProject: (id) => api(`/api/projects/${id}/export`, { method: "POST" }),
	listShots: (projectId) => api(`/api/projects/${projectId}/shots`),
	createShot: (projectId, body = {}) =>
		api(`/api/projects/${projectId}/shots`, {
			method: "POST",
			body: JSON.stringify(body),
		}),
	getShot: (shotId) => api(`/api/shots/${shotId}`),
	deleteShot: (shotId) => api(`/api/shots/${shotId}`, { method: "DELETE" }),
	generate: (shotId, prompt) =>
		api(`/api/shots/${shotId}/generate`, {
			method: "POST",
			body: JSON.stringify({ prompt }),
		}),
	edit: (shotId, message) =>
		api(`/api/shots/${shotId}/edit`, {
			method: "POST",
			body: JSON.stringify({ message }),
		}),
	regenerate: (shotId, prompt) =>
		api(`/api/shots/${shotId}/regenerate`, {
			method: "POST",
			body: JSON.stringify({ prompt: prompt ?? null }),
		}),
	render: (shotId, tryFix = false) =>
		api(`/api/shots/${shotId}/render?try_fix=${tryFix ? "true" : "false"}`, {
			method: "POST",
		}),
};
