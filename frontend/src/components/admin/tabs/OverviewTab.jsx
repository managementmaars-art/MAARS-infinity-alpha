import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Users, MessageSquare, Activity, DollarSign, Bot, UserCheck, ListTodo, CreditCard, TrendingUp } from "lucide-react";

const StatCard = ({ title, value, icon: Icon, color }) => (
  <Card className="bg-zinc-900/50 border-white/10">
    <CardContent className="p-4">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg bg-${color}-500/20 flex items-center justify-center`}>
          <Icon className={`w-5 h-5 text-${color}-400`} />
        </div>
        <div>
          <p className="text-xs text-zinc-400">{title}</p>
          <p className="text-lg font-bold text-white">{value}</p>
        </div>
      </div>
    </CardContent>
  </Card>
);

export const OverviewTab = ({ stats, profitData, apiKeysConfig }) => {
    const p = profitData;
    const costs = apiKeysConfig?.cost_reference || {};
    return (
    <div className="space-y-6">
      {/* Top stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Users" value={stats?.total_users || 0} icon={Users} color="indigo" />
        <StatCard title="Total Chats" value={stats?.total_chats || 0} icon={MessageSquare} color="violet" />
        <StatCard title="Messages Sent" value={stats?.total_messages || 0} icon={Activity} color="emerald" />
        <StatCard title="Revenue" value={`$${stats?.total_revenue?.toFixed(2) || '0.00'}`} icon={DollarSign} color="amber" />
      </div>

      {/* Subscription Distribution + Credits Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <CardTitle className="text-white font-['Outfit'] text-base">Subscription Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {stats?.plan_distribution && Object.keys(stats.plan_distribution).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(stats.plan_distribution).map(([plan, count]) => (
                  <div key={plan} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${
                        plan === 'business' ? 'bg-amber-400' :
                        plan === 'pro' ? 'bg-violet-400' :
                        plan === 'starter' ? 'bg-indigo-400' : 'bg-zinc-400'
                      }`} />
                      <span className="text-zinc-300 capitalize">{plan}</span>
                    </div>
                    <Badge variant="outline" className="border-white/10 text-zinc-300">{count} users</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-zinc-500 text-sm">No subscription data yet</p>
            )}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <CardTitle className="text-white font-['Outfit'] text-base">Credits Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Total Credits Used</span>
              <span className="text-white font-semibold">{stats?.total_credits_used || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Credits Remaining (All Users)</span>
              <span className="text-white font-semibold">{stats?.total_credits_remaining || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Active Subscriptions</span>
              <span className="text-white font-semibold">{stats?.active_subscriptions || 0}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent/Task stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Agents" value={stats?.total_agents || 0} icon={Bot} color="cyan" />
        <StatCard title="Custom Agents" value={stats?.custom_agents || 0} icon={UserCheck} color="pink" />
        <StatCard title="Total Tasks" value={stats?.total_tasks || 0} icon={ListTodo} color="orange" />
        <StatCard title="Subscriptions" value={stats?.active_subscriptions || 0} icon={CreditCard} color="teal" />
      </div>

      {/* Profit Dashboard */}
      <Card className="bg-zinc-900/50 border-white/10" data-testid="profit-dashboard">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            Profit Dashboard
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
              <p className="text-xs text-emerald-400 mb-1">Total Revenue</p>
              <p className="text-2xl font-bold text-white">${p?.revenue?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
              <p className="text-xs text-red-400 mb-1">Total API Cost</p>
              <p className="text-2xl font-bold text-white">${p?.total_api_cost?.toFixed(4) || '0.00'}</p>
            </div>
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
              <p className="text-xs text-amber-400 mb-1">Net Profit</p>
              <p className="text-2xl font-bold text-white">${p?.net_profit?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
              <p className="text-xs text-indigo-400 mb-1">Profit Margin</p>
              <p className="text-2xl font-bold text-white">{p?.profit_margin_pct?.toFixed(1) || '0'}%</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="text-center p-3 rounded-lg bg-white/5">
              <p className="text-lg font-bold text-white">{p?.total_api_calls?.toLocaleString() || 0}</p>
              <p className="text-[10px] text-zinc-500">API Calls</p>
            </div>
            <div className="text-center p-3 rounded-lg bg-white/5">
              <p className="text-lg font-bold text-white">{((p?.total_input_tokens || 0) / 1000).toFixed(1)}K</p>
              <p className="text-[10px] text-zinc-500">Input Tokens</p>
            </div>
            <div className="text-center p-3 rounded-lg bg-white/5">
              <p className="text-lg font-bold text-white">{((p?.total_output_tokens || 0) / 1000).toFixed(1)}K</p>
              <p className="text-[10px] text-zinc-500">Output Tokens</p>
            </div>
          </div>

          <p className="text-[10px] text-zinc-600">* API costs are estimated based on token usage. Avg cost per call: ${p?.avg_cost_per_call?.toFixed(5) || '0'}</p>
        </CardContent>
      </Card>

      {/* Per-Plan Profit Breakdown */}
      {p?.plan_profits && (
        <Card className="bg-zinc-900/50 border-white/10" data-testid="plan-profit-card">
          <CardHeader>
            <CardTitle className="text-white font-['Outfit'] text-base">Profit Per Plan (if all credits used)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="grid grid-cols-5 gap-2 text-[10px] text-zinc-500 font-medium px-1">
                <span>Plan</span><span>Price</span><span>Est. Max Cost</span><span>Profit</span><span>Margin</span>
              </div>
              {Object.entries(p.plan_profits).map(([plan, data]) => (
                <div key={plan} className="grid grid-cols-5 gap-2 items-center text-sm">
                  <span className="text-white font-medium capitalize">{plan}</span>
                  <span className="text-emerald-400">${data.revenue}</span>
                  <span className="text-red-400">${data.est_max_cost}</span>
                  <span className={`font-semibold ${data.profit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    ${data.profit}
                  </span>
                  <span className={`text-xs ${(data.margin_pct || 0) >= 50 ? 'text-emerald-400' : (data.margin_pct || 0) >= 0 ? 'text-amber-400' : 'text-red-400'}`}>
                    {data.margin_pct || 0}%
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Per-Model Cost and Provider Cost */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {p?.model_costs?.length > 0 && (
          <Card className="bg-zinc-900/50 border-white/10">
            <CardHeader>
              <CardTitle className="text-white font-['Outfit'] text-base">Cost By Model</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {p.model_costs.map((m, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span className="text-zinc-300">{m.model}</span>
                    <div className="flex gap-3 text-right">
                      <span className="text-zinc-500 text-xs">{m.calls} calls</span>
                      <span className="text-red-400 font-mono">${m.cost.toFixed(4)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {p?.provider_costs && Object.keys(p.provider_costs).length > 0 && (
          <Card className="bg-zinc-900/50 border-white/10">
            <CardHeader>
              <CardTitle className="text-white font-['Outfit'] text-base">Cost By Provider</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(p.provider_costs).map(([provider, data]) => (
                  <div key={provider} className="p-3 rounded-lg bg-white/5">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-white font-medium capitalize">{provider}</span>
                      <span className="text-red-400 font-mono">${data.cost.toFixed(4)}</span>
                    </div>
                    <div className="flex gap-4 text-[10px] text-zinc-500">
                      <span>{data.calls} calls</span>
                      <span>{(data.input_tokens / 1000).toFixed(1)}K input</span>
                      <span>{(data.output_tokens / 1000).toFixed(1)}K output</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Direct Provider Costs */}
      <Card className="bg-zinc-900/50 border-white/10" data-testid="cost-reference-card">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
            <DollarSign className="w-5 h-5 text-emerald-400" />
            Direct Provider Costs
          </CardTitle>
          <p className="text-zinc-500 text-xs mt-1">Reference pricing when using your own API keys. Prices are from provider websites and may change.</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(costs).map(([providerId, data]) => (
              <div key={providerId} className="rounded-lg border border-white/10 overflow-hidden">
                <div className="px-3 py-2 bg-white/5 border-b border-white/10">
                  <span className="text-sm font-semibold text-white capitalize">{providerId}</span>
                  <span className="text-[10px] text-zinc-500 ml-2">{data.unit}</span>
                </div>
                <div className="divide-y divide-white/5">
                  {(data.models || []).map((model, i) => (
                    <div key={i} className="flex items-center justify-between px-3 py-2 text-xs">
                      <span className="text-zinc-300">{model.name}</span>
                      <div className="flex gap-3 text-right">
                        <span className="text-zinc-500">In: <span className="text-emerald-400">{model.input}</span></span>
                        <span className="text-zinc-500">Out: <span className="text-amber-400">{model.output}</span></span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-zinc-600 mt-3">* MAARS AI Gateway includes a small markup over direct pricing for convenience and unified billing.</p>
        </CardContent>
      </Card>
    </div>
    );
};
