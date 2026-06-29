import { createContext, useCallback, useEffect, useState } from "react";
import { endpoints } from "../api/client";

export const Context = createContext();

const defaultName = () => `Project ${new Date().toLocaleString()}`;


const ContextProvider = (props) => {

	{/* const [state, setState] = useState(initialState) */}
	{/* Here we use state to be the main variable and setState is used to change the value of the variable */}
	{/* state = "Hello", setState("Hello World") then state = "Hello World", value change */}
	{/* We can't directly change the value of state because if we do that then react can't identfy the change happened in state and can't render the change so we have to use setState function*/}

	const [input, setInput] = useState("");
	const [recentPrompt, setRecentPrompt] = useState("");
	const [prevPrompts, setPrevPrompts] = useState([]);
	const [showResults, setShowResults] = useState(false);
	const [loading, setLoading] = useState(false);
	const [renderLoading, setRenderLoading] = useState(false);
	const [exporting, setExporting] = useState(false);
	const [resultData, setResultData] = useState("");
	const [error, setError] = useState("");
	const [projects, setProjects] = useState([]);
	const [currentProject, setCurrentProject] = useState(null);
	const [shots, setShots] = useState([]);
	const [currentShot, setCurrentShot] = useState(null);

	const refreshProjects = useCallback(async () => {
		const list = await endpoints.projects();
		setProjects(list);
		return list;
	}, []);

	const loadProject = useCallback(async (id) => {
		const p = await endpoints.project(id);
		setCurrentProject(p);
		setShots(p.shots || []);
		if (p.shots?.length) {
			const sameProjectCurrentShot = currentShot?.project_id === p.id ? p.shots.find((s) => s.id === currentShot.id) : null;
			const selectedShot = sameProjectCurrentShot ?? p.shots[0];
			setCurrentShot(selectedShot);
			setShowResults(true);
			setResultData("");
			setRecentPrompt(selectedShot.user_prompt || "");
		} else {
			setCurrentShot(null);
		}
		return p;
	}, [currentShot]);

	const refreshShot = useCallback(async (shotId) => {
		const s = await endpoints.getShot(shotId);
		setCurrentShot(s);
		setShots((prev) => prev.map((x) => (x.id === s.id ? s : x)));
		return s;
	}, []);

	useEffect(() => {
		refreshProjects().catch((e) => console.error(e));
	}, [refreshProjects]);

	const newChat = () => {
		setLoading(false);
		setRenderLoading(false);
		setShowResults(false);
		setResultData("");
		setError("");
		setRecentPrompt("");
	};

	const createProject = async () => {
		setError("");
		const p = await endpoints.createProject(defaultName());
		await refreshProjects();
		await loadProject(p.id);
	};

	const selectProject = async (id) => {
		setError("");
		await loadProject(id);
	};

	const deleteProject = async (id) => {
		if (!window.confirm("Delete this project and all shots?")) return;
		setError("");
		await endpoints.deleteProject(id);
		if (currentProject?.id === id) {
			setCurrentProject(null);
			setShots([]);
			setCurrentShot(null);
			newChat();
		}
		await refreshProjects();
	};

	const createNewShot = async () => {
		if (!currentProject) {
			setError("Select or create a project first.");
			return;
		}
		setError("");
		const s = await endpoints.createShot(currentProject.id, { title: "Shot" });
		await loadProject(currentProject.id);
		setCurrentShot(s);
	};

	const selectShot = async (shot) => {
		setError("");
		const s = await endpoints.getShot(shot.id);
		setCurrentShot(s);
		setShowResults(true);
		setResultData("");
		setRecentPrompt(s.user_prompt || "");
	};

	const deleteShot = async (shotId) => {
		if (!window.confirm("Delete this shot?")) return;
		setError("");
		await endpoints.deleteShot(shotId);
		if (currentShot?.id === shotId) setCurrentShot(null);
		if (currentProject) await loadProject(currentProject.id);
	};

	const appendHistory = (text) => {
		setPrevPrompts((prev) => {
			const next = [text, ...prev.filter((p) => p !== text)];
			return next.slice(0, 20);
		});
	};

	const onSent = async (prompt) => {
		const text = (prompt ?? input).trim();
		if (!text) return;
		setRecentPrompt(text);
		setShowResults(true);
		setLoading(true);
		setRenderLoading(false);
		setResultData("");
		setError("");
		appendHistory(text);

		try {
			if (!currentProject) {
				throw new Error("Create or open a project from the sidebar first.");
			}

			// Use a local variable so we always work with the latest shot ref
			let shot = currentShot;
			if (!shot) {
				shot = await endpoints.createShot(currentProject.id, { title: "Shot" });
				await loadProject(currentProject.id);
				setCurrentShot(shot);
			}

			// Decide generate vs edit based on whether code already exists on THIS shot
			let updated;
			if (!shot.generated_manim_code) {
				updated = await endpoints.generate(shot.id, text);
			} else {
				updated = await endpoints.edit(shot.id, text);
			}

			setCurrentShot(updated);
			setShots((prev) => prev.map((x) => (x.id === updated.id ? updated : x)));

			const codePreview = updated.generated_manim_code?.slice(0, 4000) || "(no code returned)";
			setResultData(
				`<p><b>Manim code updated.</b> Scene: <code>${updated.scene_class_name || "?"}</code></p>` +
				`<pre style="white-space:pre-wrap;font-size:13px;background:#f6f7f8;padding:12px;border-radius:8px;max-height:240px;overflow:auto;">${escapeHtml(codePreview)}</pre>`
			);

			setLoading(false);
			setRenderLoading(true);

			const rendered = await endpoints.render(updated.id, false);
			setCurrentShot(rendered);
			setShots((prev) => prev.map((x) => (x.id === rendered.id ? rendered : x)));

			if (!rendered.video_url) {
				setError("Render failed. Check the log below or try Regenerate / Render + AI fix.");
				const log = rendered.render_log || "";
				setResultData(
					(prev) =>
						prev +
						`<p style="color:#b42318">Render error</p>` +
						`<pre style="white-space:pre-wrap;font-size:12px;background:#fff4f4;padding:12px;border-radius:8px;max-height:200px;overflow:auto;">${escapeHtml(log.slice(0, 8000))}</pre>`
				);
			}
		} catch (e) {
			setError(e.message || String(e));
			setResultData(
				`<p style="color:#b42318">${escapeHtml(e.message || String(e))}</p>`
			);
		} finally {
			// Always clear both loading states
			setLoading(false);
			setRenderLoading(false);
			setInput("");
		}
	};

	const runRender = async (tryFix = false) => {
		if (!currentShot) {
			setError("Select a shot first.");
			return;
		}
		setError("");
		setRenderLoading(true);
		try {
			const rendered = await endpoints.render(currentShot.id, tryFix);
			setCurrentShot(rendered);
			setShots((prev) => prev.map((x) => (x.id === rendered.id ? rendered : x)));
			if (!rendered.video_url) {
				setError("Render failed. See render log or try AI fix.");
			}
		} catch (e) {
			setError(e.message || String(e));
		} finally {
			setRenderLoading(false);
		}
	};

	const runRegenerate = async () => {
		if (!currentShot) {
			setError("Select a shot first.");
			return;
		}
		setLoading(true);
		setRenderLoading(false);
		setError("");
		try {
			const updated = await endpoints.regenerate(currentShot.id, null);
			setCurrentShot(updated);
			setShots((prev) => prev.map((x) => (x.id === updated.id ? updated : x)));

			// Transition from generate-loading to render-loading cleanly
			setLoading(false);
			setRenderLoading(true);

			const rendered = await endpoints.render(updated.id, false);
			setCurrentShot(rendered);
			setShots((prev) => prev.map((x) => (x.id === rendered.id ? rendered : x)));
			if (!rendered.video_url) {
				setError("Render failed after regeneration. Try Render + AI fix.");
			}
		} catch (e) {
			setError(e.message || String(e));
		} finally {
			// Always clear both states
			setLoading(false);
			setRenderLoading(false);
		}
	};

	const runExport = async () => {
		if (!currentProject) {
			setError("Select a project first.");
			return;
		}
		setExporting(true);
		setError("");
		try {
			const res = await endpoints.exportProject(currentProject.id);
			const url = res.video_url;
			const filename = `${currentProject.name.replace(/[^a-z0-9_.-]/gi, "_") || "project"}-final.mp4`;
			const a = document.createElement("a");
			a.href = url;
			a.download = filename;
			a.style.display = "none";
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
		} catch (e) {
			setError(e.message || String(e));
		} finally {
			setExporting(false);
		}
	};

	const contextValue = {
		prevPrompts,
		setPrevPrompts,
		onSent,
		setRecentPrompt,
		recentPrompt,
		input,
		setInput,
		showResults,
		loading,
		renderLoading,
		exporting,
		resultData,
		newChat,
		error,
		projects,
		currentProject,
		createProject,
		selectProject,
		deleteProject,
		shots,
		currentShot,
		createNewShot,
		selectShot,
		deleteShot,
		runRender,
		runRegenerate,
		runExport,
		refreshShot,
	};

	return (
		<Context.Provider value={contextValue}>{props.children}</Context.Provider>
	);
};

function escapeHtml(s) {
	return String(s)
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;");
}

export default ContextProvider;
