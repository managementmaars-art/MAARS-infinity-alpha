import { useParams } from 'react-router-dom'
import { AgentProfilePage } from '../pages/AgentProfilePage'
import { AgentFollowListPage } from '../pages/AgentFollowListPage'
import { CommunityPage } from '../pages/CommunityPage'
import { PostDetailPage } from '../pages/PostDetailPage'
import { ChatRoomsPage } from '../pages/ChatRoomsPage'

// Wrapper to extract handle param for AgentProfilePage
export function AgentProfileWrapper() {
  const { handle } = useParams<{ handle: string }>()
  return <AgentProfilePage handle={handle ?? ''} />
}

// Wrapper to extract handle param for AgentFollowListPage (following)
export function AgentFollowingWrapper() {
  const { handle } = useParams<{ handle: string }>()
  return <AgentFollowListPage handle={handle ?? ''} type="following" />
}

// Wrapper to extract handle param for AgentFollowListPage (followers)
export function AgentFollowersWrapper() {
  const { handle } = useParams<{ handle: string }>()
  return <AgentFollowListPage handle={handle ?? ''} type="followers" />
}

// Wrapper to extract slug param for CommunityPage
export function CommunityWrapper() {
  const { slug } = useParams<{ slug: string }>()
  return <CommunityPage slug={slug ?? ''} />
}

// Wrapper to extract id param for PostDetailPage
export function PostDetailWrapper() {
  const { id } = useParams<{ id: string }>()
  return <PostDetailPage postId={id ?? ''} />
}

// Chat rooms - no slug (list view)
export function ChatRoomListWrapper() {
  return <ChatRoomsPage />
}

// Chat room - with slug param
export function ChatRoomWrapper() {
  const { slug } = useParams<{ slug: string }>()
  return <ChatRoomsPage slug={slug ?? undefined} />
}
