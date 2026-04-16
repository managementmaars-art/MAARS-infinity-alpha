import { 
  S3Client, 
  PutObjectCommand, 
  DeleteObjectCommand, 
  GetObjectCommand,
  HeadObjectCommand 
} from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

/**
 * S3-compatible storage utilities (works with Railway Storage, AWS S3, Cloudflare R2, etc.)
 * 
 * Features:
 * - Lazy-loaded singleton client
 * - Presigned URLs for secure uploads/downloads
 * - Range request support for video streaming
 * - Proxy pattern for private buckets
 */

let s3Client: S3Client | null = null;

function getS3Client(): S3Client {
  if (!s3Client) {
    s3Client = new S3Client({
      endpoint: process.env.AWS_ENDPOINT_URL,
      region: process.env.AWS_DEFAULT_REGION ?? "auto",
      credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
      },
      forcePathStyle: true, // Required for Railway/MinIO
    });
  }
  return s3Client;
}

export function getS3Bucket(): string {
  return process.env.AWS_S3_BUCKET_NAME!;
}

/**
 * Upload a file directly to S3
 * Returns a proxy URL since Railway storage doesn't support public buckets
 */
export async function uploadToS3(
  key: string,
  body: Buffer,
  contentType: string
): Promise<string> {
  const client = getS3Client();
  const bucket = process.env.AWS_S3_BUCKET_NAME!;

  await client.send(
    new PutObjectCommand({
      Bucket: bucket,
      Key: key,
      Body: body,
      ContentType: contentType,
    })
  );

  // Return proxy URL since Railway storage doesn't support public buckets
  return `/uploads/${key}`;
}

/**
 * Get a presigned URL for downloading an S3 object
 * @param key - S3 object key
 * @param expiresIn - URL expiration in seconds (default 1 hour)
 */
export async function getPresignedUrl(key: string, expiresIn = 3600): Promise<string> {
  const client = getS3Client();
  const bucket = process.env.AWS_S3_BUCKET_NAME!;

  const command = new GetObjectCommand({
    Bucket: bucket,
    Key: key,
  });

  return getSignedUrl(client, command, { expiresIn });
}

/**
 * Get a presigned URL for uploading to S3
 * This allows direct client-to-S3 uploads for large files
 */
export async function getPresignedUploadUrl(
  key: string,
  contentType: string,
  expiresIn = 3600
): Promise<string> {
  const client = getS3Client();
  const bucket = process.env.AWS_S3_BUCKET_NAME!;

  const command = new PutObjectCommand({
    Bucket: bucket,
    Key: key,
    ContentType: contentType,
  });

  return getSignedUrl(client, command, { expiresIn });
}

/**
 * Get an object from S3 with optional range support for streaming
 */
export async function getS3Object(
  key: string,
  range?: string
): Promise<{
  body: ReadableStream;
  contentType: string;
  contentLength: number;
  contentRange?: string;
  acceptRanges: string;
} | null> {
  const client = getS3Client();
  const bucket = process.env.AWS_S3_BUCKET_NAME!;

  const response = await client.send(
    new GetObjectCommand({
      Bucket: bucket,
      Key: key,
      Range: range,
    })
  );

  if (!response.Body) return null;

  return {
    body: response.Body.transformToWebStream(),
    contentType: response.ContentType || "application/octet-stream",
    contentLength: response.ContentLength || 0,
    contentRange: response.ContentRange,
    acceptRanges: response.AcceptRanges || "bytes",
  };
}

/**
 * Get S3 object metadata (HEAD request)
 */
export async function getS3ObjectMetadata(key: string): Promise<{
  contentType: string;
  contentLength: number;
} | null> {
  const client = getS3Client();
  const bucket = process.env.AWS_S3_BUCKET_NAME!;
  
  const response = await client.send(
    new HeadObjectCommand({
      Bucket: bucket,
      Key: key,
    })
  );

  return {
    contentType: response.ContentType || "application/octet-stream",
    contentLength: response.ContentLength || 0,
  };
}

/**
 * Get an S3 object as a Buffer
 */
export async function getS3ObjectBuffer(key: string): Promise<Buffer | null> {
  const client = getS3Client();
  const bucket = process.env.AWS_S3_BUCKET_NAME!;

  const response = await client.send(
    new GetObjectCommand({
      Bucket: bucket,
      Key: key,
    })
  );

  if (!response.Body) return null;

  const chunks: Uint8Array[] = [];
  for await (const chunk of response.Body as AsyncIterable<Uint8Array>) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}

/**
 * Extract S3 key from a URL (supports proxy URLs and direct S3 URLs)
 */
export function getS3KeyFromUrl(url: string | null): string | null {
  if (!url) return null;
  
  // Proxy format: /uploads/{key}
  if (url.startsWith("/uploads/")) {
    return url.slice("/uploads/".length);
  }
  
  // Direct S3 format: ${endpoint}/${bucket}/{key}
  const endpoint = process.env.AWS_ENDPOINT_URL;
  const bucket = process.env.AWS_S3_BUCKET_NAME;
  const prefix = `${endpoint}/${bucket}/`;
  
  if (url.startsWith(prefix)) {
    return url.slice(prefix.length);
  }
  
  return null;
}

/**
 * Delete an object from S3
 */
export async function deleteFromS3(key: string): Promise<void> {
  const client = getS3Client();
  const bucket = process.env.AWS_S3_BUCKET_NAME!;

  await client.send(
    new DeleteObjectCommand({
      Bucket: bucket,
      Key: key,
    })
  );
}

/**
 * Download an image from URL and re-upload to S3
 * Useful for persisting expiring CDN URLs
 */
export async function downloadAndUploadImage(
  sourceUrl: string,
  destinationKey: string
): Promise<string | null> {
  const response = await fetch(sourceUrl);
  
  if (!response.ok) {
    return null;
  }
  
  const arrayBuffer = await response.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  
  let contentType = response.headers.get('content-type') || 'image/jpeg';
  if (!contentType.startsWith('image/')) {
    contentType = 'image/jpeg';
  }
  
  return uploadToS3(destinationKey, buffer, contentType);
}
