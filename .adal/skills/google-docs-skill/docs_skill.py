#!/usr/bin/env python3
"""
Google Docs Skill - Create, read, write, share, and export Google Docs.

Usage:
    python docs_skill.py list [--limit N] [--account EMAIL]
    python docs_skill.py create --title "Name" [--body "Text"] [--file path/to/file.md] [--share EMAIL] [--account EMAIL]
    python docs_skill.py get DOC_ID [--account EMAIL]
    python docs_skill.py read DOC_ID [--account EMAIL]
    python docs_skill.py update DOC_ID --body "Content" [--account EMAIL]
    python docs_skill.py update DOC_ID --file path/to/file.md [--account EMAIL]
    python docs_skill.py append DOC_ID --text "Content" [--account EMAIL]
    python docs_skill.py insert DOC_ID --text "Content" --index N [--account EMAIL]
    python docs_skill.py replace DOC_ID --find "old" --replace "new" [--account EMAIL]
    python docs_skill.py share DOC_ID --email EMAIL [--role reader|writer|commenter] [--account EMAIL]
    python docs_skill.py export DOC_ID --format FORMAT [--output PATH] [--account EMAIL]
    python docs_skill.py from-markdown FILE [--title "Name"] [--share EMAIL] [--account EMAIL]
    python docs_skill.py accounts
    python docs_skill.py login [--account EMAIL]
    python docs_skill.py logout [--account EMAIL]

Export formats: pdf, docx, txt, html, md, odt, rtf
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import io
except ImportError:
    print("Error: Google API libraries not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

SKILL_DIR = Path(__file__).parent
TOKENS_DIR = SKILL_DIR / "tokens"
CREDENTIALS_FILE = SKILL_DIR / "credentials.json"
OUTPUT_DIR = SKILL_DIR / "output"

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

EXPORT_FORMATS = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "html": "text/html",
    "md": "text/plain",
    "odt": "application/vnd.oasis.opendocument.text",
    "rtf": "application/rtf",
}

TOKENS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def get_credentials_file() -> Path:
    """Get credentials file, falling back to gmail-skill shared creds."""
    if CREDENTIALS_FILE.exists():
        return CREDENTIALS_FILE

    for skill in ["gmail-skill", "google-sheets-skill", "google-slides-skill"]:
        shared = Path.home() / ".claude/skills" / skill / "credentials.json"
        if shared.exists():
            return shared

    print("\n" + "=" * 60)
    print("FIRST-TIME SETUP")
    print("=" * 60)
    print("\nYou need Google OAuth credentials.")
    print("If you have gmail-skill or other Google skills set up, those credentials will work.")
    print("\nOtherwise:")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Create OAuth client (Desktop app)")
    print("3. Download JSON and save as:")
    print(f"   {CREDENTIALS_FILE}")
    print("4. Enable Google Docs API and Google Drive API in your project")
    print("=" * 60 + "\n")
    sys.exit(1)


def get_token_path(account: str = None) -> Path:
    """Get token file path for account."""
    if account:
        safe = "".join(c if c.isalnum() or c in ".-_" else "_" for c in account)
        return TOKENS_DIR / f"token_{safe}.json"
    tokens = list(TOKENS_DIR.glob("token_*.json"))
    return tokens[0] if tokens else TOKENS_DIR / "token_default.json"


def get_credentials(account: str = None):
    """Get or refresh credentials."""
    creds_file = get_credentials_file()
    token_path = get_token_path(account)
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
            creds = flow.run_local_server(port=9996)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds


def get_docs_service(account: str = None):
    """Get Google Docs API service."""
    creds = get_credentials(account)
    return build("docs", "v1", credentials=creds)


def get_drive_service(account: str = None):
    """Get Google Drive API service."""
    creds = get_credentials(account)
    return build("drive", "v3", credentials=creds)


def output_json(data):
    """Output JSON response."""
    print(json.dumps(data, indent=2, default=str))


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text_from_doc(doc):
    """Extract plain text from document content."""
    text = []
    content = doc.get("body", {}).get("content", [])

    for element in content:
        if "paragraph" in element:
            for elem in element["paragraph"].get("elements", []):
                if "textRun" in elem:
                    text.append(elem["textRun"].get("content", ""))

    return "".join(text)


# ---------------------------------------------------------------------------
# Markdown-to-Google-Docs converter
# ---------------------------------------------------------------------------

def _parse_inline_formatting(text):
    """Parse inline markdown (bold, italic) and return segments.

    Each segment is a dict: {"text": str, "bold": bool, "italic": bool}
    """
    segments = []
    # Pattern matches **bold**, *italic*, ***bold+italic***, __bold__, _italic___
    # Process in order: bold+italic first, then bold, then italic
    # We use a simple state-machine approach for reliability.

    # Regex that captures bold+italic (***), bold (**), italic (*) markers
    # We handle __ and _ as well
    pattern = re.compile(
        r'(\*\*\*|___)'   # bold+italic marker
        r'|(\*\*|__)'     # bold marker
        r'|(\*|_)'        # italic marker
    )

    pos = 0
    bold = False
    italic = False
    buf = []

    def flush():
        t = "".join(buf)
        if t:
            segments.append({"text": t, "bold": bold, "italic": italic})
        buf.clear()

    raw = text
    matches = list(pattern.finditer(raw))

    if not matches:
        return [{"text": text, "bold": False, "italic": False}]

    for m in matches:
        # Append text before this marker
        before = raw[pos:m.start()]
        if before:
            buf.append(before)

        marker = m.group(0)
        if marker in ("***", "___"):
            flush()
            bold = not bold
            italic = not italic
        elif marker in ("**", "__"):
            flush()
            bold = not bold
        elif marker in ("*", "_"):
            flush()
            italic = not italic

        pos = m.end()

    # Remaining text after last marker
    remaining = raw[pos:]
    if remaining:
        buf.append(remaining)
    flush()

    return segments


def markdown_to_requests(markdown_text):
    """Convert markdown to Google Docs API requests.

    Handles:
    - First # heading → TITLE style (document title in body)
    - Non-heading text immediately after title → SUBTITLE style
    - Subsequent # headings → HEADING_1
    - ## → HEADING_2, ### → HEADING_3, #### → HEADING_4
    - **bold** and *italic* inline formatting
    - - bullet lists (unordered)
    - 1. numbered lists (ordered)
    - --- horizontal rules (paragraph break)
    - Regular paragraphs
    """
    requests_list = []
    style_requests = []
    current_index = 1  # Google Docs uses 1-based indexing

    lines = markdown_text.split("\n")
    i = 0
    seen_first_h1 = False  # Track whether we've seen the document title
    in_subtitle_zone = False  # After title, before first blank line
    last_was_blank = False  # Track consecutive blank lines
    last_was_list_item = False  # Track bullet/numbered list items

    def _is_list_line(l):
        return bool(re.match(r'^\s*[-*+]\s+', l) or re.match(r'^\s*\d+\.\s+', l))

    while i < len(lines):
        line = lines[i]
        i += 1

        # Handle empty lines: collapse consecutive blanks, skip between list items
        if line.strip() == "":
            if in_subtitle_zone:
                in_subtitle_zone = False
            # Skip blank lines between consecutive list items
            if last_was_list_item and i < len(lines) and _is_list_line(lines[i]):
                continue
            # Skip consecutive blank lines (collapse to max one)
            if last_was_blank:
                continue
            # Skip blank line right before a heading (headings have their own spacing)
            if i < len(lines) and re.match(r'^#{1,4}\s+', lines[i]):
                last_was_blank = True
                continue
            last_was_blank = True
            last_was_list_item = False
            insert_req = {
                "insertText": {
                    "location": {"index": current_index},
                    "text": "\n"
                }
            }
            requests_list.append(insert_req)
            current_index += 1
            continue

        # --- Horizontal rule
        if re.match(r'^-{3,}$', line.strip()) or re.match(r'^\*{3,}$', line.strip()):
            insert_req = {
                "insertText": {
                    "location": {"index": current_index},
                    "text": "\n"
                }
            }
            requests_list.append(insert_req)
            current_index += 1
            continue

        # Reset blank line tracker for content lines
        last_was_blank = False

        # Determine paragraph type
        heading_level = 0
        is_bullet = False
        is_numbered = False
        is_subtitle = False
        content_text = line

        # Headers: # through ####
        header_match = re.match(r'^(#{1,4})\s+(.+)$', line)
        if header_match:
            heading_level = len(header_match.group(1))
            content_text = header_match.group(2)

        # Bullet list: - item or * item
        elif re.match(r'^\s*[-*+]\s+', line):
            is_bullet = True
            content_text = re.sub(r'^\s*[-*+]\s+', '', line)

        # Numbered list: 1. item
        elif re.match(r'^\s*\d+\.\s+', line):
            is_numbered = True
            content_text = re.sub(r'^\s*\d+\.\s+', '', line)

        # Check if this non-heading text is in the subtitle zone
        elif in_subtitle_zone and not header_match:
            is_subtitle = True

        # Track list items for blank line collapsing
        last_was_list_item = is_bullet or is_numbered

        # Parse inline formatting
        segments = _parse_inline_formatting(content_text)

        # Build the full text for this paragraph
        para_text = "".join(seg["text"] for seg in segments) + "\n"

        # Insert the paragraph text
        insert_req = {
            "insertText": {
                "location": {"index": current_index},
                "text": para_text
            }
        }
        requests_list.append(insert_req)

        para_start = current_index
        para_end = current_index + len(para_text)

        # Apply heading style
        if heading_level > 0:
            if heading_level == 1 and not seen_first_h1:
                # First # heading → TITLE style
                seen_first_h1 = True
                in_subtitle_zone = True
                style_requests.append({
                    "updateParagraphStyle": {
                        "range": {"startIndex": para_start, "endIndex": para_end},
                        "paragraphStyle": {"namedStyleType": "TITLE"},
                        "fields": "namedStyleType"
                    }
                })
            else:
                # Subsequent headings: # → HEADING_1, ## → HEADING_2, etc.
                heading_map = {
                    1: "HEADING_1",
                    2: "HEADING_2",
                    3: "HEADING_3",
                    4: "HEADING_4",
                }
                style_requests.append({
                    "updateParagraphStyle": {
                        "range": {"startIndex": para_start, "endIndex": para_end},
                        "paragraphStyle": {"namedStyleType": heading_map[heading_level]},
                        "fields": "namedStyleType"
                    }
                })
                in_subtitle_zone = False

        # Apply subtitle style
        if is_subtitle:
            style_requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": para_start, "endIndex": para_end},
                    "paragraphStyle": {"namedStyleType": "SUBTITLE"},
                    "fields": "namedStyleType"
                }
            })

        # Apply bullet list style
        if is_bullet:
            style_requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": para_start, "endIndex": para_end},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                }
            })

        # Apply numbered list style
        if is_numbered:
            style_requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": para_start, "endIndex": para_end},
                    "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN"
                }
            })

        # Apply inline bold/italic formatting
        seg_offset = current_index
        for seg in segments:
            seg_len = len(seg["text"])
            if seg_len == 0:
                continue

            seg_start = seg_offset
            seg_end = seg_offset + seg_len

            if seg["bold"]:
                style_requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": seg_start, "endIndex": seg_end},
                        "textStyle": {"bold": True},
                        "fields": "bold"
                    }
                })
            if seg["italic"]:
                style_requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": seg_start, "endIndex": seg_end},
                        "textStyle": {"italic": True},
                        "fields": "italic"
                    }
                })

            seg_offset += seg_len

        current_index = para_end

    # Combine: insert requests first, then style requests
    # Google Docs API processes requests in order. We insert all text first,
    # then apply styles. This is safe because we pre-computed all indices.
    return requests_list + style_requests


def _resolve_body_content(args):
    """Resolve body content from --body, --file, or --content flags.

    Returns the content string or None.
    """
    # --file takes priority: read content from file
    file_path = getattr(args, "file", None)
    if file_path:
        p = Path(file_path)
        if not p.exists():
            output_json({"error": f"File not found: {file_path}"})
            sys.exit(1)
        with open(p, "r") as f:
            return f.read()

    # --body is the primary text flag
    body = getattr(args, "body", None)
    if body:
        return body

    # --content for backward compatibility
    content = getattr(args, "content", None)
    if content:
        return content

    return None


# ---------------------------------------------------------------------------
# Sharing helper
# ---------------------------------------------------------------------------

def share_document(drive, doc_id, email, role="writer"):
    """Share a document with a specific email address.

    Roles: reader, writer, commenter
    """
    permission = {
        "type": "user",
        "role": role,
        "emailAddress": email,
    }
    result = drive.permissions().create(
        fileId=doc_id,
        body=permission,
        sendNotificationEmail=True,
        fields="id,role,emailAddress"
    ).execute()
    return result


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def add_comment(file_id: str, content: str, quoted_text: str = None, account: str = None):
    """Add a comment to a Google Doc, optionally anchored to quoted text."""
    drive = get_drive_service(account)
    body = {"content": content}
    if quoted_text:
        body["anchor"] = None  # Will be set via quotedFileContent
        body["quotedFileContent"] = {"value": quoted_text}
    result = drive.comments().create(
        fileId=file_id,
        body=body,
        fields="id,content,quotedFileContent,author,createdTime",
    ).execute()
    return result


def list_comments(file_id: str, account: str = None):
    """List comments on a Google Doc."""
    drive = get_drive_service(account)
    result = drive.comments().list(
        fileId=file_id,
        fields="comments(id,content,quotedFileContent,author,createdTime,resolved)",
    ).execute()
    return result.get("comments", [])


def resolve_comment(file_id: str, comment_id: str, account: str = None):
    """Resolve a comment on a Google Doc."""
    drive = get_drive_service(account)
    result = drive.comments().update(
        fileId=file_id,
        commentId=comment_id,
        body={"resolved": True},
        fields="id,content,resolved",
    ).execute()
    return result


def delete_comment(file_id: str, comment_id: str, account: str = None):
    """Delete a comment from a Google Doc."""
    drive = get_drive_service(account)
    drive.comments().delete(fileId=file_id, commentId=comment_id).execute()
    return {"success": True, "deleted": comment_id}


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_comment(args):
    """Add a comment to a document, optionally anchored to quoted text."""
    account = getattr(args, "account", None)
    result = add_comment(args.doc_id, args.text, args.quote, account)
    output_json({"success": True, "comment": result})


def cmd_list_comments(args):
    """List comments on a document."""
    account = getattr(args, "account", None)
    comments = list_comments(args.doc_id, account)
    output_json({"comments": comments, "total": len(comments)})


def cmd_resolve_comment(args):
    """Resolve a comment."""
    account = getattr(args, "account", None)
    result = resolve_comment(args.doc_id, args.comment_id, account)
    output_json({"success": True, "comment": result})


def cmd_delete_comment(args):
    """Delete a comment."""
    account = getattr(args, "account", None)
    result = delete_comment(args.doc_id, args.comment_id, account)
    output_json(result)


def cmd_accounts(args):
    """List authenticated accounts."""
    accounts = []
    for f in TOKENS_DIR.glob("token_*.json"):
        accounts.append({"name": f.stem.replace("token_", ""), "file": str(f)})
    output_json({"accounts": accounts})


def cmd_login(args):
    """Authenticate with Google."""
    creds = get_credentials(args.account)
    output_json({"success": True, "account": args.account or "default"})


def cmd_upload_image(args):
    """Upload an image to Google Drive and return a public URL."""
    from googleapiclient.http import MediaFileUpload
    drive = get_drive_service(args.account)

    file_path = Path(args.file)
    if not file_path.exists():
        output_json({"error": f"File not found: {args.file}"})
        return

    # Detect mime type
    ext = file_path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml"}
    mime_type = mime_map.get(ext, "application/octet-stream")

    # Upload to Drive
    file_metadata = {"name": file_path.name}
    if args.folder_id:
        file_metadata["parents"] = [args.folder_id]

    media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)
    uploaded = drive.files().create(
        body=file_metadata, media_body=media,
        fields="id, name, webViewLink, webContentLink"
    ).execute()

    file_id = uploaded["id"]

    # Make publicly readable
    drive.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"}
    ).execute()

    # Get the direct download link
    file_info = drive.files().get(
        fileId=file_id,
        fields="id, name, webViewLink, webContentLink, thumbnailLink"
    ).execute()

    # Build direct image URLs
    # lh3 format serves directly (200 OK, image/jpeg) — works for embedding in Gamma, etc.
    # drive.google.com/uc format does a 303 redirect — many services can't follow it
    lh3_url = f"https://lh3.googleusercontent.com/d/{file_id}"
    drive_url = f"https://drive.google.com/uc?export=view&id={file_id}"

    output_json({
        "id": file_id,
        "name": file_info.get("name"),
        "directUrl": lh3_url,
        "driveUrl": drive_url,
        "webViewLink": file_info.get("webViewLink"),
        "webContentLink": file_info.get("webContentLink"),
    })


def cmd_logout(args):
    """Remove authentication for account."""
    path = get_token_path(args.account)
    if path.exists():
        path.unlink()
        output_json({"success": True})
    else:
        output_json({"error": "Account not found"})


def cmd_list(args):
    """List Google Docs."""
    drive = get_drive_service(args.account)
    results = drive.files().list(
        q="mimeType='application/vnd.google-apps.document'",
        pageSize=args.limit,
        fields="files(id, name, modifiedTime, webViewLink)",
        orderBy="modifiedTime desc"
    ).execute()
    files = results.get("files", [])
    output_json({"documents": files, "count": len(files)})


def cmd_create(args):
    """Create a new Google Doc with optional markdown body and sharing."""
    docs = get_docs_service(args.account)

    doc = docs.documents().create(body={"title": args.title}).execute()
    doc_id = doc.get("documentId")

    content = _resolve_body_content(args)

    if content:
        # Use markdown converter for rich formatting
        reqs = markdown_to_requests(content)
        if reqs:
            docs.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": reqs}
            ).execute()

    result = {
        "success": True,
        "documentId": doc_id,
        "title": args.title,
        "url": f"https://docs.google.com/document/d/{doc_id}/edit"
    }

    # Share if requested
    share_emails = getattr(args, "share", None)
    if share_emails:
        drive = get_drive_service(args.account)
        shared_with = []
        for email in share_emails:
            try:
                share_document(drive, doc_id, email, "writer")
                shared_with.append(email)
            except Exception as e:
                shared_with.append({"email": email, "error": str(e)})
        result["sharedWith"] = shared_with

    output_json(result)


def cmd_get(args):
    """Get document metadata."""
    docs = get_docs_service(args.account)
    doc = docs.documents().get(documentId=args.doc_id).execute()

    output_json({
        "documentId": doc.get("documentId"),
        "title": doc.get("title"),
        "url": f"https://docs.google.com/document/d/{doc.get('documentId')}/edit",
        "revisionId": doc.get("revisionId"),
    })


def cmd_read(args):
    """Read document content as plain text."""
    docs = get_docs_service(args.account)
    doc = docs.documents().get(documentId=args.doc_id).execute()

    text = extract_text_from_doc(doc)

    output_json({
        "documentId": doc.get("documentId"),
        "title": doc.get("title"),
        "content": text,
        "length": len(text),
    })


def cmd_update(args):
    """Update/replace entire document content.

    Clears existing content, then inserts new content with markdown formatting.
    """
    docs = get_docs_service(args.account)

    content = _resolve_body_content(args)
    if not content:
        output_json({"error": "Provide --body or --file with content to update"})
        return

    # Get current document to find content range
    doc = docs.documents().get(documentId=args.doc_id).execute()
    body_content = doc.get("body", {}).get("content", [])

    # Find end index (we need to delete from index 1 to endIndex - 1)
    end_index = 1
    if body_content:
        end_index = body_content[-1].get("endIndex", 1) - 1

    batch_requests = []

    # Delete existing content (if any beyond the initial newline)
    if end_index > 1:
        batch_requests.append({
            "deleteContentRange": {
                "range": {
                    "startIndex": 1,
                    "endIndex": end_index,
                }
            }
        })

    # Apply deletion first
    if batch_requests:
        docs.documents().batchUpdate(
            documentId=args.doc_id,
            body={"requests": batch_requests}
        ).execute()

    # Now insert new content with markdown formatting
    insert_requests = markdown_to_requests(content)
    if insert_requests:
        docs.documents().batchUpdate(
            documentId=args.doc_id,
            body={"requests": insert_requests}
        ).execute()

    output_json({
        "success": True,
        "documentId": args.doc_id,
        "title": doc.get("title"),
        "contentLength": len(content),
        "url": f"https://docs.google.com/document/d/{args.doc_id}/edit",
    })


def cmd_append(args):
    """Append text to end of document."""
    docs = get_docs_service(args.account)

    doc = docs.documents().get(documentId=args.doc_id).execute()
    content = doc.get("body", {}).get("content", [])

    end_index = 1
    if content:
        end_index = content[-1].get("endIndex", 1) - 1

    reqs = [{
        "insertText": {
            "location": {"index": end_index},
            "text": args.text
        }
    }]

    docs.documents().batchUpdate(
        documentId=args.doc_id,
        body={"requests": reqs}
    ).execute()

    output_json({
        "success": True,
        "documentId": args.doc_id,
        "appendedText": args.text[:100] + "..." if len(args.text) > 100 else args.text,
    })


def cmd_insert(args):
    """Insert text at specific index."""
    docs = get_docs_service(args.account)

    reqs = [{
        "insertText": {
            "location": {"index": args.index},
            "text": args.text
        }
    }]

    docs.documents().batchUpdate(
        documentId=args.doc_id,
        body={"requests": reqs}
    ).execute()

    output_json({
        "success": True,
        "documentId": args.doc_id,
        "insertedAt": args.index,
    })


def cmd_replace(args):
    """Find and replace text in document."""
    docs = get_docs_service(args.account)

    reqs = [{
        "replaceAllText": {
            "containsText": {
                "text": args.find,
                "matchCase": True
            },
            "replaceText": args.replace
        }
    }]

    result = docs.documents().batchUpdate(
        documentId=args.doc_id,
        body={"requests": reqs}
    ).execute()

    replies = result.get("replies", [{}])
    occurrences = replies[0].get("replaceAllText", {}).get("occurrencesChanged", 0)

    output_json({
        "success": True,
        "documentId": args.doc_id,
        "replacements": occurrences,
        "find": args.find,
        "replace": args.replace,
    })


def cmd_share(args):
    """Share a document with one or more email addresses."""
    drive = get_drive_service(args.account)

    role = args.role or "writer"
    shared_with = []

    for email in args.email:
        try:
            result = share_document(drive, args.doc_id, email, role)
            shared_with.append({
                "email": email,
                "role": role,
                "permissionId": result.get("id"),
            })
        except Exception as e:
            shared_with.append({
                "email": email,
                "error": str(e),
            })

    output_json({
        "success": True,
        "documentId": args.doc_id,
        "sharedWith": shared_with,
        "url": f"https://docs.google.com/document/d/{args.doc_id}/edit",
    })


def cmd_export(args):
    """Export document to various formats."""
    drive = get_drive_service(args.account)
    docs = get_docs_service(args.account)

    fmt = args.format.lower()
    if fmt not in EXPORT_FORMATS:
        output_json({"error": f"Unknown format: {fmt}", "available": list(EXPORT_FORMATS.keys())})
        return

    mime_type = EXPORT_FORMATS[fmt]

    doc = docs.documents().get(documentId=args.doc_id).execute()
    title = doc.get("title", "document")
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title).strip()

    request = drive.files().export_media(fileId=args.doc_id, mimeType=mime_type)

    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    ext = fmt if fmt != "md" else "txt"
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = OUTPUT_DIR / f"{safe_title}.{ext}"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(file_data.getvalue())

    output_json({
        "success": True,
        "documentId": args.doc_id,
        "title": title,
        "format": fmt,
        "file": str(output_path),
        "size": output_path.stat().st_size,
    })


def cmd_from_markdown(args):
    """Create a Google Doc from a markdown file with full formatting."""
    docs = get_docs_service(args.account)

    md_path = Path(args.file)
    if not md_path.exists():
        output_json({"error": f"File not found: {args.file}"})
        return

    with open(md_path, "r") as f:
        markdown_content = f.read()

    title = args.title or md_path.stem

    doc = docs.documents().create(body={"title": title}).execute()
    doc_id = doc.get("documentId")

    reqs = markdown_to_requests(markdown_content)
    if reqs:
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": reqs}
        ).execute()

    result = {
        "success": True,
        "documentId": doc_id,
        "title": title,
        "url": f"https://docs.google.com/document/d/{doc_id}/edit",
        "sourceFile": str(md_path),
    }

    # Share if requested
    share_emails = getattr(args, "share", None)
    if share_emails:
        drive = get_drive_service(args.account)
        shared_with = []
        for email in share_emails:
            try:
                share_document(drive, doc_id, email, "writer")
                shared_with.append(email)
            except Exception as e:
                shared_with.append({"email": email, "error": str(e)})
        result["sharedWith"] = shared_with

    output_json(result)


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------

def add_account_arg(parser):
    """Add account argument to parser."""
    parser.add_argument("--account", "-a", help="Account to use")


def main():
    parser = argparse.ArgumentParser(description="Google Docs Skill")
    subs = parser.add_subparsers(dest="command")

    # accounts
    subs.add_parser("accounts").set_defaults(func=cmd_accounts)

    # login
    login = subs.add_parser("login")
    login.add_argument("--account", "-a")
    login.set_defaults(func=cmd_login)

    # logout
    logout = subs.add_parser("logout")
    logout.add_argument("--account", "-a")
    logout.set_defaults(func=cmd_logout)

    # list
    ls = subs.add_parser("list")
    ls.add_argument("--limit", "-l", type=int, default=20)
    add_account_arg(ls)
    ls.set_defaults(func=cmd_list)

    # create
    create = subs.add_parser("create")
    create.add_argument("--title", "-t", required=True, help="Document title")
    create.add_argument("--body", "-b", help="Body content (markdown-formatted)")
    create.add_argument("--file", help="Read body content from a file (markdown)")
    create.add_argument("--content", "-c", help="Initial content (plain text, backward compat)")
    create.add_argument("--share", nargs="+", help="Email address(es) to share with after creation")
    add_account_arg(create)
    create.set_defaults(func=cmd_create)

    # get
    get = subs.add_parser("get")
    get.add_argument("doc_id", help="Document ID")
    add_account_arg(get)
    get.set_defaults(func=cmd_get)

    # read
    read = subs.add_parser("read")
    read.add_argument("doc_id", help="Document ID")
    add_account_arg(read)
    read.set_defaults(func=cmd_read)

    # update
    update = subs.add_parser("update")
    update.add_argument("doc_id", help="Document ID")
    update.add_argument("--body", "-b", help="New body content (markdown-formatted)")
    update.add_argument("--file", help="Read new body content from a file (markdown)")
    add_account_arg(update)
    update.set_defaults(func=cmd_update)

    # append
    append = subs.add_parser("append")
    append.add_argument("doc_id", help="Document ID")
    append.add_argument("--text", "-t", required=True, help="Text to append")
    add_account_arg(append)
    append.set_defaults(func=cmd_append)

    # insert
    insert = subs.add_parser("insert")
    insert.add_argument("doc_id", help="Document ID")
    insert.add_argument("--text", "-t", required=True, help="Text to insert")
    insert.add_argument("--index", "-i", type=int, required=True, help="Index to insert at")
    add_account_arg(insert)
    insert.set_defaults(func=cmd_insert)

    # replace
    replace = subs.add_parser("replace")
    replace.add_argument("doc_id", help="Document ID")
    replace.add_argument("--find", "-f", required=True, help="Text to find")
    replace.add_argument("--replace", "-r", required=True, help="Replacement text")
    add_account_arg(replace)
    replace.set_defaults(func=cmd_replace)

    # share
    share = subs.add_parser("share")
    share.add_argument("doc_id", help="Document ID")
    share.add_argument("--email", "-e", nargs="+", required=True, help="Email address(es) to share with")
    share.add_argument("--role", choices=["reader", "writer", "commenter"], default="writer",
                       help="Permission role (default: writer)")
    add_account_arg(share)
    share.set_defaults(func=cmd_share)

    # export
    export = subs.add_parser("export")
    export.add_argument("doc_id", help="Document ID")
    export.add_argument("--format", "-f", required=True,
                        help="Export format: pdf, docx, txt, html, md, odt, rtf")
    export.add_argument("--output", "-o", help="Output file path")
    add_account_arg(export)
    export.set_defaults(func=cmd_export)

    # from-markdown
    from_md = subs.add_parser("from-markdown")
    from_md.add_argument("file", help="Markdown file path")
    from_md.add_argument("--title", "-t", help="Document title (defaults to filename)")
    from_md.add_argument("--share", nargs="+", help="Email address(es) to share with after creation")
    add_account_arg(from_md)
    from_md.set_defaults(func=cmd_from_markdown)

    # comment
    comment = subs.add_parser("comment")
    comment.add_argument("doc_id", help="Document ID")
    comment.add_argument("--text", "-t", required=True, help="Comment text")
    comment.add_argument("--quote", "-q", help="Quoted text to anchor the comment to")
    add_account_arg(comment)
    comment.set_defaults(func=cmd_comment)

    # list-comments
    list_cmt = subs.add_parser("list-comments")
    list_cmt.add_argument("doc_id", help="Document ID")
    add_account_arg(list_cmt)
    list_cmt.set_defaults(func=cmd_list_comments)

    # resolve-comment
    resolve_cmt = subs.add_parser("resolve-comment")
    resolve_cmt.add_argument("doc_id", help="Document ID")
    resolve_cmt.add_argument("comment_id", help="Comment ID to resolve")
    add_account_arg(resolve_cmt)
    resolve_cmt.set_defaults(func=cmd_resolve_comment)

    # delete-comment
    delete_cmt = subs.add_parser("delete-comment")
    delete_cmt.add_argument("doc_id", help="Document ID")
    delete_cmt.add_argument("comment_id", help="Comment ID to delete")
    add_account_arg(delete_cmt)
    delete_cmt.set_defaults(func=cmd_delete_comment)

    # upload-image
    upload_img = subs.add_parser("upload-image", help="Upload image to Drive, return public URL")
    upload_img.add_argument("file", help="Path to image file")
    upload_img.add_argument("--folder-id", help="Drive folder ID to upload to")
    add_account_arg(upload_img)
    upload_img.set_defaults(func=cmd_upload_image)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
