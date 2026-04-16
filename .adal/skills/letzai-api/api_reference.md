# LetzAI API Reference

Complete API documentation for the LetzAI image and video generation platform.

## Base Configuration

| Property | Value |
|----------|-------|
| Base URL | `https://api.letz.ai` |
| Authentication | Bearer Token |
| Content-Type | `application/json` |
| Swagger Docs | [api.letz.ai/doc](https://api.letz.ai/doc) |

## Authentication

All API requests require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

Get your API key at [letz.ai/subscription](https://letz.ai/subscription).

---

## Image Generation

### Create Image

**Endpoint:** `POST /images`

Creates a new AI-generated image based on the provided prompt and settings.

#### Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text description of the desired image. Can include `@modelname` to use trained models. |
| `baseModel` | string | No | AI model to use (see Available Base Models) |
| `mode` | string | No | Resolution/quality mode (model-dependent) |
| `width` | integer | No | Image width in pixels (520-2160) |
| `height` | integer | No | Image height in pixels (520-2160) |
| `negativePrompt` | string | No | Elements to exclude from the image |
| `seed` | integer | No | Seed for reproducible results |
| `aspectRatio` | string | No | Aspect ratio (e.g., "16:9", "1:1", "9:16") |

#### Available Base Models

| Model Name | API Value | Available Modes | Default Mode |
|------------|-----------|-----------------|--------------|
| Nano Banana Pro | `gemini-3-pro-image-preview` | default, 2k, 4k | default |
| Flux2 Max | `flux2-max` | 1k, hd | 1k |
| SeeDream 4.5 | `seedream-4-5-251128` | 2k, 4k | 2k |

#### Example Request

```json
{
  "prompt": "A majestic mountain landscape at sunset with golden light",
  "baseModel": "gemini-3-pro-image-preview",
  "mode": "2k",
  "width": 1920,
  "height": 1080,
  "negativePrompt": "blurry, low quality"
}
```

#### Response

```json
{
  "id": "img_abc123xyz",
  "status": "new",
  "createdAt": "2025-01-27T10:00:00Z"
}
```

### Get Image Status

**Endpoint:** `GET /images/{id}`

Retrieves the status and result of an image generation job.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | The image generation job ID |

#### Response (Pending)

```json
{
  "id": "img_abc123xyz",
  "status": "in progress",
  "progress": 45,
  "createdAt": "2025-01-27T10:00:00Z"
}
```

#### Response (Complete)

```json
{
  "id": "img_abc123xyz",
  "status": "ready",
  "prompt": "A majestic mountain landscape at sunset",
  "baseModel": "gemini-3-pro-image-preview",
  "mode": "2k",
  "width": 1920,
  "height": 1080,
  "imageVersions": {
    "original": "https://cdn.letz.ai/images/img_abc123xyz/original.png",
    "1920x1920": "https://cdn.letz.ai/images/img_abc123xyz/1920x1920.png",
    "640x640": "https://cdn.letz.ai/images/img_abc123xyz/640x640.png"
  },
  "creditsUsed": 160,
  "createdAt": "2025-01-27T10:00:00Z",
  "completedAt": "2025-01-27T10:00:25Z"
}
```

### List Images

**Endpoint:** `GET /images`

Retrieves a list of user's generated images.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 10 | Results per page |

### Interrupt Image Generation

**Endpoint:** `PUT /images/{id}/interruption`

Stops an in-progress image generation job.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | The image generation job ID |

### Change Image Privacy

**Endpoint:** `PUT /images/{id}/privacy`

Changes the privacy setting of a generated image.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | The image ID |

---

## Video Generation

### Create Video

**Endpoint:** `POST /videos`

Creates a new AI-generated video from a source image.

#### Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text description of the desired video motion |
| `imageUrl` | string | Conditional | URL of source image (required if no imageCompletionId) |
| `originalImageCompletionId` | string | Conditional | ID of previously generated image |
| `settings.mode` | string | No | Video model (default, veo31, kling26, wan25) |
| `settings.duration` | integer | No | Video duration in seconds |
| `settings.fps` | integer | No | Frames per second |

#### Available Video Models

| Model Name | API Value | Duration Range | Notes |
|------------|-----------|----------------|-------|
| Default | `default` | 2-6 sec | Most cost-effective |
| VEO 3.1 | `veo31` | 8 sec | Highest quality |
| Kling 2.6 | `kling26` | 5-10 sec | Balanced |
| Wan 2.5 | `wan25` | 5-10 sec | Good motion |

#### Example Request

```json
{
  "prompt": "The camera slowly pans across the mountain as clouds drift by",
  "originalImageCompletionId": "img_abc123xyz",
  "settings": {
    "mode": "kling26",
    "duration": 5
  }
}
```

#### Response

```json
{
  "id": "vid_def456uvw",
  "status": "new",
  "createdAt": "2025-01-27T10:05:00Z"
}
```

### Get Video Status

**Endpoint:** `GET /videos/{id}`

Retrieves the status and result of a video generation job.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | The video generation job ID |

#### Response (Complete)

```json
{
  "id": "vid_def456uvw",
  "status": "ready",
  "prompt": "The camera slowly pans across the mountain",
  "settings": {
    "mode": "kling26",
    "duration": 5
  },
  "videoPaths": {
    "mp4": "https://cdn.letz.ai/videos/vid_def456uvw/video.mp4",
    "webm": "https://cdn.letz.ai/videos/vid_def456uvw/video.webm"
  },
  "thumbnailUrl": "https://cdn.letz.ai/videos/vid_def456uvw/thumbnail.jpg",
  "creditsUsed": 750,
  "createdAt": "2025-01-27T10:05:00Z",
  "completedAt": "2025-01-27T10:06:30Z"
}
```

### List Videos

**Endpoint:** `GET /videos`

Retrieves a list of user's generated videos.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 10 | Results per page |

### Interrupt Video Generation

**Endpoint:** `PUT /videos/{id}/interruption`

Stops an in-progress video generation job.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | The video generation job ID |

### Change Video Privacy

**Endpoint:** `PUT /videos/{id}/privacy`

Changes the privacy setting of a generated video.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | The video ID |

---

## Image Editing (Context Editing)

### Create Image Edit

**Endpoint:** `POST /image-edits`

Edits an existing image using AI-powered modifications. The primary mode is "context" editing.

#### Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mode` | string | Yes | Edit mode: `"context"` (AI editing) or `"skin"` (skin fix) |
| `prompt` | string | Yes | Edit instruction (e.g., "change background to sunset") |
| `imageUrl` | string | Conditional | URL of source image |
| `inputImageUrls` | array | Conditional | Array of source image URLs (max 9) |
| `originalImageCompletionId` | string | Conditional | ID of previously generated LetzAI image |
| `settings` | object | No | Configuration options (see below) |
| `baseModel` | string | No | Alternative to settings.model |
| `organizationId` | string | No | Optional org ID for billing |
| `webhookUrl` | string | No | Optional callback URL |

#### Settings Object

| Parameter | Type | Description |
|-----------|------|-------------|
| `resolution` | string | `"2k"` (HD) or `"4k"` (Ultra HD) |
| `aspect_ratio` | string | `"1:1"`, `"16:9"`, `"9:16"`, `"4:3"`, `"3:4"`, `"21:9"`, `"9:21"` |
| `model` | string | `"gemini-3-pro-image-preview"`, `"flux2-max"`, `"seedream-4-5-251128"` |

#### Edit Modes

| Mode | Description |
|------|-------------|
| `context` | AI-powered contextual editing (primary mode) |
| `skin` | Skin fix/enhancement |

**Note:** Inpainting (mode: "in") and Outpainting (mode: "out") are deprecated - use Context Editing instead.

#### Example Request - Single Image

```json
{
  "mode": "context",
  "prompt": "Change the background to a tropical beach with palm trees",
  "imageUrl": "https://example.com/my-photo.jpg",
  "settings": {
    "resolution": "2k",
    "aspect_ratio": "16:9",
    "model": "gemini-3-pro-image-preview"
  }
}
```

#### Example Request - Multi-Reference Editing

```json
{
  "mode": "context",
  "prompt": "Combine elements from these images into a cohesive scene",
  "inputImageUrls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
  ],
  "settings": {
    "resolution": "4k",
    "model": "gemini-3-pro-image-preview"
  }
}
```

#### Response (Initial)

```json
{
  "id": "edit_ghi789rst",
  "status": "new",
  "createdAt": "2025-01-27T10:10:00Z"
}
```

### Get Image Edit Status

**Endpoint:** `GET /image-edits/{id}`

Retrieves the status and result of an image edit job.

#### Response (Complete)

```json
{
  "id": "edit_ghi789rst",
  "status": "ready",
  "mode": "context",
  "prompt": "Change the background to a tropical beach",
  "originalImageCompletion": {
    "imageVersions": {
      "original": "https://images.letz.ai/..."
    }
  },
  "generatedImageCompletion": {
    "imageVersions": {
      "original": "https://images.letz.ai/edited/original.png",
      "1920x1920": "https://images.letz.ai/edited/1920x1920.png",
      "640x640": "https://images.letz.ai/edited/640x640.png"
    }
  },
  "creditsUsed": 160,
  "createdAt": "2025-01-27T10:10:00Z",
  "completedAt": "2025-01-27T10:10:30Z"
}
```

**Important:** Access the edited image via `generatedImageCompletion.imageVersions.original`

### List Image Edits

**Endpoint:** `GET /image-edits`

Retrieves a list of user's image edits.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 10 | Results per page |

---

## Image Upscaling

### Create Upscale

**Endpoint:** `POST /upscales`

Upscales an image to higher resolution.

#### Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `imageUrl` | string | Conditional | URL of single source image |
| `imageUrls` | array | Conditional | Array of image URLs for batch upscaling |
| `imageCompletionId` | string | Conditional | ID of previously generated image |
| `strength` | integer | No | Upscale factor (1-3, default: 2) |
| `mode` | string | No | Upscale mode |
| `size` | integer | No | Target size |

#### Example Request - Single Image

```json
{
  "imageCompletionId": "img_abc123xyz",
  "strength": 2
}
```

#### Example Request - Batch Upscaling

```json
{
  "imageUrls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "strength": 2
}
```

#### Response

```json
{
  "id": "ups_jkl012mno",
  "status": "new",
  "createdAt": "2025-01-27T10:15:00Z"
}
```

### Get Upscale Status

**Endpoint:** `GET /upscales/{id}`

Retrieves the status and result of an upscale job.

---

## Custom AI Models (Trained Models)

LetzAI users can train custom AI models on persons, objects, or styles via the web interface. These trained models can then be used in prompts via the `@modelname` syntax.

### List Trained Models

**Endpoint:** `GET /models`

Retrieves a list of user's trained AI models.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number for pagination |
| `limit` | integer | 10 | Number of results per page |
| `sortBy` | string | - | Sort field: `"createdAt"` or `"usages"` |
| `sortOrder` | string | - | Sort direction: `"ASC"` or `"DESC"` |
| `class` | string | - | Filter by model class: `"person"`, `"object"`, `"style"` |

#### Model Classes

| Class | Description |
|-------|-------------|
| `person` | Trained on photos of a specific person |
| `object` | Trained on product/object images |
| `style` | Trained on artistic style examples |

#### Example Request

```
GET /models?class=person&limit=5&sortBy=usages&sortOrder=DESC
```

#### Response

```json
{
  "data": [
    {
      "id": "model_abc123",
      "name": "john_doe",
      "class": "person",
      "createdAt": "2025-01-15T08:00:00Z",
      "usages": 42,
      "thumbnail": "https://cdn.letz.ai/models/model_abc123/thumb.jpg"
    },
    {
      "id": "model_def456",
      "name": "vintage_style",
      "class": "style",
      "createdAt": "2025-01-10T12:00:00Z",
      "usages": 28,
      "thumbnail": "https://cdn.letz.ai/models/model_def456/thumb.jpg"
    }
  ],
  "page": 1,
  "limit": 5,
  "total": 12
}
```

### Get Model Details

**Endpoint:** `GET /models/{id}`

Retrieves detailed information about a specific trained model.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | The trained model ID |

#### Response

```json
{
  "id": "model_abc123",
  "name": "john_doe",
  "class": "person",
  "createdAt": "2025-01-15T08:00:00Z",
  "usages": 42,
  "thumbnail": "https://cdn.letz.ai/models/model_abc123/thumb.jpg",
  "trainingImages": 20,
  "status": "ready"
}
```

### Using Trained Models in Prompts

Tag models in prompts using `@modelname` syntax:

```javascript
// Generate image with a person model
{
  "prompt": "@john_doe on the beach at sunset",
  "baseModel": "gemini-3-pro-image-preview",
  "mode": "2k"
}

// Generate image with an object model
{
  "prompt": "A product photo featuring @my_product in studio lighting",
  "baseModel": "gemini-3-pro-image-preview",
  "mode": "2k"
}

// Generate image with a style model
{
  "prompt": "Portrait of a woman in @vintage_style aesthetic",
  "baseModel": "gemini-3-pro-image-preview",
  "mode": "2k"
}
```

**Note:** Model training is done via the LetzAI web interface (letz.ai), not via API.

---

## Status Values

All generation jobs use the following status values:

| Status | Description |
|--------|-------------|
| `new` | Job has been created and queued |
| `in progress` | Job is currently being processed |
| `generating` | Alternative status for processing |
| `ready` | Job completed successfully |
| `failed` | Job failed - check error field |

---

## Error Responses

### Error Format

```json
{
  "error": "Description of the error",
  "code": "ERROR_CODE",
  "details": {}
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 402 | Payment Required - Insufficient credits |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limited |
| 500 | Internal Server Error |

### Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_API_KEY` | The provided API key is invalid |
| `INSUFFICIENT_CREDITS` | Account doesn't have enough credits |
| `INVALID_MODEL` | The specified model doesn't exist |
| `INVALID_PARAMETERS` | Request parameters are invalid |
| `CONTENT_POLICY_VIOLATION` | Prompt violates content policy |
| `GENERATION_FAILED` | The generation process failed |

---

## Webhooks

LetzAI supports webhooks for receiving notifications when jobs complete. Include a `webhookUrl` parameter when creating jobs:

```json
{
  "prompt": "A beautiful landscape",
  "baseModel": "gemini-3-pro-image-preview",
  "webhookUrl": "https://your-server.com/api/letzai/callback"
}
```

The webhook will receive a POST request when the job completes or fails.

**Note:** Refer to [api.letz.ai/doc](https://api.letz.ai/doc) for complete webhook payload documentation.
