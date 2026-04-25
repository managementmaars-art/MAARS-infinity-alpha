#!/bin/bash
# Higgsfield clip downloads - batch 2 (the 13 NEW URLs not in batch 1)
# Saved by timestamp; we'll rename after visual inspection.

URLS=(
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013543_903f9806-0247-4d01-812f-2b79b7b0bd8e.mp4|raw_013543.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013420_3a0dbbdd-348c-4d61-ac65-773092a91d67.mp4|raw_013420.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_013132_d11d5567-f926-4c7c-8459-0e6e34a42f5c.mp4|raw_013132.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012926_05102516-6569-44e6-bd5e-b3358cd7e99f.mp4|raw_012926.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012757_611be014-befb-4cf4-8cbd-53099145544b.mp4|raw_012757.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012519_200de92e-e364-468e-9b3e-27eb1e6fe453.mp4|raw_012519.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012417_3567a0e9-c0a0-4df0-b048-8ac3c44f333e.mp4|raw_012417.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012359_78a498b4-1d27-4777-941b-11ba06e4dedf.mp4|raw_012359.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012329_08836d44-183e-4c4b-9b76-063ad2f57963.mp4|raw_012329.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012255_ca838c28-0916-41ef-bc8e-7d20bc56920f.mp4|raw_012255.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012234_fb3ed0fa-277d-4682-9f70-eeadc8cb6fd9.mp4|raw_012234.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_012132_185c4701-b50e-4ff2-b5a2-ffc8ecade79a.mp4|raw_012132.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_011421_0784301c-eb53-45f4-aa44-97baffba6be4.mp4|raw_011421.mp4"
)
mkdir -p raw
count=0
for entry in "${URLS[@]}"; do
  url="${entry%%|*}"
  name="raw/${entry##*|}"
  if [ -f "$name" ] && [ -s "$name" ]; then continue; fi
  curl -sSL -o "$name" "$url" && count=$((count+1))
done
echo "Downloaded $count new files"
du -h raw/*.mp4 2>/dev/null
