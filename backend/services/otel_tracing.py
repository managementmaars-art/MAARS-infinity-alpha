"""OpenTelemetry tracing — distributed spans for the gateway.

Emits spans that any OTel collector can ingest (Jaeger, Tempo, Honeycomb,
Datadog APM). Each gateway call becomes a trace with nested spans:

  maars.gateway.complete
    ├── injection.scan
    ├── pii.scrub
    ├── semantic_cache.lookup
    ├── wallet.reserve
    ├── provider.call
    │    └── http.post
    └── wallet.settle

If `opentelemetry` isn't installed or `OTEL_EXPORTER_OTLP_ENDPOINT` isn't
set, every tracer call becomes a no-op. No behavior change, no dependency
penalty if you don't opt in.

Set env:
  OTEL_EXPORTER_OTLP_ENDPOINT = https://collector.example.com:4318
  OTEL_SERVICE_NAME            = maars-gateway (default)
"""
from __future__ import annotations
import contextlib
import logging
import os
from typing import Any, Iterator

logger = logging.getLogger(__name__)

_tracer = None
_initialized = False


def init() -> bool:
    """Wire OpenTelemetry SDK. Safe to call repeatedly — only takes effect once."""
    global _tracer, _initialized
    if _initialized:
        return _tracer is not None
    _initialized = True

    if not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    except ImportError:
        logger.info("opentelemetry not installed; tracing disabled")
        return False

    resource = Resource.create({
        "service.name": os.environ.get("OTEL_SERVICE_NAME", "maars-gateway"),
        "service.version": os.environ.get("MAARS_VERSION", "dev"),
    })
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer("maars.gateway")
    logger.info("OpenTelemetry tracing initialized → %s", os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"))
    return True


@contextlib.contextmanager
def span(name: str, **attributes: Any) -> Iterator[Any]:
    """Context manager that yields an active span (or a no-op if OTel
    isn't configured). Usage:
        with otel.span("provider.call", provider="openai") as s:
            ...
            s.set_attribute("latency_ms", 420)
    """
    if _tracer is None:
        yield _NoopSpan()
        return
    with _tracer.start_as_current_span(name) as s:
        for k, v in (attributes or {}).items():
            try:
                s.set_attribute(k, v)
            except Exception:
                pass
        yield s


class _NoopSpan:
    def set_attribute(self, *_a, **_kw): pass
    def add_event(self, *_a, **_kw): pass
    def record_exception(self, *_a, **_kw): pass
    def set_status(self, *_a, **_kw): pass
