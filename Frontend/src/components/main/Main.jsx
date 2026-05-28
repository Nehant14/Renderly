import { useContext } from "react";
import { assets } from "../../assets/assets";
import "./main.css";
import { Context } from "../../context/Context";

const Main = () => {
	const {
		onSent,
		recentPrompt,
		showResults,
		loading,
		renderLoading,
		exporting,
		resultData,
		setInput,
		input,
		error,
		currentShot,
		currentProject,
		runRender,
		runRegenerate,
		runExport,
	} = useContext(Context);

	{/* Main prompt function */}
	const handleCardClick = (promptText) => {
		setInput(promptText);
	};

	const handleKeyDown = (e) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			onSent();
		}
	};

	const busy = loading || renderLoading;

	return (
		<div className="main">
			<div className="nav">
				<p>Renderly</p>
			</div>
			<div className="main-container">
				{!showResults ? (
					<>
						<div className="greet">
							<p>
								<span>Hello , Animator </span>
							</p>
							<p>How Can i Help You Today?</p>
						</div>
						
					</>
				) : (
					<div className="result">
						<div className="result-title">
							<img src={assets.user} alt="" />
							<p>{recentPrompt}</p>
						</div>
						{currentShot?.video_url ? (
							<div className="video-preview">
								<video
									key={currentShot.video_url}
									src={currentShot.video_url}
									controls
									playsInline
								/>
							</div>
						) : null}
						{error ? (
							<p className="inline-error" role="alert">
								{error}
							</p>
						) : null}
						<div className="shot-toolbar">
							<button
								type="button"
								className="toolbar-btn"
								disabled={!currentShot || busy}
								onClick={() => runRender(false)}
							>
								{renderLoading ? "Rendering…" : "Render"}
							</button>
							<button
								type="button"
								className="toolbar-btn"
								disabled={!currentShot || busy}
								onClick={() => runRender(true)}
							>
								Render + AI fix
							</button>
							<button
								type="button"
								className="toolbar-btn"
								disabled={!currentShot || busy}
								onClick={() => runRegenerate()}
							>
								Regenerate
							</button>
							<button
								type="button"
								className="toolbar-btn"
								disabled={!currentProject || exporting || busy}
								onClick={() => runExport()}
							>
								{exporting ? "Exporting…" : "Export project"}
							</button>
						</div>
						<div className="result-data">
							<img src={assets.gemini_icon} alt="" />
							{loading || renderLoading ? (
								<div className="loader">
									<hr />
									<hr />
									<hr />
									<p className="status-hint">
										{loading ? "Generating Manim code…" : "Rendering video…"}
									</p>
								</div>
							) : (
								<div
									className="result-html"
									dangerouslySetInnerHTML={{ __html: resultData }}
								/>
							)}
						</div>
					</div>
				)}

				<div className="main-bottom">
					<div className="search-box">
						<input
							onChange={(e) => {
								setInput(e.target.value);
							}}
							onKeyDown={handleKeyDown}
							value={input}
							type="text"
							placeholder="Describe the animation (select a project in the sidebar)"
							disabled={busy}
						/>
						<div>
							<img
								src={assets.send_icon}
								alt=""
								onClick={() => {
									if (!busy) onSent();
								}}
							/>
						</div>
					</div>
					<div className="bottom-info">
						<p>Renderly — Manim studio</p>
					</div>
				</div>
			</div>
		</div>
	);
};

export default Main;
