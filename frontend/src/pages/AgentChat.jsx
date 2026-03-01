import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { ScrollArea } from "../components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Bot, Send, Plus, ArrowLeft, MessageSquare, Trash2,
  LayoutDashboard, Users, ListTodo, Settings, LogOut, Menu, X,
  Paperclip, Image, FileText, Sparkles, Mic, MicOff, Loader2,
  Download, Film, FileSpreadsheet, File, Volume2, VolumeX,
  Search, Calculator, ClipboardList, BarChart3, Wrench, ChevronDown, ChevronRight, Brain, Zap,
  Mail, MessageCircle, Phone, Github, Table, Calendar, Share2, ThumbsUp, ThumbsDown
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const AVAILABLE_MODELS = [
  { provider: "auto", model: "auto", name: "Auto (Smart Selection)", category: "auto" },
  // OpenAI
  { provider: "openai", model: "gpt-5.2", name: "GPT-5.2", category: "flagship" },
  { provider: "openai", model: "gpt-4o", name: "GPT-4o", category: "fast" },
  { provider: "openai", model: "gpt-4o-mini", name: "GPT-4o Mini", category: "economy" },
  { provider: "openai", model: "o3", name: "O3 (Reasoning)", category: "reasoning" },
  { provider: "openai", model: "o3-mini", name: "O3 Mini", category: "reasoning" },
  // Anthropic
  { provider: "anthropic", model: "claude-sonnet-4-5-20250929", name: "Claude Sonnet 4.5", category: "flagship" },
  { provider: "anthropic", model: "claude-opus-4-5-20251101", name: "Claude Opus 4.5", category: "premium" },
  { provider: "anthropic", model: "claude-haiku-4-5-20250929", name: "Claude Haiku 4.5", category: "economy" },
  // Google
  { provider: "gemini", model: "gemini-3-flash-preview", name: "Gemini 3 Flash", category: "fast" },
  { provider: "gemini", model: "gemini-3-pro-preview", name: "Gemini 3 Pro", category: "flagship" },
  // xAI Grok
  { provider: "xai", model: "grok-3", name: "Grok 3", category: "flagship" },
  { provider: "xai", model: "grok-3-mini", name: "Grok 3 Mini", category: "economy" },
  { provider: "xai", model: "grok-2", name: "Grok 2", category: "fast" },
  // DeepSeek
  { provider: "deepseek", model: "deepseek-chat", name: "DeepSeek Chat", category: "economy" },
  { provider: "deepseek", model: "deepseek-reasoner", name: "DeepSeek Reasoner", category: "reasoning" },
  // Mistral
  { provider: "mistral", model: "mistral-large-latest", name: "Mistral Large", category: "flagship" },
  { provider: "mistral", model: "mistral-medium-latest", name: "Mistral Medium", category: "fast" },
  { provider: "mistral", model: "mistral-small-latest", name: "Mistral Small", category: "economy" },
  // Perplexity
  { provider: "perplexity", model: "sonar", name: "Perplexity Sonar", category: "search" },
  { provider: "perplexity", model: "sonar-pro", name: "Perplexity Sonar Pro", category: "search" },
  // Cohere
  { provider: "cohere", model: "command-r-plus", name: "Cohere Command R+", category: "flagship" },
  { provider: "cohere", model: "command-r", name: "Cohere Command R", category: "fast" },
];

import NotificationCenter from "../components/NotificationCenter";
import AgentCustomizePanel from "../components/AgentCustomizePanel";
import MarkdownRenderer from "../components/MarkdownRenderer";

// Commander Group Chat Component - renders delegation as individual agent chat bubbles
const CommanderGroupChat = ({ msg, msgIndex, generatedFiles, generateFile, generatingFile, currentAgent }) => {
  const data = msg.delegation_data;
  const priorityColors = {
    high: "bg-red-500/20 text-red-400 border-red-500/30",
    medium: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    low: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  };

  return (
    <div className="space-y-3" data-testid={`commander-group-${msgIndex}`}>
      {/* Commander header card */}
      <div className="flex gap-3" data-testid={`message-${msgIndex}`}>
        <img
          src={currentAgent?.avatar}
          alt="Commander"
          className="w-8 h-8 rounded-lg object-cover flex-shrink-0"
        />
        <div className="flex-1 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-semibold text-amber-400 text-sm">Commander Orion</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">MISSION BRIEFING</span>
          </div>
          <p className="text-zinc-200 text-sm font-medium mb-1">Goal: {data.goal}</p>
          <p className="text-zinc-400 text-xs">{data.task_count} specialists deployed &middot; {data.task_count} tasks created</p>
          
          {/* Agent avatars row */}
          <div className="flex items-center gap-1 mt-3">
            {data.agents.map((a, idx) => (
              <div key={idx} className="relative group">
                <img
                  src={a.agent_avatar}
                  alt={a.agent_name}
                  className="w-7 h-7 rounded-full object-cover ring-2 ring-zinc-800 -ml-1 first:ml-0 hover:ring-indigo-500 transition-all hover:z-10 hover:scale-110"
                  title={a.agent_name}
                />
              </div>
            ))}
            <span className="text-xs text-zinc-500 ml-2">{data.agents.length} active</span>
          </div>
        </div>
      </div>

      {/* Individual agent responses */}
      {data.agents.map((agent, idx) => (
        <div key={idx} className="flex gap-3 ml-6 animate-in fade-in slide-in-from-left-2" style={{ animationDelay: `${idx * 100}ms` }} data-testid={`delegation-agent-${idx}`}>
          <div className="relative flex-shrink-0">
            <img
              src={agent.agent_avatar}
              alt={agent.agent_name}
              className="w-8 h-8 rounded-lg object-cover"
            />
            <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-zinc-900 ${agent.status === "completed" ? "bg-emerald-500" : "bg-red-500"}`} />
          </div>
          <div className="flex-1 rounded-xl bg-zinc-800/60 border border-white/5 p-4 hover:border-white/10 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-white text-sm">{agent.agent_name}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-zinc-400">{agent.agent_role}</span>
              </div>
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${priorityColors[agent.priority]}`}>
                {agent.priority.toUpperCase()}
              </span>
            </div>
            <div className="text-xs text-indigo-300/80 mb-2 flex items-center gap-1">
              <ListTodo className="w-3 h-3" />
              {agent.task_title || agent.task}
            </div>
            <MarkdownRenderer content={agent.response} />
          </div>
        </div>
      ))}

      {/* Commander summary footer */}
      <div className="flex gap-3 ml-6">
        <div className="w-8 flex-shrink-0 flex justify-center">
          <div className="w-px h-full bg-amber-500/20" />
        </div>
        <div className="flex-1 rounded-lg bg-zinc-900/50 border border-white/5 p-3">
          <p className="text-xs text-zinc-400">
            All specialists have reported. <span className="text-amber-400 font-medium">{data.task_count} tasks</span> auto-created on your Tasks page.
          </p>
        </div>
      </div>
    </div>
  );
};

// Execution Steps Component - shows agent's reasoning and tool usage
const ExecutionSteps = ({ steps }) => {
  const [expanded, setExpanded] = useState(false);
  if (!steps || steps.length === 0) return null;
  
  const toolIcons = { web_search: Search, calculate: Calculator, create_task: ClipboardList, analyze_data: BarChart3, send_slack: MessageCircle, send_email: Mail, send_sms: Phone, github_action: Github, airtable_action: Table, search_gif: Image, schedule_meeting: Calendar, google_calendar: Calendar, send_gmail: Mail };
  const toolLabels = { web_search: "Web Search", calculate: "Calculate", create_task: "Create Task", analyze_data: "Analyze Data", send_slack: "Slack Message", send_email: "Send Email", send_sms: "Send SMS", github_action: "GitHub", airtable_action: "Airtable", search_gif: "GIF Search", schedule_meeting: "Schedule", google_calendar: "Calendar", send_gmail: "Gmail" };
  
  return (
    <div className="mb-2" data-testid="execution-steps">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-xs text-amber-400/80 hover:text-amber-300 transition-colors"
        data-testid="toggle-execution-steps"
      >
        <Brain className="w-3 h-3" />
        <span className="font-medium">{steps.length} reasoning step{steps.length > 1 ? 's' : ''}</span>
        {expanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
      </button>
      {expanded && (
        <div className="mt-2 space-y-1.5 pl-2 border-l-2 border-amber-500/20">
          {steps.map((step, idx) => {
            if (step.step_type === "thinking") {
              return (
                <div key={idx} className="flex items-start gap-2 text-xs" data-testid={`step-thinking-${idx}`}>
                  <Brain className="w-3 h-3 text-indigo-400 mt-0.5 shrink-0" />
                  <p className="text-zinc-400 italic">{step.content}</p>
                </div>
              );
            }
            if (step.step_type === "tool_call") {
              const ToolIcon = toolIcons[step.tool_name] || Wrench;
              return (
                <div key={idx} className="flex items-start gap-2 text-xs" data-testid={`step-tool-call-${idx}`}>
                  <Zap className="w-3 h-3 text-amber-400 mt-0.5 shrink-0" />
                  <div>
                    <span className="text-amber-400 font-medium">Using {toolLabels[step.tool_name] || step.tool_name}</span>
                    <span className="text-zinc-500 ml-1">
                      {step.tool_input?.query || step.tool_input?.expression || step.tool_input?.title || ''}
                    </span>
                  </div>
                </div>
              );
            }
            if (step.step_type === "tool_result") {
              return (
                <div key={idx} className="text-xs p-2 rounded bg-white/5 border border-white/5" data-testid={`step-tool-result-${idx}`}>
                  <p className="text-emerald-400/80 font-mono text-[10px] leading-relaxed whitespace-pre-wrap line-clamp-4">{step.content}</p>
                </div>
              );
            }
            return null;
          })}
        </div>
      )}
    </div>
  );
};

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
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const [isResizing, setIsResizing] = useState(false);
  const [selectedModel, setSelectedModel] = useState("auto/auto");
  const [attachments, setAttachments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [generatingFile, setGeneratingFile] = useState(null);
  const [generatedFiles, setGeneratedFiles] = useState({});
  const [ttsPlaying, setTtsPlaying] = useState(null);
  const [ttsLoading, setTtsLoading] = useState(null);
  const [feedbackState, setFeedbackState] = useState({});
  const [showCustomize, setShowCustomize] = useState(false);
  const ttsAudioRef = useRef(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const resizeRef = useRef(null);
  const textareaRef = useRef(null);

  // Sidebar resize handlers
  const startResize = (e) => {
    e.preventDefault();
    setIsResizing(true);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      const newWidth = Math.min(Math.max(e.clientX, 200), 600);
      setSidebarWidth(newWidth);
    };
    const handleMouseUp = () => {
      if (isResizing) {
        setIsResizing(false);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    };
    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const playTTS = async (msgId, text) => {
    if (ttsPlaying === msgId) {
      if (ttsAudioRef.current) { ttsAudioRef.current.pause(); ttsAudioRef.current = null; }
      setTtsPlaying(null);
      return;
    }
    setTtsLoading(msgId);
    try {
      const res = await fetch(`${API}/tts/generate`, {
        method: "POST", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.substring(0, 4000), voice: "nova" })
      });
      if (!res.ok) { const e = await res.json(); toast.error(e.detail || "TTS failed"); return; }
      const data = await res.json();
      if (ttsAudioRef.current) ttsAudioRef.current.pause();
      const audio = new Audio(data.audio_url);
      ttsAudioRef.current = audio;
      audio.onended = () => { setTtsPlaying(null); ttsAudioRef.current = null; };
      audio.play();
      setTtsPlaying(msgId);
    } catch { toast.error("TTS not available"); }
    finally { setTtsLoading(null); }
  };

  // Initialize feedback state from loaded messages
  const initFeedback = (msgs) => {
    const fb = {};
    msgs.forEach(m => { if (m.feedback) fb[m.message_id] = m.feedback; });
    setFeedbackState(fb);
  };

  const submitFeedback = async (chatId, messageId, type) => {
    const current = feedbackState[messageId];
    const newFeedback = current === type ? null : type;
    setFeedbackState(prev => ({ ...prev, [messageId]: newFeedback }));
    try {
      await fetch(`${API}/chats/${chatId}/messages/${messageId}/feedback`, {
        method: "POST", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ feedback: newFeedback })
      });
    } catch {}
  };

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

  // Poll for background video generation completion
  useEffect(() => {
    const hasGenerating = messages.some(m => m.video_generating && !m.generated_video);
    const activeChatId = currentChat?.chat_id;
    if (!hasGenerating || !activeChatId) return;
    
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/chats/${activeChatId}`, { headers });
        if (res.ok) {
          const chat = await res.json();
          const updated = chat.messages || [];
          const changed = updated.some(m => m.generated_video && !m.video_generating);
          if (changed) {
            setMessages(updated);
            updated.forEach(m => {
              if (m.generated_video) {
                setGeneratedFiles(prev => ({ ...prev, [`${m.message_id}_video`]: m.generated_video }));
              }
            });
          }
          if (!updated.some(m => m.video_generating)) clearInterval(interval);
        }
      } catch {}
    }, 10000);
    
    return () => clearInterval(interval);
  }, [messages, currentChat]);

  // Poll for Commander delegation completion
  useEffect(() => {
    const hasProcessing = messages.some(m => m.commander_status === "processing");
    const activeChatId = currentChat?.chat_id;
    if (!hasProcessing || !activeChatId) return;
    
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/chats/${activeChatId}`, { headers });
        if (res.ok) {
          const chat = await res.json();
          const updated = chat.messages || [];
          const complete = updated.some(m => m.commander_status === "complete" || m.commander_status === "error");
          if (complete) {
            setMessages(updated);
            clearInterval(interval);
          }
        }
      } catch {}
    }, 5000);
    
    return () => clearInterval(interval);
  }, [messages, currentChat]);


  const fetchInitialData = async () => {
    try {
      const [agentsRes, chatsRes] = await Promise.all([
        fetch(`${API}/agents`, { headers }),
        fetch(`${API}/chats`, { headers })
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
      const response = await fetch(`${API}/chats/${chatId}`, { headers
      });
      if (response.ok) {
        const chat = await response.json();
        setCurrentChat(chat);
        setMessages(chat.messages || []);
        initFeedback(chat.messages || []);
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
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ agent_id: selectedAgent.agent_id })
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
          headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ agent_id: selectedAgent.agent_id })
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
    const isAuto = provider === "auto";
    const userMessage = { role: "user", 
      content: input, 
      message_id: `temp_${Date.now()}`,
      attachments: attachments.map(a => a.preview),
      attachment_files: attachments.filter(a => a.file_url).map(a => ({ file_url: a.file_url, type: a.type, filename: a.filename })),
      model_used: isAuto ? "Auto-selecting..." : selectedModel,
      auto_selected: isAuto
    };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setAttachments([]);
    if (textareaRef.current) textareaRef.current.style.height = "40px";

    try {
      const response = await fetch(`${API}/chats/${chatId}/messages`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ content: userMessage.content,
          model_provider: isAuto ? "auto" : provider,
          model_name: isAuto ? "auto" : model,
          attachments: userMessage.attachments,
          attachment_files: userMessage.attachment_files
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [
          ...prev.slice(0, -1),
          data.user_message,
          data.assistant_message
        ]);
        // Auto-store generated image if present
        if (data.generated_image && data.assistant_message?.message_id) {
          const imgKey = `${data.assistant_message.message_id}_image`;
          setGeneratedFiles(prev => ({ ...prev, [imgKey]: data.generated_image }));
        }
        // Auto-store generated video if present
        if (data.generated_video && data.assistant_message?.message_id) {
          const vidKey = `${data.assistant_message.message_id}_video`;
          setGeneratedFiles(prev => ({ ...prev, [vidKey]: data.generated_video }));
        }
        // Auto-store generated file if present
        if (data.generated_file && data.assistant_message?.message_id) {
          const fileKey = `${data.assistant_message.message_id}_file`;
          setGeneratedFiles(prev => ({ ...prev, [fileKey]: data.generated_file }));
        }
        // Show toast if auto-selected
        if (data.auto_selected && data.model_reason) {
          toast.success(`Smart Selection: ${data.model_used} - ${data.model_reason}`);
        }
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
          headers: headers, body: formData
        });

        if (response.ok) {
          const data = await response.json();
          setAttachments(prev => [...prev, {
            filename: data.filename,
            type: data.content_type,
            size: data.size,
            preview: data.data_url,
            file_url: data.file_url
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

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        await transcribeAudio(audioBlob);
      };
      
      mediaRecorder.start();
      setRecording(true);
    } catch {
      toast.error("Microphone access denied. Please allow microphone access.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob) => {
    setTranscribing(true);
    try {
      const formData = new FormData();
      formData.append("audio_file", audioBlob, "recording.webm");
      
      const response = await fetch(`${API}/audio/speech-to-text`, {
        method: "POST",
        headers: { ...headers }, body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.text) {
          setInput(prev => prev ? `${prev} ${data.text}` : data.text);
          toast.success("Voice transcribed!");
        } else {
          toast.error("No speech detected");
        }
      } else {
        toast.error("Transcription failed");
      }
    } catch {
      toast.error("Transcription failed");
    } finally {
      setTranscribing(false);
    }
  };

  const generateFile = async (type, content, msgId, title) => {
    const key = `${msgId}_${type}`;
    setGeneratingFile(key);
    try {
      let endpoint = `${API}/generate/document`;
      let body = { type, title: title || "Generated File", content };
      
      if (type === "image") {
        endpoint = `${API}/generate/image`;
        body = { prompt: content, model: "gpt-image-1" };
      } else if (type === "video") {
        endpoint = `${API}/generate/video`;
        body = { prompt: content, model: "sora-2", duration: 4 };
      } else if (type === "xlsx") {
        // Try to parse content as table data
        const lines = content.split("\n").filter(l => l.trim());
        const rows = lines.map(l => l.split(/[,\t|]/).map(c => c.trim()));
        body = { type: "xlsx", title: title || "Spreadsheet", content, rows };
      }
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify(body)
      });
      
      if (response.ok) {
        const data = await response.json();
        setGeneratedFiles(prev => ({ ...prev, [key]: data }));
        toast.success(`${type.toUpperCase()} file generated!`);
      } else {
        const err = await response.json().catch(() => ({}));
        toast.error(err.detail || `${type} generation failed`);
      }
    } catch {
      toast.error(`${type} generation failed`);
    } finally {
      setGeneratingFile(null);
    }
  };

  const FileGenButtons = ({ content, msgId }) => {
    const truncated = content?.slice(0, 500) || "";
    return (
      <div className="flex flex-wrap gap-1.5 mt-2">
        {[
          { type: "pdf", icon: FileText, label: "PDF", color: "text-red-400 bg-red-500/10 hover:bg-red-500/20" },
          { type: "docx", icon: File, label: "Word", color: "text-blue-400 bg-blue-500/10 hover:bg-blue-500/20" },
          { type: "xlsx", icon: FileSpreadsheet, label: "Excel", color: "text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20" },
          { type: "txt", icon: FileText, label: "Text", color: "text-zinc-400 bg-zinc-500/10 hover:bg-zinc-500/20" },
          { type: "image", icon: Image, label: "Image", color: "text-rose-400 bg-rose-500/10 hover:bg-rose-500/20" },
          { type: "video", icon: Film, label: "Video", color: "text-violet-400 bg-violet-500/10 hover:bg-violet-500/20" },
        ].map(({ type, icon: Icon, label, color }) => {
          const key = `${msgId}_${type}`;
          const file = generatedFiles[key];
          const isGenerating = generatingFile === key;
          
          if (file) {
            return (
              <a
                key={type}
                href={file.preview || `${API}${file.url}`}
                target="_blank"
                rel="noopener noreferrer"
                download={file.filename}
                className={`flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium ${color} border border-white/5`}
                data-testid={`download-${type}-${msgId}`}
              >
                <Download className="w-3 h-3" />
                {label}
              </a>
            );
          }
          
          return (
            <button
              key={type}
              onClick={() => generateFile(type, truncated, msgId, `${selectedAgent?.name || "Agent"} Output`)}
              disabled={isGenerating}
              className={`flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium transition-colors ${color} border border-white/5`}
              data-testid={`gen-${type}-${msgId}`}
            >
              {isGenerating ? <Loader2 className="w-3 h-3 animate-spin" /> : <Icon className="w-3 h-3" />}
              {isGenerating ? "..." : label}
            </button>
          );
        })}
      </div>
    );
  };

  const deleteChat = async (chatId) => {
    try {
      const response = await fetch(`${API}/chats/${chatId}`, {
        method: "DELETE", headers
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

  const shareChat = async () => {
    if (!currentChat) return;
    try {
      const res = await fetch(`${API}/chats/${currentChat.chat_id}/share`, { method: "POST", headers });
      if (res.ok) {
        const data = await res.json();
        toast.success(data.shared ? "Chat shared with team" : "Chat unshared from team");
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Failed to share");
      }
    } catch { toast.error("Failed to share chat"); }
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
    <div className="h-screen bg-background flex overflow-hidden" data-testid="chat-page">
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
                <span className="text-lg font-bold text-white font-['Outfit']">MAARS Command</span>
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
      <div className="hidden lg:flex flex-col bg-zinc-900/50 border-r border-white/10 relative" style={{ width: sidebarWidth, minWidth: 200, maxWidth: 600 }}>
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center justify-between mb-4">
            <Link to="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-white font-['Outfit']">MAARS Command</span>
            </Link>
            <NotificationCenter />
          </div>
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
        {/* Resize Handle */}
        <div
          ref={resizeRef}
          onMouseDown={startResize}
          className="absolute right-0 top-0 bottom-0 w-1.5 cursor-col-resize hover:bg-indigo-500/40 active:bg-indigo-500/60 transition-colors z-10"
          data-testid="sidebar-resize-handle"
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-screen pt-16 lg:pt-0 overflow-hidden">
        {/* Agent Header */}
        {selectedAgent && (
          <div className="hidden lg:flex items-center justify-between p-4 border-b border-white/10 shrink-0">
            <div className="flex items-center gap-4">
              <img
                src={selectedAgent.avatar}
                alt={selectedAgent.name}
                className="w-10 h-10 rounded-lg object-cover"
              />
              <div>
                <h2 className="font-semibold text-white">{selectedAgent.name}</h2>
                <p className="text-sm text-zinc-400">{selectedAgent.role}</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowCustomize(!showCustomize)}
                className={`text-zinc-400 hover:text-indigo-400 h-8 ml-2 ${showCustomize ? 'text-indigo-400 bg-indigo-500/10' : ''}`}
                data-testid="customize-agent-btn"
              >
                <Settings className="w-4 h-4 mr-1" />Customize
              </Button>
            </div>
            <div className="flex items-center gap-2 mr-32">
              {currentChat && (
                <Button variant="ghost" size="sm" onClick={shareChat} className="text-zinc-400 hover:text-indigo-400 h-8" data-testid="share-chat-btn">
                  <Share2 className="w-4 h-4 mr-1" />Share
                </Button>
              )}
            </div>
          </div>
        )}
        {showCustomize && selectedAgent && (
          <AgentCustomizePanel agent={selectedAgent} onClose={() => setShowCustomize(false)} />
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
                  {selectedAgent.tools?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 justify-center mt-3" data-testid="agent-chat-tools">
                      <span className="flex items-center gap-1 text-xs text-amber-400 mr-1">
                        <Wrench className="w-3 h-3" /> Tools:
                      </span>
                      {selectedAgent.tools.map((tool, i) => {
                        const icons = { web_search: Search, calculate: Calculator, create_task: ClipboardList, analyze_data: BarChart3, send_slack: MessageCircle, send_email: Mail, send_sms: Phone, github_action: Github, airtable_action: Table, search_gif: Image, schedule_meeting: Calendar, google_calendar: Calendar, send_gmail: Mail };
                        const labels = { web_search: "Web Search", calculate: "Calculator", create_task: "Task Creator", analyze_data: "Data Analyzer", send_slack: "Slack", send_email: "Email", send_sms: "SMS", github_action: "GitHub", airtable_action: "Airtable", search_gif: "GIFs", schedule_meeting: "Calendly", google_calendar: "Calendar", send_gmail: "Gmail" };
                        const Icon = icons[tool] || Wrench;
                        return (
                          <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                            <Icon className="w-3 h-3" /> {labels[tool] || tool}
                          </span>
                        );
                      })}
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="space-y-4 max-w-3xl mx-auto">
              {messages.map((msg, i) => {
                // Commander delegation group chat rendering
                if (msg.role === "assistant" && msg.delegation_data?.type === "commander_delegation") {
                  return (
                    <CommanderGroupChat 
                      key={msg.message_id || i} 
                      msg={msg} 
                      msgIndex={i}
                      generatedFiles={generatedFiles}
                      generateFile={generateFile}
                      generatingFile={generatingFile}
                      currentAgent={selectedAgent}
                    />
                  );
                }
                
                // Commander processing indicator
                if (msg.role === "assistant" && msg.commander_status === "processing") {
                  return (
                    <div key={msg.message_id || i} className="flex gap-3" data-testid={`message-${i}`}>
                      <img src={selectedAgent?.avatar} alt="" className="w-8 h-8 rounded-lg object-cover flex-shrink-0" />
                      <div className="rounded-xl px-4 py-3 bg-zinc-800/50 border border-indigo-500/20 max-w-[85%]">
                        <div className="flex items-center gap-2 mb-2">
                          <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
                          <span className="text-indigo-400 text-sm font-medium">Commander is coordinating specialists...</span>
                        </div>
                        <MarkdownRenderer content={msg.content} className="text-sm" />
                        <p className="text-zinc-500 text-xs mt-2">This usually takes 1-3 minutes. Results will appear automatically.</p>
                      </div>
                    </div>
                  );
                }

                return (
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
                    {msg.role === "assistant" && msg.execution_steps && (
                      <ExecutionSteps steps={msg.execution_steps} />
                    )}
                    {msg.role === "assistant" ? (
                      <MarkdownRenderer content={msg.content} />
                    ) : (
                      <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      {msg.model_used && (
                        <div className="text-xs text-zinc-500 flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          <span>{msg.model_used}</span>
                          {msg.auto_selected && msg.model_reason && (
                            <span className="text-indigo-400 ml-1">• {msg.model_reason}</span>
                          )}
                        </div>
                      )}
                      {msg.role === "assistant" && (
                        <button
                          onClick={() => playTTS(msg.message_id || i, msg.content)}
                          disabled={ttsLoading === (msg.message_id || i)}
                          className="text-xs text-zinc-500 hover:text-indigo-400 transition-colors flex items-center gap-1 ml-auto"
                          data-testid={`tts-btn-${i}`}
                          title="Read aloud"
                        >
                          {ttsLoading === (msg.message_id || i) ? <Loader2 className="w-3 h-3 animate-spin" /> :
                           ttsPlaying === (msg.message_id || i) ? <VolumeX className="w-3 h-3 text-red-400" /> :
                           <Volume2 className="w-3 h-3" />}
                        </button>
                      )}
                      {msg.role === "assistant" && msg.message_id && (
                        <div className="flex items-center gap-1 ml-2 border-l border-white/10 pl-2">
                          <button
                            onClick={() => submitFeedback(currentChat?.chat_id, msg.message_id, "up")}
                            className={`p-1 rounded transition-colors ${feedbackState[msg.message_id] === "up" ? "text-emerald-400 bg-emerald-500/15" : "text-zinc-600 hover:text-emerald-400 hover:bg-emerald-500/10"}`}
                            data-testid={`feedback-up-${i}`}
                            title="Good response"
                          >
                            <ThumbsUp className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => submitFeedback(currentChat?.chat_id, msg.message_id, "down")}
                            className={`p-1 rounded transition-colors ${feedbackState[msg.message_id] === "down" ? "text-red-400 bg-red-500/15" : "text-zinc-600 hover:text-red-400 hover:bg-red-500/10"}`}
                            data-testid={`feedback-down-${i}`}
                            title="Poor response"
                          >
                            <ThumbsDown className="w-3 h-3" />
                          </button>
                        </div>
                      )}
                    </div>
                    {/* Generated file preview */}
                    {msg.role === "assistant" && (() => {
                      const imgKey = `${msg.message_id || i}_image`;
                      const vidKey = `${msg.message_id || i}_video`;
                      const fileKey = `${msg.message_id || i}_file`;
                      const imgFile = generatedFiles[imgKey] || msg.generated_image;
                      const vidFile = generatedFiles[vidKey] || msg.generated_video;
                      const docFile = generatedFiles[fileKey] || msg.generated_file;
                      const formatIcons = { pdf: "text-red-400 bg-red-500/10 border-red-500/30", docx: "text-blue-400 bg-blue-500/10 border-blue-500/30", xlsx: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30", csv: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30", txt: "text-zinc-400 bg-zinc-500/10 border-zinc-500/30" };
                      return (
                        <>
                          {docFile?.url && (
                            <div className={`mt-3 rounded-xl border p-4 max-w-sm flex items-center gap-3 ${formatIcons[docFile.format] || "text-zinc-400 bg-zinc-500/10 border-white/10"}`} data-testid={`generated-file-${msg.message_id || i}`}>
                              <FileText className="w-8 h-8 flex-shrink-0" />
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-white truncate">{docFile.filename}</p>
                                <p className="text-xs opacity-70">{docFile.format?.toUpperCase()} {docFile.size ? `- ${(docFile.size / 1024).toFixed(1)}KB` : ""}</p>
                              </div>
                              <a href={`${API}${docFile.url}`} download={docFile.filename} className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-medium transition-colors">
                                <Download className="w-3.5 h-3.5" />Download
                              </a>
                            </div>
                          )}
                          {(imgFile?.preview || imgFile?.url) && (
                            <div className="mt-3 rounded-lg overflow-hidden border border-white/10 max-w-sm" data-testid={`generated-image-${msg.message_id || i}`}>
                              <img src={imgFile.preview || `${API}${imgFile.url}`} alt="Generated" className="w-full" />
                              <a href={imgFile.url ? `${API}${imgFile.url}` : imgFile.preview} download className="block text-center text-xs text-indigo-400 py-2 hover:bg-white/5">
                                <Download className="w-3 h-3 inline mr-1" />Download PNG
                              </a>
                            </div>
                          )}
                          {vidFile?.url && (
                            <div className="mt-3 rounded-lg overflow-hidden border border-white/10 max-w-sm" data-testid={`generated-video-${msg.message_id || i}`}>
                              <video controls className="w-full" src={`${API}${vidFile.url}`} />
                              <a href={`${API}${vidFile.url}`} download className="block text-center text-xs text-violet-400 py-2 hover:bg-white/5">
                                <Download className="w-3 h-3 inline mr-1" />Download MP4
                              </a>
                            </div>
                          )}
                          {!vidFile?.url && msg.video_generating && (
                            <div className="mt-3 rounded-lg border border-violet-500/30 bg-violet-500/5 p-4 max-w-sm" data-testid={`video-generating-${msg.message_id || i}`}>
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full border-2 border-violet-400 border-t-transparent animate-spin" />
                                <div>
                                  <p className="text-sm text-violet-300 font-medium">Generating video with Sora 2...</p>
                                  <p className="text-xs text-zinc-500 mt-0.5">This may take 3-5 minutes. You can continue chatting.</p>
                                </div>
                              </div>
                            </div>
                          )}
                          {msg.video_error && (
                            <div className="mt-3 rounded-lg border border-red-500/30 bg-red-500/5 p-3 max-w-sm">
                              <p className="text-xs text-red-400">Video generation failed: {msg.video_error}</p>
                            </div>
                          )}
                        </>
                      );
                    })()}
                    {/* File generation buttons */}
                    {msg.role === "assistant" && <FileGenButtons content={msg.content} msgId={msg.message_id || i} />}
                  </div>
                  {msg.role === "user" && (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-sm font-semibold">
                        {user?.name?.charAt(0) || "U"}
                      </span>
                    </div>
                  )}
                </div>
                );
              })}
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

        {/* Input - Always visible at bottom */}
        <div className="p-4 border-t border-white/10 shrink-0 bg-background">
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
          <div className="max-w-3xl mx-auto mb-3 flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span className="text-xs text-zinc-400">Model:</span>
            </div>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="w-[220px] h-8 text-xs bg-zinc-900/50 border-white/10" data-testid="model-selector">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {AVAILABLE_MODELS.map((m) => (
                  <SelectItem key={`${m.provider}/${m.model}`} value={`${m.provider}/${m.model}`}>
                    {m.provider === "auto" ? "🧠 " : ""}{m.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedModel === "auto/auto" ? (
              <span className="text-xs text-indigo-400">AI picks the best model for each task</span>
            ) : (
              <span className="text-xs text-zinc-500">No limits • Switch anytime</span>
            )}
          </div>

          <form onSubmit={sendMessage} className="max-w-3xl mx-auto flex gap-3 items-end">
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
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={recording ? stopRecording : startRecording}
              disabled={transcribing}
              className={`border-white/10 ${recording ? "bg-red-500/20 border-red-500/50 text-red-400 animate-pulse" : "hover:bg-white/5"}`}
              data-testid="mic-btn"
              title={recording ? "Stop recording" : transcribing ? "Transcribing..." : "Voice input"}
            >
              {transcribing ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : recording ? (
                <MicOff className="w-4 h-4" />
              ) : (
                <Mic className="w-4 h-4" />
              )}
            </Button>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = "auto";
                e.target.style.height = Math.min(e.target.scrollHeight, 200) + "px";
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (input.trim() && selectedAgent && !sending) sendMessage(e);
                }
              }}
              placeholder={`Message ${selectedAgent?.name || "AI"}...`}
              className="flex-1 bg-zinc-900/50 border border-white/10 focus:border-indigo-500 rounded-md px-3 py-2 text-sm text-white placeholder:text-zinc-500 resize-none overflow-y-auto outline-none"
              style={{ minHeight: "40px", maxHeight: "200px" }}
              rows={1}
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
const SidebarContent = ({ agents, chats, selectedAgent, setSelectedAgent, 
  currentChat, loadChat, deleteChat, startNewChat, navigate 
}) => (
  <div className="flex-1 flex flex-col overflow-hidden">
    {/* Navigation - at the top */}
    <div className="px-4 pt-3 pb-2 space-y-0.5 border-b border-white/10">
      <Link
        to="/dashboard"
        className="flex items-center gap-3 px-3 py-2 rounded-lg text-zinc-400 hover:bg-white/5 hover:text-white transition-colors"
        data-testid="nav-dashboard"
      >
        <LayoutDashboard className="w-4 h-4" />
        <span className="text-sm font-medium">Dashboard</span>
      </Link>
      <Link
        to="/agents"
        className="flex items-center gap-3 px-3 py-2 rounded-lg text-zinc-400 hover:bg-white/5 hover:text-white transition-colors"
        data-testid="nav-agents"
      >
        <Users className="w-4 h-4" />
        <span className="text-sm font-medium">All Agents</span>
      </Link>
      <Link
        to="/tasks"
        className="flex items-center gap-3 px-3 py-2 rounded-lg text-zinc-400 hover:bg-white/5 hover:text-white transition-colors"
        data-testid="nav-tasks"
      >
        <ListTodo className="w-4 h-4" />
        <span className="text-sm font-medium">Tasks</span>
      </Link>
      <Link
        to="/team"
        className="flex items-center gap-3 px-3 py-2 rounded-lg text-zinc-400 hover:bg-white/5 hover:text-white transition-colors"
        data-testid="nav-team"
      >
        <Users className="w-4 h-4" />
        <span className="text-sm font-medium">Team</span>
      </Link>
    </div>

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
              toast.success(`Switched to ${agent.name}`);
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
  </div>
);

export default AgentChat;
