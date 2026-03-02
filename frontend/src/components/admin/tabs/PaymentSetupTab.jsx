import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";
import { Label } from "../../ui/label";
import { CreditCard, ExternalLink } from "lucide-react";
import { API } from "../../../App";
import { toast } from "sonner";

export const PaymentSetupTab = ({ token }) => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white font-['Outfit']">Payment Gateway Setup</h2>
        <Badge className="bg-amber-500/20 text-amber-400">Configuration Guide</Badge>
      </div>

      {/* Stripe Setup */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
              <CreditCard className="w-5 h-5 text-violet-400" />
            </div>
            Stripe (Global Payments - USD & International Cards)
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-zinc-400 text-sm">Stripe handles all international card payments, subscriptions, and credit purchases. Supports 135+ currencies including USD.</p>

          <div className="space-y-3">
            <h4 className="text-white font-semibold text-sm">Setup Steps:</h4>
            <div className="space-y-2">
              {[
                { step: "1", text: "Create a Stripe account", link: "https://dashboard.stripe.com/register" },
                { step: "2", text: "Go to Developers > API Keys in your Stripe Dashboard" },
                { step: "3", text: "Copy your Secret Key (sk_live_...) - keep this private!" },
                { step: "4", text: "Replace STRIPE_API_KEY in your backend .env file with the live key" },
                { step: "5", text: "Create Products/Prices matching your plans (Starter $29, Pro $79, Business $199)" },
                { step: "6", text: "Set up Webhook endpoint: yourdomain.com/api/stripe-webhook" },
                { step: "7", text: "In Webhook settings, listen for: checkout.session.completed, customer.subscription.updated" },
              ].map((item) => (
                <div key={item.step} className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
                  <div className="w-6 h-6 rounded-full bg-violet-500/20 flex items-center justify-center shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-violet-400">{item.step}</span>
                  </div>
                  <div>
                    <p className="text-zinc-300 text-sm">{item.text}</p>
                    {item.link && (
                      <a href={item.link} target="_blank" rel="noopener noreferrer" className="text-violet-400 text-xs hover:underline">{item.link}</a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <p className="text-emerald-300 text-sm">
              <strong>Tip:</strong> Use Stripe's test mode (sk_test_...) first to verify everything works, then switch to live keys when ready to accept real payments.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Bangladesh Payments */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-emerald-400" />
            </div>
            Bangladesh Payments (BDT)
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-zinc-400 text-sm">Options for accepting payments from Bangladesh in BDT:</p>

          <div className="space-y-3">
            <div className="p-4 rounded-lg bg-white/5 space-y-2">
              <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                Option 1: Stripe Multi-Currency (Recommended)
                <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px]">Easiest</Badge>
              </h4>
              <p className="text-zinc-400 text-sm">Stripe can accept BDT payments if you enable multi-currency in your Stripe dashboard. Funds are converted and deposited in your bank currency.</p>
              <ul className="text-zinc-400 text-sm space-y-1 ml-4 list-disc">
                <li>Go to Stripe Dashboard &gt; Settings &gt; Payments &gt; Currencies</li>
                <li>Enable BDT (Bangladeshi Taka)</li>
                <li>Customers see prices in BDT, you receive in your local currency</li>
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-white/5 space-y-2">
              <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                Option 2: SSLCommerz (Bangladesh Gateway)
                <Badge className="bg-indigo-500/20 text-indigo-400 text-[10px]">Local</Badge>
              </h4>
              <p className="text-zinc-400 text-sm">SSLCommerz is Bangladesh's leading payment gateway. Supports Bangladeshi bank cards, Visa/Mastercard, and mobile banking (Nagad, Rocket).</p>
              <ul className="text-zinc-400 text-sm space-y-1 ml-4 list-disc">
                <li>Register at <a href="https://www.sslcommerz.com" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline">sslcommerz.com</a></li>
                <li>Requires Bangladeshi business trade license</li>
                <li>Can be managed remotely from abroad</li>
                <li>Supports bank transfer, cards, and mobile wallets</li>
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-white/5 space-y-2">
              <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                Option 3: Paddle / Payoneer
                <Badge className="bg-amber-500/20 text-amber-400 text-[10px]">International</Badge>
              </h4>
              <p className="text-zinc-400 text-sm">If Stripe isn't available in your region, Paddle or Payoneer can act as a Merchant of Record, handling payments globally and paying you via bank transfer.</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Environment Variables */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] text-base">Environment Variables (.env)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-zinc-400 text-sm">Update these in your backend <code className="text-violet-400 bg-violet-500/10 px-1.5 py-0.5 rounded">.env</code> file:</p>
          <div className="p-4 rounded-lg bg-zinc-950 font-mono text-sm space-y-2">
            <p className="text-zinc-500"># Stripe (replace with your live keys)</p>
            <p className="text-emerald-400">STRIPE_API_KEY=sk_live_your_stripe_secret_key</p>
            <p className="text-emerald-400">STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret</p>
            <p className="text-zinc-500 mt-3"># MongoDB (already configured)</p>
            <p className="text-zinc-600">MONGO_URL=mongodb://localhost:27017</p>
          </div>
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
            <p className="text-red-300 text-sm">
              <strong>Important:</strong> Never share your secret keys publicly. After updating .env, restart the backend service for changes to take effect.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Current Pricing Summary */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] text-base">Your Pricing Structure (200% Profit Margin)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 text-zinc-400 font-medium">Plan</th>
                  <th className="text-right py-2 text-zinc-400 font-medium">USD</th>
                  <th className="text-right py-2 text-zinc-400 font-medium">BDT</th>
                  <th className="text-right py-2 text-zinc-400 font-medium">Credits</th>
                  <th className="text-right py-2 text-zinc-400 font-medium">Custom Agents</th>
                </tr>
              </thead>
              <tbody className="text-zinc-300">
                <tr className="border-b border-white/5"><td className="py-2">Free</td><td className="text-right">$0</td><td className="text-right">$0</td><td className="text-right">50</td><td className="text-right">0</td></tr>
                <tr className="border-b border-white/5"><td className="py-2">Starter</td><td className="text-right">$29</td><td className="text-right">3,100</td><td className="text-right">500</td><td className="text-right">2</td></tr>
                <tr className="border-b border-white/5"><td className="py-2">Pro</td><td className="text-right">$79</td><td className="text-right">8,400</td><td className="text-right">2,000</td><td className="text-right">5</td></tr>
                <tr><td className="py-2">Business</td><td className="text-right">$199</td><td className="text-right">21,100</td><td className="text-right">6,000</td><td className="text-right">Unlimited</td></tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );

