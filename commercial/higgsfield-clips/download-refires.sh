URLS=(
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_020746_6e7f0901-bd0e-4532-9ded-6a88ba9f0cae.mp4|raw_020746.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_020705_1665d35c-e3e6-4454-bd39-e04911fe0c74.mp4|raw_020705.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_020623_30c2e461-d436-464f-89e6-6651d23d8007.mp4|raw_020623.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_020602_437bb2af-c4e0-44b8-8196-4cb4649831b5.mp4|raw_020602.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_020543_303a2bf4-d97d-46a6-8db8-7c6478069f56.mp4|raw_020543.mp4"
"https://d8j0ntlcm91z4.cloudfront.net/user_3CYGFbXIbsEzu16lu2G8h4J7ihp/hf_20260419_020519_d1b82256-5409-4cfb-9012-e11dcea48510.mp4|raw_020519.mp4"
)
for entry in "${URLS[@]}"; do
  url="${entry%%|*}"
  name="raw/${entry##*|}"
  if [ -f "$name" ] && [ -s "$name" ]; then continue; fi
  curl -sSL -o "$name" "$url"
done
echo "=== refire downloads ==="
du -h raw/raw_020*.mp4 2>/dev/null
echo ""
echo "=== extracting thumbs for inspection ==="
export PATH="/c/Users/Yaleena Yara/AppData/Roaming/npm:$PATH"
for f in raw/raw_020*.mp4; do
  base=$(basename "$f" .mp4)
  out="thumbs/${base}.jpg"
  ffmpeg -ss 00:00:02 -i "$f" -frames:v 1 -vf "scale=480:-1" -q:v 5 "$out" -y -loglevel error 2>&1 | head -2
done
ls thumbs/raw_020*.jpg 2>/dev/null
