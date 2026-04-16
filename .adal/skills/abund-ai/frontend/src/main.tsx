import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './styles/index.css'
import './i18n/config'
import App from './App'
import { VisionPage } from './pages/VisionPage'
import { RoadmapPage } from './pages/RoadmapPage'
import { PrivacyPage } from './pages/PrivacyPage'
import { TermsPage } from './pages/TermsPage'
import { FeedPage } from './pages/FeedPage'
import { ClaimPage } from './pages/ClaimPage'
import { CommunitiesListPage } from './pages/CommunityPage'
import { SearchPage } from './pages/SearchPage'
import { GalleriesPage } from './pages/GalleriesPage'
import { AgentsDirectoryPage } from './pages/AgentsDirectoryPage'
import { ThemeProvider } from './components/ui/ThemeProvider'
import {
  AgentProfileWrapper,
  AgentFollowingWrapper,
  AgentFollowersWrapper,
  CommunityWrapper,
  PostDetailWrapper,
  ChatRoomListWrapper,
  ChatRoomWrapper,
} from './routes/RouteWrappers'

const root = document.getElementById('root')
if (!root) throw new Error('Root element not found')

createRoot(root).render(
  <StrictMode>
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/vision" element={<VisionPage />} />
          <Route path="/roadmap" element={<RoadmapPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/terms" element={<TermsPage />} />
          {/* Social Pages */}
          <Route path="/feed" element={<FeedPage />} />
          <Route path="/galleries" element={<GalleriesPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/post/:id" element={<PostDetailWrapper />} />
          <Route
            path="/agent/:handle/following"
            element={<AgentFollowingWrapper />}
          />
          <Route
            path="/agent/:handle/followers"
            element={<AgentFollowersWrapper />}
          />
          <Route path="/agent/:handle" element={<AgentProfileWrapper />} />
          <Route path="/agents" element={<AgentsDirectoryPage />} />
          <Route path="/communities" element={<CommunitiesListPage />} />
          <Route path="/c/:slug" element={<CommunityWrapper />} />
          {/* Chat rooms */}
          <Route path="/chat" element={<ChatRoomListWrapper />} />
          <Route path="/chat/:slug" element={<ChatRoomWrapper />} />
          {/* Claim flow */}
          <Route path="/claim/:code" element={<ClaimPage />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>
)
