import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Badge } from "../ui/badge";
import { Card, CardContent } from "../ui/card";
import {
  X, CheckCircle, ChevronRight, ChevronLeft, ExternalLink, Copy,
  MessageSquare, Github, Mail, Loader2, AlertCircle
} from "lucide-react";
import { useAuth, API } from "../../App";
import { toast } from "sonner";

const WIZARD_STEPS = {
  slack: {
    name: "Slack",
    icon: MessageSquare,
    color: "emerald",
    steps: [
      {
        title: "Create a Slack App",
        description: "Go to the Slack API dashboard and create a new app for your workspace.",
        link: "https://api.slack.com/apps",
        linkText: "Open Slack API Dashboard",
      },
      {
        title: "Add Bot Permissions",
        description: "Under 'OAuth & Permissions', add these Bot Token Scopes: chat:write, channels:read, channels:join",
        fields: [],
      },
      {
        title: "Install to Workspace",
        description: "Click 'Install to Workspace' and authorize the app. Copy the Bot User OAuth Token.",
        fields: [{ key: "bot_token", label: "Bot User OAuth Token", placeholder: "xoxb-..." }],
      },
    ],
  },
  github: {
    name: "GitHub",
    icon: Github,
    color: "zinc",
    steps: [
      {
        title: "Generate a Personal Access Token",
        description: "Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic).",
        link: "https://github.com/settings/tokens",
        linkText: "Open GitHub Token Settings",
      },
      {
        title: "Set Token Permissions",
        description: "Select scopes: repo (full), read:org, read:user. Set an expiration date and generate.",
        fields: [],
      },
      {
        title: "Enter Your Token",
        description: "Paste the generated personal access token below.",
        fields: [{ key: "personal_access_token", label: "Personal Access Token", placeholder: "ghp_..." }],
      },
    ],
  },
  google_suite: {
    name: "Google Suite",
    icon: Mail,
    color: "blue",
    steps: [
      {
        title: "Create a Google Cloud Project",
        description: "Go to Google Cloud Console and create a new project (or select existing). Enable Calendar API and Gmail API.",
        link: "https://console.cloud.google.com/apis/dashboard",
        linkText: "Open Google Cloud Console",
      },
      {
        title: "Create a Service Account",
        description: "Go to IAM & Admin > Service Accounts > Create. Download the JSON key file.",
        link: "https://console.cloud.google.com/iam-admin/serviceaccounts",
        linkText: "Service Accounts",
      },
      {
        title: "Configure Credentials",
        description: "Paste the service account JSON and (optionally) set a delegate email for Gmail sending.",
        fields: [
          { key: "service_account_json", label: "Service Account JSON", placeholder: '{"type": "service_account", ...}', multiline: true },
          { key: "delegate_email", label: "Delegate Email (for Gmail)", placeholder: "admin@yourdomain.com" },
        ],
      },
    ],
  },
};

const IntegrationWizard = ({ onClose, onComplete }) => {
  const { token } = useAuth();
  const [selectedService, setSelectedService] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [inputs, setInputs] = useState({});
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleServiceSelect = (serviceId) => {
    setSelectedService(serviceId);
    setCurrentStep(0);
    setInputs({});
    setTestResult(null);
  };

  const handleNext = () => {
    const config = WIZARD_STEPS[selectedService];
    if (currentStep < config.steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) setCurrentStep(prev => prev - 1);
    else { setSelectedService(null); setTestResult(null); }
  };

  const handleSaveAndTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      // Save integration
      const saveRes = await fetch(`${API}/admin/integrations`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ service_id: selectedService, config: inputs }),
      });
      if (!saveRes.ok) throw new Error("Failed to save");

      // Test integration
      const testRes = await fetch(`${API}/admin/integrations/test/${selectedService}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const result = await testRes.json();
      setTestResult(result);

      if (result.status === "active") {
        toast.success(`${WIZARD_STEPS[selectedService].name} connected successfully!`);
      } else {
        toast.error(`Test failed: ${result.message}`);
      }
    } catch (err) {
      setTestResult({ status: "error", message: err.message });
      toast.error("Failed to save integration");
    } finally {
      setTesting(false);
    }
  };

  const handleFinish = () => {
    onComplete?.();
    onClose();
  };

  const config = selectedService ? WIZARD_STEPS[selectedService] : null;
  const step = config?.steps[currentStep];

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" data-testid="integration-wizard-modal">
      <div className="bg-zinc-900 border border-white/10 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <h2 className="text-lg font-semibold text-white font-['Outfit']">
            {selectedService ? `Setup ${config.name}` : "Quick Setup Wizard"}
          </h2>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/10 text-zinc-400 hover:text-white transition-colors" data-testid="wizard-close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          {!selectedService ? (
            /* Service Selection */
            <div className="space-y-3" data-testid="wizard-service-list">
              <p className="text-zinc-400 text-sm mb-4">Choose a service to connect. We'll guide you step by step.</p>
              {Object.entries(WIZARD_STEPS).map(([id, svc]) => {
                const Icon = svc.icon;
                return (
                  <button
                    key={id}
                    onClick={() => handleServiceSelect(id)}
                    className="w-full flex items-center gap-4 p-4 rounded-xl bg-zinc-800/50 border border-white/5 hover:border-white/15 hover:bg-zinc-800 transition-all text-left"
                    data-testid={`wizard-service-${id}`}
                  >
                    <div className={`w-11 h-11 rounded-lg bg-${svc.color}-500/15 flex items-center justify-center`}>
                      <Icon className={`w-5 h-5 text-${svc.color}-400`} />
                    </div>
                    <div className="flex-1">
                      <p className="text-white font-medium">{svc.name}</p>
                      <p className="text-xs text-zinc-500">{svc.steps.length} steps to connect</p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-zinc-600" />
                  </button>
                );
              })}
            </div>
          ) : (
            /* Step Content */
            <div data-testid={`wizard-step-${currentStep}`}>
              {/* Progress */}
              <div className="flex items-center gap-2 mb-5">
                {config.steps.map((_, i) => (
                  <div key={i} className={`h-1.5 flex-1 rounded-full transition-colors ${i <= currentStep ? "bg-indigo-500" : "bg-zinc-800"}`} />
                ))}
              </div>

              <div className="mb-1 flex items-center gap-2">
                <Badge variant="outline" className="border-white/10 text-zinc-400 text-[10px]">Step {currentStep + 1}/{config.steps.length}</Badge>
              </div>
              <h3 className="text-white font-semibold text-base mb-2">{step.title}</h3>
              <p className="text-zinc-400 text-sm mb-4">{step.description}</p>

              {step.link && (
                <a href={step.link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300 mb-4 transition-colors" data-testid="wizard-external-link">
                  <ExternalLink className="w-4 h-4" />{step.linkText}
                </a>
              )}

              {step.fields?.map(field => (
                <div key={field.key} className="mb-3">
                  <label className="text-xs text-zinc-400 mb-1 block">{field.label}</label>
                  {field.multiline ? (
                    <textarea
                      value={inputs[field.key] || ""}
                      onChange={e => setInputs(prev => ({ ...prev, [field.key]: e.target.value }))}
                      placeholder={field.placeholder}
                      className="w-full bg-zinc-800 border border-white/10 rounded-lg p-3 text-white text-sm min-h-[100px] resize-none focus:outline-none focus:border-indigo-500/50"
                      data-testid={`wizard-field-${field.key}`}
                    />
                  ) : (
                    <Input
                      value={inputs[field.key] || ""}
                      onChange={e => setInputs(prev => ({ ...prev, [field.key]: e.target.value }))}
                      placeholder={field.placeholder}
                      className="bg-zinc-800 border-white/10 text-white"
                      data-testid={`wizard-field-${field.key}`}
                    />
                  )}
                </div>
              ))}

              {testResult && (
                <div className={`p-3 rounded-lg mb-4 flex items-center gap-2 ${testResult.status === "active" ? "bg-emerald-500/10 border border-emerald-500/20" : "bg-red-500/10 border border-red-500/20"}`} data-testid="wizard-test-result">
                  {testResult.status === "active" ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : <AlertCircle className="w-4 h-4 text-red-400" />}
                  <span className={`text-sm ${testResult.status === "active" ? "text-emerald-400" : "text-red-400"}`}>{testResult.message}</span>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-3 mt-6">
                <Button variant="outline" onClick={handleBack} className="border-white/10 text-zinc-300" data-testid="wizard-back">
                  <ChevronLeft className="w-4 h-4 mr-1" />Back
                </Button>
                <div className="flex-1" />
                {currentStep < config.steps.length - 1 ? (
                  <Button onClick={handleNext} className="bg-indigo-600 hover:bg-indigo-500 text-white" data-testid="wizard-next">
                    Next<ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                ) : testResult?.status === "active" ? (
                  <Button onClick={handleFinish} className="bg-emerald-600 hover:bg-emerald-500 text-white" data-testid="wizard-finish">
                    <CheckCircle className="w-4 h-4 mr-1" />Done
                  </Button>
                ) : (
                  <Button onClick={handleSaveAndTest} disabled={testing} className="bg-indigo-600 hover:bg-indigo-500 text-white" data-testid="wizard-save-test">
                    {testing ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : null}
                    {testing ? "Testing..." : "Save & Test"}
                  </Button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IntegrationWizard;
