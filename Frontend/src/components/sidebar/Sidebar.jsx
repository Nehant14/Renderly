import "./sidebar.css";
import { assets } from "../../assets/assets";
import { useContext, useState } from "react";
import { Context } from "../../context/Context";

const Sidebar = () => {
	const [extended, setExtended] = useState(false);
	const {
		onSent,
		prevPrompts,
		setRecentPrompt,
		newChat,
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
		runExport,
		exporting,
	} = useContext(Context);

	const loadPreviousPrompt = async (prompt) => {
		setRecentPrompt(prompt);
		await onSent(prompt);
	};

	return (
		<div className="sidebar">
			<div className="top">
				<img
					src={assets.menu_icon}
					className="menu"
					alt="menu-icon"
					onClick={() => {
						setExtended((prev) => !prev);
					}}
				/>
				<div className="new-chat">
					<img
						src={assets.plus_icon}
						alt=""
						onClick={() => {
							newChat();
						}}
					/>
					{extended ? <p>New chat</p> : null}
				</div>
				{extended ? (
					<div className="recent">
						<p className="recent-title">Projects</p>
						<div
							className="new-chat"
							onClick={() => {
								createProject().catch(console.error);
							}}
						>
							<img src={assets.plus_icon} alt="" />
							<p>New project</p>
						</div>
						{projects.map((p) => (
							<div key={p.id} className="project-block">
								<div
									className={`recent-entry ${currentProject?.id === p.id ? "active" : ""}`}
									onClick={() => selectProject(p.id).catch(console.error)}
								>
									<img src={assets.message_icon} alt="" />
									<p>{p.name.slice(0, 22)}{p.name.length > 22 ? "…" : ""}</p>
								</div>
								<button
									type="button"
									className="icon-btn"
									title="Delete project"
									onClick={(e) => {
										e.stopPropagation();
										deleteProject(p.id).catch(console.error);
									}}
								>
									×
								</button>
							</div>
						))}
						{currentProject ? (
							<>
								<p className="recent-title">Project actions</p>
						<div className="new-chat" style={{ cursor: "default", gap: "0.75rem" }}>
							<button
								type="button"
								className="toolbar-btn"
								onClick={() => {
									runExport().catch(console.error);
								}}
								disabled={!currentProject || exporting}
							>
								{exporting ? "Merging…" : "Merge & Download"}
							</button>
						</div>
						<p className="recent-title">Shots</p>
								<div
									className="new-chat"
									onClick={() => {
										createNewShot().catch(console.error);
									}}
								>
									<img src={assets.plus_icon} alt="" />
									<p>New shot</p>
								</div>
								{shots.map((s) => (
									<div key={s.id} className="project-block">
										<div
											className={`recent-entry ${currentShot?.id === s.id ? "active" : ""}`}
											onClick={() => selectShot(s).catch(console.error)}
										>
											<img src={assets.code_icon} alt="" />
											<p>
												{s.title.slice(0, 18)}
												{s.title.length > 18 ? "…" : ""}
											</p>
										</div>
										<button
											type="button"
											className="icon-btn"
											title="Delete shot"
											onClick={(e) => {
												e.stopPropagation();
												deleteShot(s.id).catch(console.error);
											}}
										>
											×
										</button>
									</div>
								))}
							</>
						) : null}
						<p className="recent-title">Recent prompts</p>
						{prevPrompts.map((item, index) => {
							return (
								<div
									key={`${item}-${index}`}
									onClick={() => {
										loadPreviousPrompt(item);
									}}
									className="recent-entry"
								>
									<img src={assets.message_icon} alt="" />
									<p>{item.slice(0, 18)}...</p>
								</div>
							);
						})}
					</div>
				) : null}
			</div>
			<div className="bottom">
				<div className="bottom-item recent-entry">
					<img src={assets.question_icon} alt="" />
					{extended ? <p>Help desk</p> : null}
				</div>
				<div className="bottom-item recent-entry">
					<img src={assets.history_icon} alt="" />
					{extended ? <p>History</p> : null}
				</div>
				<div className="bottom-item recent-entry">
					<img src={assets.setting_icon} alt="" />
					{extended ? <p>Settings</p> : null}
				</div>
			</div>
		</div>
	);
};

export default Sidebar;
