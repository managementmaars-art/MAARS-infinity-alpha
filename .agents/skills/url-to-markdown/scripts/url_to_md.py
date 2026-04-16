#!/usr/bin/env python
from __future__ import print_function

import argparse
import collections
import datetime
import json
import os
import re
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from urllib.error import HTTPError, URLError
    from urllib.parse import quote, urlencode, urlparse
    from urllib.request import Request, urlopen
except ImportError:  # pragma: no cover
    from urllib2 import HTTPError, URLError, Request, urlopen
    from urllib import quote, urlencode
    from urlparse import urlparse


DEFAULT_TIMEOUT = 30
JINA_PREFIX_URL = "https://r.jina.ai/"
MARKDOWN_NEW_URL = "https://markdown.new/"
USER_AGENT = "url-to-md/1.1 (+https://r.jina.ai/; fallback https://markdown.new/)"
ConversionResult = collections.namedtuple(
    "ConversionResult",
    ["markdown", "headers", "status", "transport", "service_url", "provider"],
)


class MarkdownServiceError(Exception):
    def __init__(self, message, service_name=None, status_code=None):
        Exception.__init__(self, message)
        self.service_name = service_name
        self.status_code = status_code


def _normalize_headers(headers):
    normalized = {}
    for key, value in headers.items():
        normalized[str(key).lower()] = value
    return normalized


def _decode_response(response, service_name):
    headers = _normalize_headers(response.headers)
    content_type = headers.get("content-type", "")
    charset = "utf-8"

    match = re.search(r"charset=([A-Za-z0-9._-]+)", content_type)
    if match:
        charset = match.group(1)

    body = response.read()
    try:
        text = body.decode(charset, "replace")
    except LookupError:
        text = body.decode("utf-8", "replace")

    if "application/json" in content_type:
        try:
            payload = json.loads(text)
        except ValueError:
            return text, headers
        if isinstance(payload, dict):
            if payload.get("success") is False and payload.get("error"):
                raise MarkdownServiceError(str(payload.get("error")), service_name=service_name)
            if "content" in payload and payload.get("content") is not None:
                return payload.get("content"), headers
        return text, headers

    return text, headers


def _build_jina_request(url):
    service_url = JINA_PREFIX_URL + quote(url, safe=":/?&=#%")
    return Request(
        service_url,
        headers={
            "Accept": "text/markdown",
            "User-Agent": USER_AGENT,
        },
    ), service_url


def _build_markdown_new_get_request(url, method, retain_images):
    query = urlencode(
        {
            "method": method,
            "retain_images": "true" if retain_images else "false",
        }
    )
    service_url = MARKDOWN_NEW_URL + quote(url, safe=":/")
    if query:
        service_url += "?" + query
    return Request(
        service_url,
        headers={
            "Accept": "text/markdown",
            "User-Agent": USER_AGENT,
        },
    ), service_url


def _build_markdown_new_post_request(url, method, retain_images):
    payload = json.dumps(
        {
            "url": url,
            "method": method,
            "retain_images": bool(retain_images),
        }
    ).encode("utf-8")
    return Request(
        MARKDOWN_NEW_URL,
        data=payload,
        headers={
            "Accept": "text/markdown",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    ), MARKDOWN_NEW_URL


def _execute_request(request, transport, timeout, service_url, service_name, provider):
    try:
        response = urlopen(request, timeout=timeout)
        markdown, headers = _decode_response(response, service_name)
        return ConversionResult(
            markdown=markdown,
            headers=headers,
            status=getattr(response, "status", response.getcode()),
            transport=transport,
            service_url=service_url,
            provider=provider,
        )
    except HTTPError as exc:
        body = exc.read()
        try:
            detail = body.decode("utf-8", "replace").strip()
        except Exception:
            detail = ""
        message = "HTTP {0} from {1}".format(exc.code, service_name)
        if exc.code == 429:
            message += " (rate limit exceeded)"
        if detail:
            message += ": " + detail
        raise MarkdownServiceError(
            message,
            service_name=service_name,
            status_code=exc.code,
        )
    except URLError as exc:
        reason = getattr(exc, "reason", exc)
        raise MarkdownServiceError(
            "Network error contacting {0}: {1}".format(service_name, reason),
            service_name=service_name,
        )
    except socket.timeout:
        raise MarkdownServiceError(
            "Request to {0} timed out after {1}s".format(service_name, timeout),
            service_name=service_name,
        )


def _is_service_unavailable(error):
    if error.status_code is None:
        return True
    if error.status_code in (408, 425, 429):
        return True
    return error.status_code >= 500


def _fetch_via_markdown_new(url, method, retain_images, timeout, transport):
    if transport == "get":
        request, service_url = _build_markdown_new_get_request(url, method, retain_images)
        return _execute_request(
            request,
            "get",
            timeout,
            service_url,
            service_name="markdown.new",
            provider="markdown.new",
        )

    if transport == "post":
        request, service_url = _build_markdown_new_post_request(url, method, retain_images)
        return _execute_request(
            request,
            "post",
            timeout,
            service_url,
            service_name="markdown.new",
            provider="markdown.new",
        )

    request, service_url = _build_markdown_new_get_request(url, method, retain_images)
    try:
        return _execute_request(
            request,
            "get",
            timeout,
            service_url,
            service_name="markdown.new",
            provider="markdown.new",
        )
    except MarkdownServiceError as exc:
        if exc.status_code == 429:
            raise
        request, service_url = _build_markdown_new_post_request(url, method, retain_images)
        return _execute_request(
            request,
            "post",
            timeout,
            service_url,
            service_name="markdown.new",
            provider="markdown.new",
        )


def fetch_markdown(
    url,
    method="auto",
    retain_images=False,
    timeout=DEFAULT_TIMEOUT,
    transport="auto",
    force_markdown_new=False,
):
    if not url:
        raise ValueError("url is required")
    if method not in ("auto", "ai", "browser"):
        raise ValueError("method must be one of: auto, ai, browser")
    if transport not in ("auto", "get", "post"):
        raise ValueError("transport must be one of: auto, get, post")

    if force_markdown_new:
        return _fetch_via_markdown_new(url, method, retain_images, timeout, transport)

    request, service_url = _build_jina_request(url)
    try:
        return _execute_request(
            request,
            "get",
            timeout,
            service_url,
            service_name="r.jina.ai",
            provider="r.jina.ai",
        )
    except MarkdownServiceError as exc:
        if not _is_service_unavailable(exc):
            raise
        try:
            return _fetch_via_markdown_new(url, method, retain_images, timeout, transport)
        except MarkdownServiceError as fallback_exc:
            raise MarkdownServiceError(
                "{0}; fallback via markdown.new also failed: {1}".format(exc, fallback_exc),
                service_name=fallback_exc.service_name,
                status_code=fallback_exc.status_code,
            )


def _slugify_target(url):
    parsed = urlparse(url)
    host = parsed.netloc or "document"
    path = parsed.path.strip("/")
    if path:
        path = path.replace("/", "-")
        slug = host + "-" + path
    else:
        slug = host
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", slug)
    slug = slug.strip("._-")
    return slug or "document"


def build_output_path(output_value, source_url, now=None):
    if not output_value:
        raise ValueError("output_value is required")

    if now is None:
        now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    default_base = _slugify_target(source_url)

    is_directory = False
    if os.path.isdir(output_value):
        is_directory = True
    elif output_value.endswith(os.sep):
        is_directory = True
    elif os.altsep and output_value.endswith(os.altsep):
        is_directory = True

    if is_directory:
        directory = output_value
        filename = "{0}-{1}.md".format(default_base, timestamp)
        return os.path.join(directory, filename)

    root, ext = os.path.splitext(output_value)
    if not root:
        root = output_value
    if not ext:
        ext = ".md"
    return "{0}-{1}{2}".format(root, timestamp, ext)


def _write_output(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    handle = open(path, "w", encoding="utf-8")
    try:
        handle.write(content)
    finally:
        handle.close()


def _print_headers(headers):
    preferred = [
        "content-type",
        "x-markdown-tokens",
        "x-rate-limit-remaining",
        "x-rate-limit-reset",
    ]
    seen = set()
    for key in preferred:
        if key in headers:
            print("{0}: {1}".format(key, headers[key]), file=sys.stderr)
            seen.add(key)
    for key in sorted(headers):
        if key.startswith("x-") and key not in seen:
            print("{0}: {1}".format(key, headers[key]), file=sys.stderr)


def _convert_single_url(args_tuple):
    """Convert a single URL. Used by batch processing."""
    url, method, retain_images, timeout, transport, force_markdown_new, output = args_tuple
    try:
        result = fetch_markdown(
            url=url,
            method=method,
            retain_images=retain_images,
            timeout=timeout,
            transport=transport,
            force_markdown_new=force_markdown_new,
        )
        output_path = None
        if output:
            output_path = build_output_path(output, url)
            _write_output(output_path, result.markdown)
        return {
            "url": url,
            "success": True,
            "markdown": result.markdown,
            "provider": result.provider,
            "output_path": output_path,
            "error": None,
        }
    except (MarkdownServiceError, ValueError) as exc:
        return {
            "url": url,
            "success": False,
            "markdown": None,
            "provider": None,
            "output_path": None,
            "error": str(exc),
        }


def parse_args(argv=None):
    description = (
        "Convert a public URL to Markdown and optionally save it to a file.\n\n"
        "Provider strategy:\n"
        "  1) Try r.jina.ai first\n"
        "  2) Fallback to markdown.new only when r.jina.ai is unavailable\n"
        "  3) Use --force-markdown-new to skip r.jina.ai"
    )
    epilog = (
        "Examples:\n"
        "  python scripts/url_to_md.py \"https://www.stanford.edu/\"\n"
        "  python scripts/url_to_md.py \"https://www.stanford.edu/\" --output \"outputs/stanford.md\"\n"
        "  python scripts/url_to_md.py \"https://example.com\" --timeout 45 --show-headers\n"
        "  python scripts/url_to_md.py \"https://example.com\" --method browser --transport post\n"
        "  python scripts/url_to_md.py \"https://example.com\" --force-markdown-new\n"
        "\n"
        "Batch conversion examples:\n"
        "  python scripts/url_to_md.py --urls \"https://example.com\" \"https://example.org\" --output-dir \"output/\"\n"
        "  python scripts/url_to_md.py --urls \"https://a.com\" \"https://b.com\" \"https://c.com\" --concurrency 5\n"
    )
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("url", nargs="?", help="Public URL to convert")
    parser.add_argument(
        "--urls",
        nargs="+",
        metavar="URL",
        help="Multiple URLs to convert in batch (mutually exclusive with positional url)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="Number of parallel conversions for batch mode (default: 3)",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for batch conversion (creates slug-based filenames)",
    )
    parser.add_argument(
        "--method",
        choices=["auto", "ai", "browser"],
        default="auto",
        help="Conversion method for markdown.new fallback (default: auto)",
    )
    parser.add_argument(
        "--retain-images",
        action="store_true",
        help="Request Markdown that keeps image references (markdown.new fallback only)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--transport",
        choices=["auto", "get", "post"],
        default="auto",
        help="Transport used by markdown.new fallback (default: auto)",
    )
    parser.add_argument(
        "--output",
        help="Write to a timestamped file. The timestamp is always appended before the extension.",
    )
    parser.add_argument(
        "--show-headers",
        action="store_true",
        help="Print selected response headers to stderr",
    )
    parser.add_argument(
        "--force-markdown-new",
        action="store_true",
        help="Skip r.jina.ai and force markdown.new directly",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # Determine URLs to process
    if args.urls:
        urls = args.urls
    elif args.url:
        urls = [args.url]
    else:
        print("error: either provide a positional url or use --urls", file=sys.stderr)
        return 1

    # Validate mutual exclusivity of output options
    if args.output and args.output_dir:
        print("error: cannot use both --output and --output-dir", file=sys.stderr)
        return 1

    # Batch mode
    if len(urls) > 1 or args.urls or args.output_dir:
        output_dir = args.output_dir or args.output
        if not output_dir:
            output_dir = "output"

        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Prepare arguments for each URL
        task_args = [
            (
                url,
                args.method,
                args.retain_images,
                args.timeout,
                args.transport,
                args.force_markdown_new,
                output_dir,
            )
            for url in urls
        ]

        # Process URLs in parallel
        results = []
        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            futures = {executor.submit(_convert_single_url, arg): arg[0] for arg in task_args}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        # Print results
        success_count = 0
        fail_count = 0
        for result in sorted(results, key=lambda x: x["url"]):
            if result["success"]:
                success_count += 1
                print(
                    "SUCCESS: {url} -> {provider} -> {output}".format(
                        url=result["url"],
                        provider=result["provider"],
                        output=result["output_path"] or "(stdout)",
                    ),
                    file=sys.stderr,
                )
            else:
                fail_count += 1
                print("FAILED: {url} -> {error}".format(url=result["url"], error=result["error"]), file=sys.stderr)

        print("\nBatch complete: {success} succeeded, {failed} failed".format(
            success=success_count, failed=fail_count), file=sys.stderr)

        # Write combined markdown to stdout if no output directory
        if not args.output_dir and not args.output:
            for result in sorted(results, key=lambda x: x["url"]):
                if result["success"] and result["markdown"]:
                    sys.stdout.write("\n<!-- {url} -->\n\n".format(url=result["url"]))
                    sys.stdout.write(result["markdown"])
                    if not result["markdown"].endswith("\n"):
                        sys.stdout.write("\n")

        return 0 if fail_count == 0 else 1

    # Single URL mode (backward compatible)
    try:
        result = fetch_markdown(
            url=args.url,
            method=args.method,
            retain_images=args.retain_images,
            timeout=args.timeout,
            transport=args.transport,
            force_markdown_new=args.force_markdown_new,
        )
    except (MarkdownServiceError, ValueError) as exc:
        print("error: {0}".format(exc), file=sys.stderr)
        return 1

    if args.show_headers:
        _print_headers(result.headers)

    if args.output:
        output_path = build_output_path(args.output, args.url)
        _write_output(output_path, result.markdown)
        print(output_path, file=sys.stderr)
        return 0

    if result.markdown:
        sys.stdout.write(result.markdown)
        if not result.markdown.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
