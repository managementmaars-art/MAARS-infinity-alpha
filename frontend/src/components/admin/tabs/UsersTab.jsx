import { Card, CardContent } from "../../ui/card";
import { Badge } from "../../ui/badge";

export const UsersTab = ({ users }) => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white font-['Outfit']">All Users ({users.length})</h2>
      </div>
      <div className="space-y-2">
        {users.map((u) => (
          <Card key={u.user_id} className="bg-zinc-900/50 border-white/10" data-testid={`admin-user-${u.user_id}`}>
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center shrink-0">
                  {u.picture ? (
                    <img src={u.picture} alt="" className="w-full h-full rounded-full object-cover" />
                  ) : (
                    <span className="text-white font-semibold text-sm">{u.name?.charAt(0) || "?"}</span>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-white truncate">{u.name}</p>
                    {u.is_admin && <Badge className="bg-red-500/20 text-red-400 text-[10px]">Admin</Badge>}
                  </div>
                  <p className="text-sm text-zinc-400 truncate">{u.email}</p>
                </div>
                <div className="text-right shrink-0">
                  <Badge className={`${
                    u.subscription?.plan_id === 'business' ? 'bg-amber-500/20 text-amber-400' :
                    u.subscription?.plan_id === 'pro' ? 'bg-violet-500/20 text-violet-400' :
                    u.subscription?.plan_id === 'starter' ? 'bg-indigo-500/20 text-indigo-400' :
                    'bg-zinc-500/20 text-zinc-400'
                  }`}>
                    {u.subscription?.plan_id || "free"}
                  </Badge>
                  <p className="text-xs text-zinc-500 mt-1">{u.subscription?.credits || 0} credits</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {users.length === 0 && <p className="text-zinc-500 text-center py-8">No users found</p>}
      </div>
    </div>
  
)
