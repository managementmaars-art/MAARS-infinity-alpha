import { Card, CardContent } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { DollarSign } from "lucide-react";

export const TransactionsTab = ({ transactions }) => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white font-['Outfit']">Payment Transactions ({transactions.length})</h2>
      </div>
      <div className="space-y-2">
        {transactions.map((tx) => (
          <Card key={tx.transaction_id} className="bg-zinc-900/50 border-white/10" data-testid={`admin-tx-${tx.transaction_id}`}>
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                  tx.payment_status === 'paid' ? 'bg-emerald-500/20' : 'bg-zinc-500/20'
                }`}>
                  <DollarSign className={`w-5 h-5 ${tx.payment_status === 'paid' ? 'text-emerald-400' : 'text-zinc-400'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-white truncate">
                    {tx.metadata?.type === 'subscription' ? `${tx.metadata?.plan_id} Plan` : `${tx.metadata?.credits} Credits`}
                  </p>
                  <p className="text-sm text-zinc-400 truncate">{tx.email}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="font-semibold text-white">${tx.amount?.toFixed(2)}</p>
                  <Badge className={`text-[10px] ${
                    tx.payment_status === 'paid' ? 'bg-emerald-500/20 text-emerald-400' :
                    tx.payment_status === 'pending' ? 'bg-amber-500/20 text-amber-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {tx.payment_status || 'pending'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {transactions.length === 0 && <p className="text-zinc-500 text-center py-8">No transactions yet</p>}
      </div>
    </div>
  
)
