#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const allowedNodeTypes = new Set(['view', 'text', 'image']);
const allowedStyleKeys = new Set([
  'display', 'position', 'flexDirection', 'justifyContent', 'alignItems', 'alignSelf',
  'flexWrap', 'flexGrow', 'flexShrink', 'flexBasis', 'gap',
  'width', 'height', 'minWidth', 'minHeight', 'maxWidth', 'maxHeight',
  'padding', 'margin', 'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
  'marginTop', 'marginRight', 'marginBottom', 'marginLeft',
  'left', 'right', 'top', 'bottom', 'zIndex',
  'backgroundColor', 'opacity', 'borderRadius',
  'fontSize', 'fontWeight', 'color', 'lineHeight', 'textAlign', 'whiteSpace', 'overflow',
  'objectFit'
]);

function fail(message) {
  console.error(`[validate-webui-schema] ${message}`);
  process.exitCode = 1;
}

function loadJson(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(raw);
}

function validateStyle(style, pathLabel) {
  if (!style || typeof style !== 'object' || Array.isArray(style)) {
    fail(`${pathLabel}.style must be an object when provided`);
    return;
  }

  for (const key of Object.keys(style)) {
    if (!allowedStyleKeys.has(key)) {
      fail(`${pathLabel}.style has unsupported key: ${key}`);
    }
  }
}

function validateNode(node, pathLabel, idSet) {
  if (!node || typeof node !== 'object' || Array.isArray(node)) {
    fail(`${pathLabel} must be an object`);
    return;
  }

  if (!allowedNodeTypes.has(node.type)) {
    fail(`${pathLabel}.type is invalid: ${node.type}`);
  }

  if (node.id != null) {
    if (typeof node.id !== 'string' || !node.id.trim()) {
      fail(`${pathLabel}.id must be a non-empty string`);
    } else if (idSet.has(node.id)) {
      fail(`${pathLabel}.id is duplicated: ${node.id}`);
    } else {
      idSet.add(node.id);
    }
  }

  if (node.style != null) {
    validateStyle(node.style, pathLabel);
  }

  if (node.type === 'text') {
    if (!node.props || typeof node.props.text !== 'string') {
      fail(`${pathLabel} is text but props.text is missing or not a string`);
    }
  }

  if (node.type === 'image') {
    if (!node.props || typeof node.props.src !== 'string') {
      fail(`${pathLabel} is image but props.src is missing or not a string`);
    }
  }

  if (node.children != null) {
    if (!Array.isArray(node.children)) {
      fail(`${pathLabel}.children must be an array when provided`);
      return;
    }

    for (let i = 0; i < node.children.length; i++) {
      validateNode(node.children[i], `${pathLabel}.children[${i}]`, idSet);
    }
  }
}

function validateMeta(meta, idSet) {
  if (!meta) {
    return;
  }

  const arrayKeys = ['interactiveIds', 'dynamicTextIds', 'dynamicImageIds', 'containerIds'];
  for (const key of arrayKeys) {
    if (meta[key] == null) {
      continue;
    }

    if (!Array.isArray(meta[key])) {
      fail(`meta.${key} must be an array when provided`);
      continue;
    }

    for (const id of meta[key]) {
      if (typeof id !== 'string' || !id.trim()) {
        fail(`meta.${key} contains an invalid id value`);
        continue;
      }
      if (!idSet.has(id)) {
        fail(`meta.${key} references missing schema id: ${id}`);
      }
    }
  }
}

function main() {
  const schemaPath = process.argv[2];
  const metaPath = process.argv[3];

  if (!schemaPath) {
    console.error('Usage: node validate-webui-schema.js <schema.json> [meta.json]');
    process.exit(1);
  }

  const schema = loadJson(path.resolve(schemaPath));
  const idSet = new Set();
  validateNode(schema, 'schema', idSet);

  if (metaPath) {
    const meta = loadJson(path.resolve(metaPath));
    validateMeta(meta, idSet);
  }

  if (process.exitCode && process.exitCode !== 0) {
    process.exit(process.exitCode);
  }

  console.log('[validate-webui-schema] OK');
}

main();
