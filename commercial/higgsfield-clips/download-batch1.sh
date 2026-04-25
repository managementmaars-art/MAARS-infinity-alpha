#!/bin/bash
# Higgsfield clip downloads - batch 1 (24 assets visible, mapped chronologically newest→oldest)

URLS=(
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013626_f6a1ac56-5bac-4546-b7c5-c18daaf0c54c.mp4|clip-07-content-gen-firing.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013604_822b2f43-cf83-44fd-aa38-51631616ffea.mp4|clip-31-maars-builds-aishas-business.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013523_67617b9a-ab7d-4b40-aeed-ba354e6f22de.mp4|clip-30-maars-rebuilds-davids-business.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013502_243031b8-71d4-4f14-bb50-4eb7a5d1acbc.mp4|clip-29-maars-builds-jamals-business.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013443_617eda53-447a-49d6-8764-7569273c7585.mp4|clip-06-dashboard-reveal.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013401_6cdc8731-cb2c-4800-8abc-8b48a7768f82.mp4|clip-04-landing-reveal.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013340_8094ded5-e040-4550-80f1-f8f25018f4dc.mp4|clip-24-cta-button.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013319_8baa6668-d397-452b-8993-ec131e19ca4d.mp4|clip-23-logo-reveal.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013259_ec7f27ae-ac1c-44ce-b5d2-6c8aa17f5245.mp4|clip-22-three-lives-converge.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013241_214a122a-ed08-4afb-809e-fdca669156c3.mp4|clip-21b-aisha-scaled.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013214_d5046a9e-84ca-47d8-ab87-144fab90a810.mp4|clip-21-david-family-lunch.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013155_5e5b37d9-c4d7-498b-b1f1-4d2f5ad88314.mp4|clip-20-jamal-brand-launched.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013107_fa134704-0397-4cbe-99ff-e441a789ca5e.mp4|clip-33-aisha-wholesale-deal.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013042_20161a8e-2a33-4c1a-b115-a61183c76285.mp4|clip-32-aisha-orders-flooding.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013016_0938fa7f-cfd6-467f-bc6c-de38891b1cb0.mp4|clip-28-jamal-momentum.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012741_cbe51b71-c6ee-47a8-918d-9f901c2c7571.mp4|clip-27-david-empty-office.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012726_ef640046-058f-4d57-89d4-68f9d9d78cc7.mp4|clip-26-david-inbox-flood.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012705_2e164ed5-cafe-4343-9ee8-d24304e03629.mp4|clip-25-jamal-first-sale.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012640_e3289a52-28df-40ff-a4ed-396094c940a8.mp4|clip-05-signup-arrow.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012621_f285fe1b-c4b2-4698-9e60-9076a8286fa6.mp4|clip-03-question-hook.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012559_aa9dd072-7a5c-49fd-a5c1-a7c852c9408f.mp4|clip-02b-aisha-pain.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012456_aece97a2-d211-4282-890e-becf1e91b487.mp4|tmp/contam-02b-reroll-1.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012435_013de04b-f420-4b0e-9494-e691d0ba9c1c.mp4|clip-02-david-pain.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_011544_b9c8566f-55f8-4c0d-8582-d6e56522ebcc.mp4|clip-01-jamal-pain.mp4"
)

count=0
for entry in "${URLS[@]}"; do
  url="${entry%%|*}"
  name="${entry##*|}"
  if [ -f "$name" ] && [ -s "$name" ]; then
    echo "EXISTS: $name"
    continue
  fi
  echo "DOWNLOAD: $name"
  curl -sSL -o "$name" "$url" && count=$((count+1)) || echo "FAIL: $name"
done
echo "Downloaded $count new files"
ls -la *.mp4 2>/dev/null | wc -l
