import { Routes, Route } from "react-router-dom";
import CommandCenter from "../components/projects/CommandCenter";
import ProjectDetail from "../components/projects/ProjectDetail";

const Projects = () => (
  <Routes>
    <Route path="/" element={<CommandCenter />} />
    <Route path="/:projectId" element={<ProjectDetail />} />
  </Routes>
);

export default Projects;
