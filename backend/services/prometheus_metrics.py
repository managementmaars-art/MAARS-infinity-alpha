"""First-class Prometheus metrics — what NVIDIA's blueprint ships with.

Exposes a /metrics endpoint in the Prometheus text format. The graph
we care about: per-provider request count, error rate, latency, and
credits-charged per source. Grafana can scrape us directly; so can the
built-in admin dashboard (parses the same text).

We avoid pulling in prometheus_client to keep deps light — the text
format is ~30 lines of code. Counters live in-process; on multi-worker
deploys each worker exposes its own /metrics and a sidecar aggregates.

Exposed metrics:
  maars_gateway_requests_total{provider,model,source,status}
  maars_gateway_latency_ms_bucket{provider,model,le}    (histogram)
  maars_gateway_latency_ms_sum / _count
  maars_gateway_credits_total{provider,model,source}
  maars_gateway_errors_total{provider,model,kind}
  maars_gateway_cache_hits_total{kind}                  (exact/semantic/idempotent/prompt)
  maars_gateway_circuit_state{provider}                 (0 closed, 1 half, 2 open)
"""
from __future__ import annotations
import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)

_lock = threading.Lock()

_LATENCY_BUCKETS_MS = (50, 100, 250, 500, 1000, 2000, 5000, 10000, 30000)


class _Hist:
    __slots__ = ("buckets", "sum", "count")

    def __init__(self) -> None:
        self.buckets = [0] * len(_LATENCY_BUCKETS_MS)
        self.sum = 0.0
        self.count = 0

    def observe(self, value: float) -> None:
        self.sum += value
        self.count += 1
        for i, b in enumerate(_LATENCY_BUCKETS_MS):
            if value <= b:
                self.buckets[i] += 1


_counters: dict[str, dict[tuple, float]] = {
    "requests_total":  {},
    "credits_total":   {},
    "errors_total":    {},
    "cache_hits_total": {},
}
_histograms: dict[tuple, _Hist] = {}
_gauges: dict[tuple, float] = {}


def inc_requests(provider: str, model: str, source: str, status: str, *, n: int = 1) -> None:
    k = (provider, model, source, status)
    with _lock:
        _counters["requests_total"][k] = _counters["requests_total"].get(k, 0) + n


def inc_credits(provider: str, model: str, source: str, credits: int) -> None:
    k = (provider, model, source)
    with _lock:
        _counters["credits_total"][k] = _counters["credits_total"].get(k, 0) + credits


def inc_errors(provider: str, model: str, kind: str) -> None:
    k = (provider, model, kind)
    with _lock:
        _counters["errors_total"][k] = _counters["errors_total"].get(k, 0) + 1


def inc_cache_hit(kind: str) -> None:
    k = (kind,)
    with _lock:
        _counters["cache_hits_total"][k] = _counters["cache_hits_total"].get(k, 0) + 1


def observe_latency(provider: str, model: str, latency_ms: float) -> None:
    k = (provider, model)
    with _lock:
        hist = _histograms.get(k)
        if hist is None:
            hist = _Hist()
            _histograms[k] = hist
        hist.observe(latency_ms)


def set_circuit_state(provider: str, state: str) -> None:
    v = {"closed": 0, "half_open": 1, "open": 2}.get(state, 0)
    k = (provider,)
    with _lock:
        _gauges[k] = v


def _fmt_labels(labels: dict[str, str]) -> str:
    return "{" + ",".join(f'{k}="{_esc(v)}"' for k, v in labels.items()) + "}"


def _esc(v: str) -> str:
    return str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def render() -> str:
    """Return Prometheus exposition-format text. Safe to call anytime."""
    lines: list[str] = []
    with _lock:
        lines.append("# HELP maars_gateway_requests_total Requests routed through the MAARS gateway")
        lines.append("# TYPE maars_gateway_requests_total counter")
        for (provider, model, source, status), v in _counters["requests_total"].items():
            labels = _fmt_labels({"provider": provider, "model": model, "source": source, "status": status})
            lines.append(f"maars_gateway_requests_total{labels} {v}")

        lines.append("# HELP maars_gateway_credits_total Credits charged per (provider,model,source)")
        lines.append("# TYPE maars_gateway_credits_total counter")
        for (provider, model, source), v in _counters["credits_total"].items():
            labels = _fmt_labels({"provider": provider, "model": model, "source": source})
            lines.append(f"maars_gateway_credits_total{labels} {v}")

        lines.append("# HELP maars_gateway_errors_total Provider or gateway errors")
        lines.append("# TYPE maars_gateway_errors_total counter")
        for (provider, model, kind), v in _counters["errors_total"].items():
            labels = _fmt_labels({"provider": provider, "model": model, "kind": kind})
            lines.append(f"maars_gateway_errors_total{labels} {v}")

        lines.append("# HELP maars_gateway_cache_hits_total Hits by cache layer")
        lines.append("# TYPE maars_gateway_cache_hits_total counter")
        for (kind,), v in _counters["cache_hits_total"].items():
            labels = _fmt_labels({"kind": kind})
            lines.append(f"maars_gateway_cache_hits_total{labels} {v}")

        lines.append("# HELP maars_gateway_latency_ms Provider latency histogram")
        lines.append("# TYPE maars_gateway_latency_ms histogram")
        for (provider, model), hist in _histograms.items():
            cumulative = 0
            for i, b in enumerate(_LATENCY_BUCKETS_MS):
                cumulative += hist.buckets[i]
                labels = _fmt_labels({"provider": provider, "model": model, "le": str(b)})
                lines.append(f"maars_gateway_latency_ms_bucket{labels} {cumulative}")
            labels_inf = _fmt_labels({"provider": provider, "model": model, "le": "+Inf"})
            lines.append(f"maars_gateway_latency_ms_bucket{labels_inf} {hist.count}")
            labels_sum = _fmt_labels({"provider": provider, "model": model})
            lines.append(f"maars_gateway_latency_ms_sum{labels_sum} {hist.sum}")
            lines.append(f"maars_gateway_latency_ms_count{labels_sum} {hist.count}")

        lines.append("# HELP maars_gateway_circuit_state Circuit breaker state (0=closed,1=half,2=open)")
        lines.append("# TYPE maars_gateway_circuit_state gauge")
        for (provider,), v in _gauges.items():
            labels = _fmt_labels({"provider": provider})
            lines.append(f"maars_gateway_circuit_state{labels} {v}")

    lines.append("")
    return "\n".join(lines)
