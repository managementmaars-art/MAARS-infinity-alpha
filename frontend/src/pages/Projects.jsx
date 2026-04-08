import { Routes, Route } from "react-router-dom";
import CommandCenter from "../components/projects/CommandCenter";
import ProjectDetail from "../components/projects/ProjectDetail";

// ProjectsLayout is intentionally NOT used here — DashboardLayout already provides
// the sidebar and page frame. Wrapping again caused a double-sidebar overlap.
const Projects = () => (
  <Routes>
    <Route path="/" element={<CommandCenter />} />
    <Route path="/:projectId" element={<ProjectDetail />} />
  </Routes>
);

export default Projects;
