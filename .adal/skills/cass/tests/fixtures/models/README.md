# Model Test Fixtures

These files are used by tests that check model installation state.
`model.onnx` is a minimal valid ONNX identity model (see source below).

## Files

- `model.onnx` - Minimal valid ONNX identity model fixture
- `model.onnx.placeholder` - Legacy placeholder (retained for backwards compatibility)
- `tokenizer.json` - Minimal valid tokenizer config
- `config.json` - Minimal valid model config
- `special_tokens_map.json` - Standard BERT special tokens
- `tokenizer_config.json` - Tokenizer configuration

## Real Semantic Fixture Bundles

### xenova-paraphrase-minilm-l3-v2-int8/

Single-file ONNX embedding model bundle (quantized int8) for semantic tests.

- `model.onnx` - From `Xenova/paraphrase-MiniLM-L3-v2` (`onnx/model_int8.onnx`)
- `tokenizer.json`
- `config.json`
- `special_tokens_map.json`
- `tokenizer_config.json`
- `checksums.sha256` - SHA256s for all files above

Approximate size: `model.onnx` ~17 MB (int8 quantized).

### xenova-ms-marco-minilm-l6-v2-int8/

Single-file ONNX cross-encoder reranker bundle (quantized int8).

- `model.onnx` - From `Xenova/ms-marco-MiniLM-L-6-v2` (`onnx/model_int8.onnx`)
- `tokenizer.json`
- `config.json`
- `special_tokens_map.json`
- `tokenizer_config.json`
- `checksums.sha256` - SHA256s for all files above

Approximate size: `model.onnx` ~22 MB (int8 quantized).

## Usage

Tests should copy these fixtures to temp directories rather than
creating synthetic "fake" content dynamically.

For semantic tests, prefer `tests/fixture_helpers::embedder_fixture_dir()`
and `tests/fixture_helpers::reranker_fixture_dir()`, then call
`verify_model_fixture_checksums()` before loading the bundles.

## Source

- `model.onnx` is sourced from ONNX test data:
  `onnx/backend/test/data/node/test_identity/model.onnx` (Apache-2.0)
- `xenova-paraphrase-minilm-l3-v2-int8/` is sourced from:
  `https://huggingface.co/Xenova/paraphrase-MiniLM-L3-v2` (Apache-2.0)
  with the upstream model derived from
  `https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L3-v2`.
- `xenova-ms-marco-minilm-l6-v2-int8/` is sourced from:
  `https://huggingface.co/Xenova/ms-marco-MiniLM-L-6-v2` (Apache-2.0)
  with the upstream model derived from
  `https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2`.

## No-Mock Policy

Per the project's no-mock policy (see TESTING.md), tests should use
real fixtures with documented provenance rather than synthetic data.
