import { Routes, Route } from "react-router-dom";
import CommandCenter from "../components/projects/CommandCenter";
import ProjectDetail from "../components/projects/ProjectDetail";
import ProjectsLayout from "../components/projects/ProjectsLayout";

const Projects = () => (
  <ProjectsLayout>
    <Routes>
      <Route path="/" element={<CommandCenter />} />
      <Route path="/:projectId" element={<ProjectDetail />} />
    </Routes>
  </ProjectsLayout>
);

export default Projects;
