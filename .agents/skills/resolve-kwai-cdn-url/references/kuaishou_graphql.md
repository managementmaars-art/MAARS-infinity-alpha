# Kuaishou GraphQL notes (for CDN extraction)

## Endpoints
- `https://www.kuaishou.com/graphql`
- `https://live.kuaishou.com/m_graphql`

Both typically require a valid browser cookie (logged-in session) to return video URLs.

## Operation
Use `visionVideoDetail` with `photoId` from the share URL.

Example payload:

```json
{
  "operationName": "visionVideoDetail",
  "query": "query visionVideoDetail($photoId: String) { visionVideoDetail(photoId: $photoId) { photo { photoUrl mainNoWatermarkUrl mainUrl } } }",
  "variables": {"photoId": "<PHOTO_ID>"}
}
```

## Where to find photoId
- URL path like `/short-video/<photoId>`
- Query params like `photoId` or `shareObjectId`
- Short links (e.g. `https://v.kuaishou.com/...`) redirect to a URL containing `photoId`.

## Output fields
`photoUrl` is usually the best CDN URL. If missing, check `mainNoWatermarkUrl` or other URL-like fields.
