---
name: figma-design
description: Figma REST API, design token extraction, component code generation, Code Connect, Dev Mode, and plugin development.
---

# Figma Design

## Overview

Figma provides REST and WebSocket APIs for accessing design files, extracting tokens, generating code, and building plugins. The Dev Mode API enables direct design-to-code workflows.

## Authentication & Client Setup

```typescript
import axios from "axios";

const figmaClient = axios.create({
  baseURL: "https://api.figma.com/v1",
  headers: {
    "X-Figma-Token": process.env.FIGMA_ACCESS_TOKEN,
    // Or use OAuth: "Authorization": `Bearer ${accessToken}`
  },
});

// File ID is from the URL: figma.com/file/FILE_ID/...
const FILE_ID = "abc123xyz";
```

## Fetch File & Node Data

```typescript
// Get entire file structure
const getFile = async (fileId: string) => {
  const { data } = await figmaClient.get(`/files/${fileId}`, {
    params: {
      depth: 2,           // Limit traversal depth for large files
      geometry: "paths",  // Include vector path data
    },
  });
  return data;
};

// Get specific nodes
const getNodes = async (fileId: string, nodeIds: string[]) => {
  const { data } = await figmaClient.get(`/files/${fileId}/nodes`, {
    params: { ids: nodeIds.join(",") },
  });
  return data.nodes;
};

// Get component metadata
const getComponents = async (fileId: string) => {
  const { data } = await figmaClient.get(`/files/${fileId}/components`);
  return data.meta.components;
};

// Get component sets (variants)
const getComponentSets = async (fileId: string) => {
  const { data } = await figmaClient.get(`/files/${fileId}/component_sets`);
  return data.meta.component_sets;
};

// Get styles (colors, text, effects)
const getStyles = async (fileId: string) => {
  const { data } = await figmaClient.get(`/files/${fileId}/styles`);
  return data.meta.styles;
};
```

## Design Token Extraction

```typescript
interface DesignToken {
  value: string | number;
  type: string;
  description?: string;
}

function extractColorTokens(styles: any[], nodes: any): Record<string, DesignToken> {
  const tokens: Record<string, DesignToken> = {};

  for (const style of styles.filter((s) => s.style_type === "FILL")) {
    const node = nodes[style.node_id];
    if (!node?.fills?.[0]) continue;

    const fill = node.fills[0];
    if (fill.type !== "SOLID") continue;

    const { r, g, b, a = 1 } = fill.color;
    const hex = rgbaToHex(r, g, b, a);

    // Convert Figma style name to token name: "Brand/Primary/500" -> "brand-primary-500"
    const tokenName = style.name.toLowerCase().replace(/\//g, "-").replace(/\s+/g, "-");
    tokens[tokenName] = {
      value: hex,
      type: "color",
      description: style.description,
    };
  }

  return tokens;
}

function extractTypographyTokens(styles: any[], nodes: any): Record<string, DesignToken> {
  const tokens: Record<string, DesignToken> = {};

  for (const style of styles.filter((s) => s.style_type === "TEXT")) {
    const node = nodes[style.node_id];
    if (!node?.style) continue;

    const { fontFamily, fontWeight, fontSize, lineHeightPx, letterSpacing } = node.style;
    const tokenName = style.name.toLowerCase().replace(/\//g, "-").replace(/\s+/g, "-");

    tokens[tokenName] = {
      value: {
        fontFamily,
        fontWeight,
        fontSize: `${fontSize}px`,
        lineHeight: `${lineHeightPx}px`,
        letterSpacing: `${letterSpacing}px`,
      } as any,
      type: "typography",
    };
  }

  return tokens;
}

function rgbaToHex(r: number, g: number, b: number, a: number): string {
  const toHex = (n: number) => Math.round(n * 255).toString(16).padStart(2, "0");
  return a === 1
    ? `#${toHex(r)}${toHex(g)}${toHex(b)}`
    : `#${toHex(r)}${toHex(g)}${toHex(b)}${toHex(a)}`;
}

// Export tokens as CSS custom properties
function tokensToCSS(tokens: Record<string, DesignToken>): string {
  const vars = Object.entries(tokens)
    .map(([name, token]) => {
      const value = typeof token.value === "object"
        ? JSON.stringify(token.value)
        : token.value;
      return `  --${name}: ${value};`;
    })
    .join("\n");

  return `:root {\n${vars}\n}`;
}
```

## Export Images & Assets

```typescript
// Export nodes as images
const exportImages = async (
  fileId: string,
  nodeIds: string[],
  format: "png" | "jpg" | "svg" | "pdf" = "svg",
  scale = 2
) => {
  const { data } = await figmaClient.get(`/images/${fileId}`, {
    params: {
      ids: nodeIds.join(","),
      format,
      scale,
    },
  });

  // data.images maps node_id -> CDN URL
  return data.images;
};

// Download and save all icons
async function downloadIcons(fileId: string, iconFrameId: string) {
  const nodes = await getNodes(fileId, [iconFrameId]);
  const frame = Object.values(nodes)[0].document;

  const iconIds = frame.children.map((child: any) => child.id);
  const imageUrls = await exportImages(fileId, iconIds, "svg");

  for (const [nodeId, url] of Object.entries(imageUrls)) {
    const node = frame.children.find((c: any) => c.id === nodeId);
    const svgContent = await fetch(url as string).then((r) => r.text());
    await fs.writeFile(`./icons/${node.name}.svg`, svgContent);
  }
}
```

## Figma Code Connect

```typescript
// figma.config.ts - Code Connect links components to Figma
import { defineConfig } from "@figma/code-connect";

export default defineConfig({
  parser: "react",
  include: ["src/components/**/*.figma.tsx"],
});
```

```tsx
// src/components/Button/Button.figma.tsx
import figma from "@figma/code-connect";
import { Button } from "./Button";

figma.connect(
  Button,
  "https://www.figma.com/file/FILE_ID?node-id=1234",
  {
    props: {
      // Map Figma variant properties to React props
      variant: figma.enum("Variant", {
        Primary: "primary",
        Secondary: "secondary",
        Destructive: "destructive",
      }),
      size: figma.enum("Size", {
        Small: "sm",
        Medium: "md",
        Large: "lg",
      }),
      disabled: figma.boolean("Disabled"),
      label: figma.string("Label"),
      icon: figma.boolean("Has Icon", {
        true: figma.instance("Icon"),
        false: undefined,
      }),
    },
    example: ({ variant, size, disabled, label, icon }) => (
      <Button variant={variant} size={size} disabled={disabled} icon={icon}>
        {label}
      </Button>
    ),
  }
);
```

```bash
# Publish code connect links
npx figma connect publish --token $FIGMA_ACCESS_TOKEN
```

## Figma Plugin Development

```typescript
// plugin/code.ts - Plugin main thread
figma.showUI(__html__, { width: 400, height: 600 });

figma.ui.onmessage = async (msg) => {
  if (msg.type === "export-tokens") {
    const styles = await figma.getLocalPaintStyles();
    const tokens = styles.map((style) => ({
      name: style.name,
      paints: style.paints,
    }));
    figma.ui.postMessage({ type: "tokens-data", tokens });
  }

  if (msg.type === "apply-style") {
    const nodes = figma.currentPage.selection;
    const style = figma.getStyleById(msg.styleId);
    for (const node of nodes) {
      if ("fillStyleId" in node && style) {
        node.fillStyleId = style.id;
      }
    }
  }

  if (msg.type === "create-component") {
    const frame = figma.createFrame();
    frame.name = msg.name;
    frame.resize(msg.width, msg.height);
    frame.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];

    const text = figma.createText();
    await figma.loadFontAsync({ family: "Inter", style: "Regular" });
    text.characters = msg.label;
    frame.appendChild(text);

    figma.currentPage.appendChild(frame);
    figma.viewport.scrollAndZoomIntoView([frame]);
  }
};
```

## Webhooks

```typescript
// Register a webhook for file changes
const registerWebhook = async () => {
  const { data } = await figmaClient.post("/webhooks/v2", {
    event_type: "FILE_UPDATE",
    team_id: process.env.FIGMA_TEAM_ID,
    endpoint: "https://your-app.com/webhooks/figma",
    passcode: process.env.FIGMA_WEBHOOK_SECRET,
    description: "Design system sync",
  });
  return data;
};

// Webhook handler
export async function POST(request: Request) {
  const body = await request.json();
  const passcode = request.headers.get("X-Figma-Passcode");

  if (passcode !== process.env.FIGMA_WEBHOOK_SECRET) {
    return new Response("Unauthorized", { status: 401 });
  }

  const { event_type, file_key, timestamp } = body;

  if (event_type === "FILE_UPDATE") {
    // Trigger design token re-extraction
    await triggerTokenSync(file_key);
  }

  return new Response("OK");
}
```

## Key Patterns

- **Use `depth` parameter** to limit file traversal — full files can be 10MB+
- **Cache style/component data** — Figma API has rate limits (1 req/min per file per token for large files)
- **Code Connect** closes the gap between design and implementation in Dev Mode
- **Token extraction** should be automated via CI to keep design system in sync
- **Node IDs** are stable across edits — safe to use as permanent references
- **Webhooks** enable real-time design system updates on file change

## Models to Use

- **claude-opus-4-5**: Design system architecture, complex token hierarchies, plugin development
- **claude-sonnet-4-5**: Token extraction scripts, Code Connect setup, API integration
- **claude-haiku-3-5**: Simple node fetching, image exports
