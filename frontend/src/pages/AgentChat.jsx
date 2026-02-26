import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { ScrollArea } from "../components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { 
  Bot, Send, Plus, ArrowLeft, MessageSquare, Trash2,
  LayoutDashboard, Users, ListTodo, Settings, LogOut, Menu, X,
  Paperclip, Image, FileText, Sparkles
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const AVAILABLE_MODELS = [
  { provider: "auto", model: "auto", name: "Auto (Smart Selection)" },
  { provider: "openai", model: "gpt-5.2", name: "GPT-5.2 (Best)" },
  { provider: "openai", model: "gpt-4o", name: "GPT-4o" },
  { provider: "openai", model: "o3", name: "O3 (Reasoning)" },
  { provider: "anthropic", model: "claude-sonnet-4-5-20250929", name: "Claude Sonnet 4.5" },
  { provider: "anthropic", model: "claude-opus-4-5-20251101", name: "Claude Opus 4.5" },
  { provider: "gemini", model: "gemini-3-flash-preview", name: "Gemini 3 Flash" },
  { provider: "gemini", model: "gemini-3-pro-preview", name: "Gemini 3 Pro" },
];

const AgentChat = () => {
  const navigate = useNavigate();
  const { agentId } = useParams();
  const [searchParams] = useSearchParams();
  const chatIdParam = searchParams.get("chat");
  
  const { user, logout, token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [chats, setChats] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState("openai/gpt-5.2");
  const [attachments, setAttachments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (agentId && agents.length > 0) {
      const agent = agents.find(a => a.agent_id === agentId);
      if (agent) {
        setSelectedAgent(agent);
        if (chatIdParam) {
          loadChat(chatIdParam);
        }
      }
    }
  }, [agentId, agents, chatIdParam]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchInitialData = async () => {
    try {
      const [agentsRes, chatsRes] = await Promise.all([
        fetch(`${API}/agents`, { credentials: "include", headers }),
        fetch(`${API}/chats`, { credentials: "include", headers })
      ]);

      if (agentsRes.ok) {
        const agentsData = await agentsRes.json();
        setAgents(agentsData);
        if (!agentId && agentsData.length > 0) {
          setSelectedAgent(agentsData[0]);
        }
      }
      if (chatsRes.ok) setChats(await chatsRes.json());
    } catch (error) {
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const loadChat = async (chatId) => {
    try {
      const response = await fetch(`${API}/chats/${chatId}`, {
        credentials: "include",
        headers
      });
      if (response.ok) {
        const chat = await response.json();
        setCurrentChat(chat);
        setMessages(chat.messages || []);
        const agent = agents.find(a => a.agent_id === chat.agent_id);
        if (agent) setSelectedAgent(agent);
      }
    } catch (error) {
      toast.error("Failed to load chat");
    }
  };

  const startNewChat = async () => {
    if (!selectedAgent) return;
    
    try {
      const response = await fetch(`${API}/chats`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ agent_id: selectedAgent.agent_id })
      });

      if (response.ok) {
        const chat = await response.json();
        setCurrentChat(chat);
        setMessages([]);
        setChats(prev => [chat, ...prev]);
        navigate(`/chat/${selectedAgent.agent_id}?chat=${chat.chat_id}`, { replace: true });
      }
    } catch (error) {
      toast.error("Failed to create chat");
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    // Create chat if needed
    let chatId = currentChat?.chat_id;
    if (!chatId) {
      try {
        const response = await fetch(`${API}/chats`, {
          method: "POST",
          headers: { ...headers, "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ agent_id: selectedAgent.agent_id })
        });
        if (response.ok) {
          const chat = await response.json();
          chatId = chat.chat_id;
          setCurrentChat(chat);
          setChats(prev => [chat, ...prev]);
        } else {
          toast.error("Failed to create chat");
          return;
        }
      } catch (error) {
        toast.error("Failed to create chat");
        return;
      }
    }

    setSending(true);
    const [provider, model] = selectedModel.split("/");
    const userMessage = { 
      role: "user", 
      content: input, 
      message_id: `temp_${Date.now()}`,
      attachments: attachments.map(a => a.preview),
      model_used: selectedModel
    };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setAttachments([]);

    try {
      const response = await fetch(`${API}/chats/${chatId}/messages`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ 
          content: userMessage.content,
          model_provider: provider,
          model_name: model,
          attachments: userMessage.attachments
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [
          ...prev.slice(0, -1),
          data.user_message,
          data.assistant_message
        ]);
        // Update chat title in list if it changed
        setChats(prev => prev.map(c => 
          c.chat_id === chatId 
            ? { ...c, title: data.user_message.content.slice(0, 50) }
            : c
        ));
      } else {
        toast.error("Failed to send message");
        setMessages(prev => prev.slice(0, -1));
      }
    } catch (error) {
      toast.error("Failed to send message");
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setUploading(true);
    
    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API}/upload`, {
          method: "POST",
          headers: headers,
          credentials: "include",
          body: formData
        });

        if (response.ok) {
          const data = await response.json();
          setAttachments(prev => [...prev, {
            filename: data.filename,
            type: data.content_type,
            size: data.size,
            preview: data.data_url
          }]);
          toast.success(`${file.name} uploaded`);
        } else {
          toast.error(`Failed to upload ${file.name}`);
        }
      } catch (error) {
        toast.error(`Failed to upload ${file.name}`);
      }
    }
    
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeAttachment = (index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const deleteChat = async (chatId) => {
    try {
      const response = await fetch(`${API}/chats/${chatId}`, {
        method: "DELETE",
        credentials: "include",
        headers
      });

      if (response.ok) {
        setChats(prev => prev.filter(c => c.chat_id !== chatId));
        if (currentChat?.chat_id === chatId) {
          setCurrentChat(null);
          setMessages([]);
        }
        toast.success("Chat deleted");
      }
    } catch (error) {
      toast.error("Failed to delete chat");
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const NavItem = ({ icon: Icon, label, to, active }) => (
    <Link
      to={to}
      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
        active 
          ? "bg-indigo-500/20 text-indigo-400" 
          : "text-zinc-400 hover:bg-white/5 hover:text-white"
      }`}
      data-testid={`nav-${label.toLowerCase()}`}
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
    </Link>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex" data-testid="chat-page">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="flex items-center justify-between h-16 px-4">
          <button onClick={() => setSidebarOpen(true)} className="p-2 text-zinc-400">
            <Menu className="w-6 h-6" />
          </button>
          <span className="font-semibold text-white">
            {selectedAgent?.name || "Chat"}
          </span>
          <Button
            size="sm"
            variant="ghost"
            onClick={startNewChat}
            className="text-indigo-400"
            data-testid="mobile-new-chat-btn"
          >
            <Plus className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Mobile Sidebar */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-80 bg-zinc-900 border-r border-white/10 flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-white/10">
              <Link to="/dashboard" className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white font-['Outfit']">MAARS Global Corporation</span>
              </Link>
              <button onClick={() => setSidebarOpen(false)} className="p-2 text-zinc-400">
                <X className="w-5 h-5" />
              </button>
            </div>
            <SidebarContent 
              agents={agents}
              chats={chats}
              selectedAgent={selectedAgent}
              setSelectedAgent={setSelectedAgent}
              currentChat={currentChat}
              loadChat={loadChat}
              deleteChat={deleteChat}
              startNewChat={startNewChat}
              navigate={navigate}
            />
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <div className="hidden lg:flex w-80 bg-zinc-900/50 border-r border-white/10 flex-col">
        <div className="p-4 border-b border-white/10">
          <Link to="/dashboard" className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white font-['Outfit']">MAARS Global Corporation</span>
          </Link>
          <Button
            onClick={startNewChat}
            className="w-full bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
            data-testid="new-chat-btn"
          >
            <Plus className="w-4 h-4 mr-2" /> New Chat
          </Button>
        </div>
        <SidebarContent 
          agents={agents}
          chats={chats}
          selectedAgent={selectedAgent}
          setSelectedAgent={setSelectedAgent}
          currentChat={currentChat}
          loadChat={loadChat}
          deleteChat={deleteChat}
          startNewChat={startNewChat}
          navigate={navigate}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col pt-16 lg:pt-0">
        {/* Agent Header */}
        {selectedAgent && (
          <div className="hidden lg:flex items-center gap-4 p-4 border-b border-white/10">
            <img
              src={selectedAgent.avatar}
              alt={selectedAgent.name}
              className="w-10 h-10 rounded-lg object-cover"
            />
            <div>
              <h2 className="font-semibold text-white">{selectedAgent.name}</h2>
              <p className="text-sm text-zinc-400">{selectedAgent.role}</p>
            </div>
          </div>
        )}

        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
              {selectedAgent && (
                <>
                  <img
                    src={selectedAgent.avatar}
                    alt={selectedAgent.name}
                    className="w-20 h-20 rounded-xl object-cover mb-4"
                  />
                  <h3 className="text-xl font-semibold text-white mb-2 font-['Outfit']">
                    Chat with {selectedAgent.name}
                  </h3>
                  <p className="text-zinc-400 max-w-md mb-4">{selectedAgent.description}</p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {selectedAgent.capabilities?.map((cap, i) => (
                      <span key={i} className="px-3 py-1 text-sm rounded-full bg-white/10 text-zinc-300">
                        {cap}
                      </span>
                    ))}
                  </div>
                </>
              )}
            </div>
          ) : (
            <div className="space-y-4 max-w-3xl mx-auto">
              {messages.map((msg, i) => (
                <div
                  key={msg.message_id || i}
                  className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
                  data-testid={`message-${i}`}
                >
                  {msg.role === "assistant" && (
                    <img
                      src={selectedAgent?.avatar}
                      alt=""
                      className="w-8 h-8 rounded-lg object-cover flex-shrink-0"
                    />
                  )}
                  <div
                    className={`max-w-[80%] p-4 rounded-xl ${
                      msg.role === "user"
                        ? "bg-indigo-500/20 text-white"
                        : "bg-zinc-800/50 text-zinc-100"
                    }`}
                  >
                    {msg.attachments?.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-2">
                        {msg.attachments.map((att, idx) => (
                          att?.startsWith("data:image") ? (
                            <img key={idx} src={att} alt="attachment" className="max-w-[200px] rounded-lg" />
                          ) : (
                            <div key={idx} className="px-2 py-1 bg-white/10 rounded text-xs">File attached</div>
                          )
                        ))}
                      </div>
                    )}
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    {msg.model_used && (
                      <p className="text-xs text-zinc-500 mt-2 flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        {msg.model_used}
                      </p>
                    )}
                  </div>
                  {msg.role === "user" && (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-sm font-semibold">
                        {user?.name?.charAt(0) || "U"}
                      </span>
                    </div>
                  )}
                </div>
              ))}
              {sending && (
                <div className="flex gap-3">
                  <img
                    src={selectedAgent?.avatar}
                    alt=""
                    className="w-8 h-8 rounded-lg object-cover"
                  />
                  <div className="bg-zinc-800/50 p-4 rounded-xl">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" />
                      <span className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                      <span className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>

        {/* Input */}
        <div className="p-4 border-t border-white/10">
          {/* Attachments Preview */}
          {attachments.length > 0 && (
            <div className="max-w-3xl mx-auto mb-3 flex flex-wrap gap-2">
              {attachments.map((att, idx) => (
                <div key={idx} className="relative group">
                  {att.type?.startsWith("image/") ? (
                    <img src={att.preview} alt={att.filename} className="w-16 h-16 object-cover rounded-lg" />
                  ) : (
                    <div className="w-16 h-16 bg-zinc-800 rounded-lg flex items-center justify-center">
                      <FileText className="w-6 h-6 text-zinc-400" />
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={() => removeAttachment(idx)}
                    className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3 text-white" />
                  </button>
                  <p className="text-xs text-zinc-500 truncate w-16 mt-1">{att.filename}</p>
                </div>
              ))}
            </div>
          )}
          
          {/* Model Selector */}
          <div className="max-w-3xl mx-auto mb-3 flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span className="text-xs text-zinc-400">Model:</span>
            </div>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="w-[200px] h-8 text-xs bg-zinc-900/50 border-white/10" data-testid="model-selector">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {AVAILABLE_MODELS.map((m) => (
                  <SelectItem key={`${m.provider}/${m.model}`} value={`${m.provider}/${m.model}`}>
                    {m.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <span className="text-xs text-zinc-500">No limits • Switch anytime</span>
          </div>

          <form onSubmit={sendMessage} className="max-w-3xl mx-auto flex gap-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              multiple
              className="hidden"
              accept="image/*,.pdf,.doc,.docx,.txt,.csv,.xlsx"
            />
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="border-white/10 hover:bg-white/5"
              data-testid="attach-file-btn"
            >
              {uploading ? (
                <div className="w-4 h-4 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
              ) : (
                <Paperclip className="w-4 h-4" />
              )}
            </Button>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Message ${selectedAgent?.name || "AI"}...`}
              className="flex-1 bg-zinc-900/50 border-white/10 focus:border-indigo-500"
              disabled={sending || !selectedAgent}
              data-testid="chat-input"
            />
            <Button
              type="submit"
              disabled={sending || !input.trim() || !selectedAgent}
              className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
              data-testid="send-message-btn"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Sidebar Content Component
const SidebarContent = ({ 
  agents, chats, selectedAgent, setSelectedAgent, 
  currentChat, loadChat, deleteChat, startNewChat, navigate 
}) => (
  <div className="flex-1 flex flex-col overflow-hidden">
    {/* Agents */}
    <div className="p-4 border-b border-white/10">
      <p className="text-xs font-semibold text-zinc-500 uppercase mb-2">Agents</p>
      <div className="flex gap-2 overflow-x-auto pb-2">
        {agents.slice(0, 6).map((agent) => (
          <button
            key={agent.agent_id}
            onClick={() => {
              setSelectedAgent(agent);
              navigate(`/chat/${agent.agent_id}`);
            }}
            className={`flex-shrink-0 p-2 rounded-lg transition-colors ${
              selectedAgent?.agent_id === agent.agent_id
                ? "bg-indigo-500/20 ring-1 ring-indigo-500"
                : "bg-zinc-800/50 hover:bg-zinc-800"
            }`}
            title={agent.name}
            data-testid={`agent-btn-${agent.agent_id}`}
          >
            <img
              src={agent.avatar}
              alt={agent.name}
              className="w-8 h-8 rounded object-cover"
            />
          </button>
        ))}
      </div>
    </div>

    {/* Chat History */}
    <ScrollArea className="flex-1">
      <div className="p-4">
        <p className="text-xs font-semibold text-zinc-500 uppercase mb-2">Recent Chats</p>
        <div className="space-y-1">
          {chats.map((chat) => (
            <div
              key={chat.chat_id}
              className={`group flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                currentChat?.chat_id === chat.chat_id
                  ? "bg-indigo-500/20"
                  : "hover:bg-white/5"
              }`}
              onClick={() => {
                loadChat(chat.chat_id);
                navigate(`/chat/${chat.agent_id}?chat=${chat.chat_id}`);
              }}
              data-testid={`chat-item-${chat.chat_id}`}
            >
              <MessageSquare className="w-4 h-4 text-zinc-500 flex-shrink-0" />
              <span className="flex-1 text-sm text-zinc-300 truncate">{chat.title}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteChat(chat.chat_id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 text-zinc-500 hover:text-red-400 transition-opacity"
                data-testid={`delete-chat-${chat.chat_id}`}
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
          {chats.length === 0 && (
            <p className="text-sm text-zinc-500 text-center py-4">No chats yet</p>
          )}
        </div>
      </div>
    </ScrollArea>

    {/* Navigation */}
    <div className="p-4 border-t border-white/10 space-y-1">
      <Link
        to="/dashboard"
        className="flex items-center gap-3 px-3 py-2 rounded-lg text-zinc-400 hover:bg-white/5 hover:text-white transition-colors"
      >
        <LayoutDashboard className="w-4 h-4" />
        <span className="text-sm">Dashboard</span>
      </Link>
      <Link
        to="/agents"
        className="flex items-center gap-3 px-3 py-2 rounded-lg text-zinc-400 hover:bg-white/5 hover:text-white transition-colors"
      >
        <Users className="w-4 h-4" />
        <span className="text-sm">All Agents</span>
      </Link>
      <Link
        to="/tasks"
        className="flex items-center gap-3 px-3 py-2 rounded-lg text-zinc-400 hover:bg-white/5 hover:text-white transition-colors"
      >
        <ListTodo className="w-4 h-4" />
        <span className="text-sm">Tasks</span>
      </Link>
    </div>
  </div>
);

export default AgentChat;
