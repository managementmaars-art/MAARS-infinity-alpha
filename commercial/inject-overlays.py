"""Convert black placeholders to chroma-key magenta + inject overlay cards."""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace black placeholders with magenta chroma-key (distinctive, unlikely in source video)
html = html.replace('background:#000', 'background:#FF00FF')

OVERLAYS = {
    'vid-1': '<div style="position:absolute;bottom:120px;left:0;right:0;text-align:center;z-index:10"><div style="display:inline-block;padding:18px 48px;background:rgba(0,0,0,.85);border-radius:18px"><p style="font-family:Outfit,sans-serif;font-size:48px;font-weight:800;color:#fff;margin:0">You don\'t know where to start.</p></div></div>',

    'vid-2': '<div style="position:absolute;bottom:120px;left:0;right:0;text-align:center;z-index:10"><div style="display:inline-block;padding:18px 48px;background:rgba(0,0,0,.85);border-radius:18px"><p style="font-family:Outfit,sans-serif;font-size:48px;font-weight:800;color:#fff;margin:0">You have a team. They cost too much.</p></div></div>',

    'vid-3': '<div style="position:absolute;bottom:120px;left:0;right:0;text-align:center;z-index:10"><div style="display:inline-block;padding:18px 48px;background:rgba(0,0,0,.85);border-radius:18px"><p style="font-family:Outfit,sans-serif;font-size:46px;font-weight:800;color:#fff;margin:0">You have skills. You don\'t know what to sell.</p></div></div>',

    'vid-4': '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:10"><h1 style="font-family:Outfit,sans-serif;font-size:120px;font-weight:900;background:linear-gradient(90deg,#4FD1C5,#A78BFA,#F472B6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;line-height:1.05;margin:0">What if 458 specialists<br>worked for you tonight?</h1></div>',

    'vid-10': '<div style="position:absolute;top:80px;right:80px;width:540px;background:rgba(15,23,42,.95);border:2px solid #34D399;border-radius:20px;padding:28px;z-index:10;box-shadow:0 30px 80px rgba(0,0,0,.8)"><div style="font-family:Inter,sans-serif;font-size:14px;color:#34D399;text-transform:uppercase;letter-spacing:.2em;margin-bottom:14px;font-weight:700">Inbox &middot; last 60 seconds</div><div style="font-family:Inter,sans-serif;color:#fff;font-size:18px;line-height:1.7">&check; Re: Yes, interested<br>&check; Re: Send a deck<br>&check; Re: Let\'s book a call<br>&check; Re: Pricing question<br><span style="color:#34D399;font-weight:700;font-size:24px">132 replies &middot; 23 demos booked</span></div></div>',

    'vid-12': '<div style="position:absolute;top:60px;left:50%;transform:translateX(-50%);width:600px;background:rgba(15,23,42,.95);border:2px solid #FBBF24;border-radius:20px;padding:24px;z-index:10;box-shadow:0 30px 80px rgba(0,0,0,.85)"><div style="font-family:Inter,sans-serif;font-size:14px;color:#FBBF24;text-transform:uppercase;letter-spacing:.2em;font-weight:700;margin-bottom:8px">CodeFuel &middot; New Order &middot; Brazil</div><div style="font-family:Outfit,sans-serif;font-size:36px;font-weight:800;color:#fff">S&atilde;o Paulo &middot; $89.00</div><div style="font-family:Inter,sans-serif;font-size:16px;color:#A1A1AA;margin-top:8px">First international sale</div></div>',

    'vid-13': '<div style="position:absolute;bottom:80px;left:80px;width:540px;background:rgba(15,23,42,.95);border:2px solid #34D399;border-radius:20px;padding:28px;z-index:10;box-shadow:0 30px 80px rgba(0,0,0,.85)"><div style="font-family:Inter,sans-serif;font-size:14px;color:#34D399;text-transform:uppercase;letter-spacing:.2em;margin-bottom:14px;font-weight:700">FORMA &middot; Today\'s Orders</div><div style="font-family:Outfit,sans-serif;font-size:64px;font-weight:900;color:#fff;line-height:1">247</div><div style="font-family:Inter,sans-serif;color:#A1A1AA;font-size:18px;margin-top:8px">orders &middot; 78 international &middot; $94 avg cart</div></div>',

    'vid-16': '<div style="position:absolute;top:80px;right:80px;width:540px;background:rgba(15,23,42,.95);border:2px solid #4FD1C5;border-radius:20px;padding:28px;z-index:10;box-shadow:0 30px 80px rgba(0,0,0,.85)"><div style="font-family:Inter,sans-serif;font-size:14px;color:#4FD1C5;text-transform:uppercase;letter-spacing:.2em;margin-bottom:14px;font-weight:700">Workflow Status &middot; Live</div><div style="font-family:Inter,sans-serif;color:#fff;font-size:18px;line-height:1.8">&check; Lead qualified<br>&check; Email sent<br>&check; Meeting scheduled<br>&check; Invoice processed<br>&check; Customer onboarded</div></div>',

    'vid-17': '<div style="position:absolute;top:80px;left:50%;transform:translateX(-50%);width:640px;background:rgba(15,23,42,.95);border:2px solid #F472B6;border-radius:20px;padding:28px;z-index:10;box-shadow:0 30px 80px rgba(0,0,0,.85)"><div style="font-family:Inter,sans-serif;font-size:14px;color:#F472B6;text-transform:uppercase;letter-spacing:.2em;margin-bottom:14px;font-weight:700">Sephora Buying Team</div><div style="font-family:Outfit,sans-serif;font-size:36px;font-weight:800;color:#fff;line-height:1.2">Re: FORMA wholesale partnership</div><div style="font-family:Outfit,sans-serif;font-size:48px;font-weight:900;color:#34D399;margin-top:14px">APPROVED &check;</div></div>',

    'vid-22': '<div style="position:absolute;bottom:80px;left:80px;width:600px;background:rgba(15,23,42,.95);border:2px solid #A78BFA;border-radius:20px;padding:28px;z-index:10;box-shadow:0 30px 80px rgba(0,0,0,.85)"><div style="font-family:Inter,sans-serif;font-size:14px;color:#A78BFA;text-transform:uppercase;letter-spacing:.2em;margin-bottom:12px;font-weight:700">CodeFuel &middot; Live Dashboard</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:18px"><div><div style="font-family:Outfit,sans-serif;font-size:42px;font-weight:900;color:#fff;line-height:1">$48,200</div><div style="font-size:14px;color:#A1A1AA;margin-top:4px">MRR</div></div><div><div style="font-family:Outfit,sans-serif;font-size:42px;font-weight:900;color:#fff;line-height:1">4,847</div><div style="font-size:14px;color:#A1A1AA;margin-top:4px">subscribers</div></div><div><div style="font-family:Outfit,sans-serif;font-size:42px;font-weight:900;color:#34D399;line-height:1">+42%</div><div style="font-size:14px;color:#A1A1AA;margin-top:4px">margin</div></div><div><div style="font-family:Outfit,sans-serif;font-size:42px;font-weight:900;color:#fff;line-height:1">23</div><div style="font-size:14px;color:#A1A1AA;margin-top:4px">cities</div></div></div></div>',

    'vid-23': '<div style="position:absolute;bottom:80px;right:80px;width:580px;background:rgba(15,23,42,.95);border:2px solid #34D399;border-radius:20px;padding:28px;z-index:10;box-shadow:0 30px 80px rgba(0,0,0,.85)"><div style="font-family:Inter,sans-serif;font-size:14px;color:#34D399;text-transform:uppercase;letter-spacing:.2em;margin-bottom:12px;font-weight:700">David\'s Plumbing Supply &middot; Today</div><div style="font-family:Outfit,sans-serif;font-size:56px;font-weight:900;color:#fff;line-height:1">$22,400</div><div style="font-family:Inter,sans-serif;color:#A1A1AA;font-size:16px;margin-top:12px;line-height:1.6">&check; 47 cold calls made<br>&check; 213 emails sent<br>&check; 18 invoices auto-processed<br><span style="color:#34D399;font-weight:700">Costs cut: $13,500/mo &middot; 60+ hrs/wk back</span></div></div>',

    'vid-24': '<div style="position:absolute;top:60px;left:50%;transform:translateX(-50%);padding:18px 36px;background:rgba(15,23,42,.95);border:2px solid #A78BFA;border-radius:999px;z-index:10;box-shadow:0 20px 60px rgba(0,0,0,.85)"><span style="font-family:Outfit,sans-serif;font-size:24px;font-weight:800;color:#fff">FORMA &middot; Now at Sephora</span></div><div style="position:absolute;bottom:120px;left:0;right:0;text-align:center;z-index:10"><div style="display:inline-block;padding:14px 36px;background:rgba(0,0,0,.85);border-radius:999px"><span style="font-family:Outfit,sans-serif;font-size:32px;font-weight:800;color:#fff">MRR $84,200 &middot; 11 countries &middot; 2 retail accounts</span></div></div>',

    'vid-25': '<div style="position:absolute;bottom:120px;left:0;right:0;text-align:center;z-index:10"><div style="display:inline-block;padding:18px 48px;background:rgba(0,0,0,.85);border-radius:999px;border:2px solid #A78BFA"><span style="font-family:Outfit,sans-serif;font-size:42px;font-weight:800;background:linear-gradient(90deg,#4FD1C5,#A78BFA,#F472B6);-webkit-background-clip:text;-webkit-text-fill-color:transparent">From nothing. From chaos. From plateau.</span></div></div>',

    'vid-26': '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:10"><h1 style="font-family:Outfit,sans-serif;font-size:160px;font-weight:900;letter-spacing:.3em;color:#fff;margin:0;text-shadow:0 0 100px rgba(167,139,250,.6)">MAARS COMMAND</h1></div><div style="position:absolute;bottom:160px;left:0;right:0;text-align:center;z-index:10"><p style="font-family:Inter,sans-serif;font-size:32px;color:#A1A1AA;letter-spacing:.1em;margin:0">Your AI Workforce. Live.</p></div>',

    'vid-27': '<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:10;gap:40px"><div style="padding:32px 80px;background:linear-gradient(90deg,#4FD1C5,#A78BFA);border-radius:999px;box-shadow:0 30px 80px rgba(167,139,250,.5)"><span style="font-family:Outfit,sans-serif;font-size:48px;font-weight:800;color:#030712">Start Free at maars.ai</span></div><p style="font-family:JetBrains Mono,monospace;font-size:24px;color:#A78BFA;margin:0">no credit card &middot; 458 agents &middot; live today</p></div>',
}

# Insert overlay HTML right after the magenta placeholder div for each scene
inserted = 0
for vid_id, overlay in OVERLAYS.items():
    pattern = r'(<div id="' + vid_id + r'"[^>]*>\s*<div[^>]*background:#FF00FF[^>]*></div>)'
    new_html, n = re.subn(pattern, lambda m: m.group(1) + overlay, html, count=1)
    if n > 0:
        inserted += 1
        html = new_html
    else:
        print(f"WARN: pattern not matched for {vid_id}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"OK: chroma-key applied; {inserted}/{len(OVERLAYS)} overlay cards injected")
