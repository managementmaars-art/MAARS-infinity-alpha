#!/usr/bin/env python3
"""
Extract all available public metadata from a Loom video URL.
Usage: python3 loom_meta.py "https://www.loom.com/share/VIDEO_ID"
"""

import sys, json, re, urllib.request


def get_loom_meta(url: str) -> dict:
    video_id = url.rstrip("/").split("/")[-1].split("?")[0]

    # oembed: title, description, duration, thumbnail
    oembed = json.loads(urllib.request.urlopen(
        f"https://www.loom.com/v1/oembed?url={url}"
    ).read())

    # GraphQL: transcript status + paths
    gql_payload = json.dumps({
        "query": """query T($id: ID!) {
            fetchVideoTranscript(videoId: $id) {
                ... on VideoTranscriptDetails {
                    transcript_url captions_url transcription_status processing_service
                }
            }
        }""",
        "variables": {"videoId": video_id}
    }).encode()

    gql_req = urllib.request.Request(
        "https://www.loom.com/graphql",
        data=gql_payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    gql = json.loads(urllib.request.urlopen(gql_req).read())
    transcript_info = gql.get("data", {}).get("fetchVideoTranscript", {})

    return {
        "video_id": video_id,
        "title": oembed.get("title"),
        "description": oembed.get("description"),
        "duration_sec": oembed.get("duration"),
        "thumbnail_url": oembed.get("thumbnail_url"),
        "embed_url": f"https://www.loom.com/embed/{video_id}",
        "transcript_status": transcript_info.get("transcription_status"),
        "transcript_url_path": transcript_info.get("transcript_url"),
        "captions_url_path": transcript_info.get("captions_url"),
    }


def download_thumbnail(thumb_url: str, out_path: str = "/tmp/loom_thumb.gif") -> str:
    urllib.request.urlretrieve(thumb_url, out_path)
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 loom_meta.py <loom_url>")
        sys.exit(1)

    meta = get_loom_meta(sys.argv[1])
    print(json.dumps(meta, indent=2))

    if meta.get("thumbnail_url"):
        path = download_thumbnail(meta["thumbnail_url"])
        print(f"\nThumbnail saved to: {path}")
        print("Run analyze_video.py to analyze with Gemini.")
