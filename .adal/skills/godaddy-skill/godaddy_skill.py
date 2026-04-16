#!/usr/bin/env python3
"""GoDaddy DNS Management Skill - Manage domains and DNS records via GoDaddy API."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SKILL_DIR, "config.json")
API_BASE = "https://api.godaddy.com/v1"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(json.dumps({
            "error": "config.json not found",
            "setup": f"Create {CONFIG_FILE} with: {{\"api_key\": \"YOUR_KEY\", \"api_secret\": \"YOUR_SECRET\"}}"
        }, indent=2))
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    if not config.get("api_key") or not config.get("api_secret"):
        print(json.dumps({
            "error": "api_key and api_secret required in config.json"
        }, indent=2))
        sys.exit(1)
    return config


def api_request(method, path, config, body=None):
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": f"sso-key {config['api_key']}:{config['api_secret']}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            if raw:
                return json.loads(raw)
            return {"status": "ok"}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_data = json.loads(error_body)
        except json.JSONDecodeError:
            error_data = {"raw": error_body}
        print(json.dumps({
            "error": f"HTTP {e.code}",
            "detail": error_data
        }, indent=2))
        sys.exit(1)


def cmd_list_domains(args, config):
    result = api_request("GET", "/domains", config)
    domains = []
    for d in result:
        domains.append({
            "domain": d.get("domain"),
            "status": d.get("status"),
            "expires": d.get("expires"),
            "renewable": d.get("renewable"),
            "locked": d.get("locked")
        })
    print(json.dumps({"domains": domains, "count": len(domains)}, indent=2))


def cmd_domain_info(args, config):
    result = api_request("GET", f"/domains/{args.domain}", config)
    print(json.dumps(result, indent=2))


def cmd_get_records(args, config):
    path = f"/domains/{args.domain}/records"
    if args.type:
        path += f"/{args.type}"
        if args.name:
            path += f"/{args.name}"
    result = api_request("GET", path, config)
    records = []
    for r in result:
        records.append({
            "type": r.get("type"),
            "name": r.get("name"),
            "data": r.get("data"),
            "ttl": r.get("ttl"),
            "priority": r.get("priority")
        })
    print(json.dumps({"domain": args.domain, "records": records, "count": len(records)}, indent=2))


def cmd_set_record(args, config):
    record = {
        "data": args.data,
        "ttl": args.ttl
    }
    if args.priority is not None:
        record["priority"] = args.priority

    # PUT replaces all records of this type+name
    path = f"/domains/{args.domain}/records/{args.type}/{args.name}"
    api_request("PUT", path, config, body=[record])
    print(json.dumps({
        "status": "ok",
        "action": "set",
        "domain": args.domain,
        "type": args.type,
        "name": args.name,
        "data": args.data,
        "ttl": args.ttl
    }, indent=2))


def cmd_add_record(args, config):
    record = {
        "type": args.type,
        "name": args.name,
        "data": args.data,
        "ttl": args.ttl
    }
    if args.priority is not None:
        record["priority"] = args.priority

    # PATCH appends records
    path = f"/domains/{args.domain}/records"
    api_request("PATCH", path, config, body=[record])
    print(json.dumps({
        "status": "ok",
        "action": "added",
        "domain": args.domain,
        "type": args.type,
        "name": args.name,
        "data": args.data,
        "ttl": args.ttl
    }, indent=2))


def cmd_delete_record(args, config):
    # GoDaddy doesn't have a direct delete endpoint for a single record.
    # Strategy: GET all records of type+name, remove the target, PUT back the rest.
    path = f"/domains/{args.domain}/records/{args.type}/{args.name}"
    records = api_request("GET", path, config)

    if args.data:
        remaining = [r for r in records if r.get("data") != args.data]
    else:
        remaining = []

    removed = len(records) - len(remaining)
    if removed == 0:
        print(json.dumps({"status": "no_match", "message": "No matching records found to delete"}, indent=2))
        return

    if remaining:
        api_request("PUT", path, config, body=remaining)
    else:
        # Can't PUT empty array for most types — use a dummy and then replace
        # Actually GoDaddy allows PUT with empty array to clear records of that type+name
        api_request("PUT", path, config, body=[])

    print(json.dumps({
        "status": "ok",
        "action": "deleted",
        "domain": args.domain,
        "type": args.type,
        "name": args.name,
        "removed": removed,
        "remaining": len(remaining)
    }, indent=2))


def cmd_bulk_set(args, config):
    """Set multiple DNS records from a JSON file or inline JSON."""
    if os.path.exists(args.records):
        with open(args.records) as f:
            records = json.load(f)
    else:
        records = json.loads(args.records)

    results = []
    for rec in records:
        rtype = rec["type"]
        name = rec["name"]
        data = rec["data"]
        ttl = rec.get("ttl", 600)
        priority = rec.get("priority")

        record_body = {"data": data, "ttl": ttl}
        if priority is not None:
            record_body["priority"] = priority

        path = f"/domains/{args.domain}/records/{rtype}/{name}"
        try:
            api_request("PUT", path, config, body=[record_body])
            results.append({"type": rtype, "name": name, "data": data, "status": "ok"})
        except SystemExit:
            results.append({"type": rtype, "name": name, "data": data, "status": "error"})

    print(json.dumps({
        "domain": args.domain,
        "results": results,
        "total": len(results),
        "success": sum(1 for r in results if r["status"] == "ok")
    }, indent=2))


def cmd_check_dns(args, config):
    """Check current DNS propagation for a domain using system dig."""
    import subprocess
    domain = args.domain
    checks = {}

    for rtype in ["A", "AAAA", "CNAME", "MX", "TXT", "NS"]:
        try:
            result = subprocess.run(
                ["dig", "+short", domain, rtype],
                capture_output=True, text=True, timeout=10
            )
            values = [v.strip() for v in result.stdout.strip().split("\n") if v.strip()]
            if values:
                checks[rtype] = values
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Also check www
    try:
        result = subprocess.run(
            ["dig", "+short", f"www.{domain}", "CNAME"],
            capture_output=True, text=True, timeout=10
        )
        www = [v.strip() for v in result.stdout.strip().split("\n") if v.strip()]
        if www:
            checks["www_CNAME"] = www
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    print(json.dumps({"domain": domain, "resolved": checks}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="GoDaddy DNS Management")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # list-domains
    sub.add_parser("list-domains", help="List all domains in account")

    # domain-info
    p = sub.add_parser("domain-info", help="Get domain details")
    p.add_argument("domain", help="Domain name (e.g., zergdesk.com)")

    # get-records
    p = sub.add_parser("get-records", help="Get DNS records for a domain")
    p.add_argument("domain", help="Domain name")
    p.add_argument("--type", "-t", help="Filter by record type (A, AAAA, CNAME, MX, TXT, NS)")
    p.add_argument("--name", "-n", help="Filter by record name (requires --type)")

    # set-record (replaces existing records of same type+name)
    p = sub.add_parser("set-record", help="Set a DNS record (replaces existing of same type+name)")
    p.add_argument("domain", help="Domain name")
    p.add_argument("type", help="Record type (A, AAAA, CNAME, MX, TXT, NS)")
    p.add_argument("name", help="Record name (@ for root, www, etc.)")
    p.add_argument("data", help="Record data (IP, hostname, etc.)")
    p.add_argument("--ttl", type=int, default=600, help="TTL in seconds (default: 600)")
    p.add_argument("--priority", type=int, help="Priority (for MX records)")

    # add-record (appends without replacing)
    p = sub.add_parser("add-record", help="Add a DNS record (appends, doesn't replace)")
    p.add_argument("domain", help="Domain name")
    p.add_argument("type", help="Record type")
    p.add_argument("name", help="Record name")
    p.add_argument("data", help="Record data")
    p.add_argument("--ttl", type=int, default=600, help="TTL in seconds (default: 600)")
    p.add_argument("--priority", type=int, help="Priority (for MX records)")

    # delete-record
    p = sub.add_parser("delete-record", help="Delete DNS record(s)")
    p.add_argument("domain", help="Domain name")
    p.add_argument("type", help="Record type")
    p.add_argument("name", help="Record name")
    p.add_argument("--data", help="Specific data value to delete (deletes all of type+name if omitted)")

    # bulk-set
    p = sub.add_parser("bulk-set", help="Set multiple DNS records from JSON")
    p.add_argument("domain", help="Domain name")
    p.add_argument("records", help="JSON array of records or path to JSON file")

    # check-dns
    p = sub.add_parser("check-dns", help="Check DNS propagation for a domain")
    p.add_argument("domain", help="Domain name")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = load_config()

    commands = {
        "list-domains": cmd_list_domains,
        "domain-info": cmd_domain_info,
        "get-records": cmd_get_records,
        "set-record": cmd_set_record,
        "add-record": cmd_add_record,
        "delete-record": cmd_delete_record,
        "bulk-set": cmd_bulk_set,
        "check-dns": cmd_check_dns,
    }

    commands[args.command](args, config)


if __name__ == "__main__":
    main()
