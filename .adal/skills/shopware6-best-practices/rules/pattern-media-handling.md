---
title: Media Upload & Processing
impact: MEDIUM
impactDescription: proper media management for products and content
tags: media, upload, image, file, thumbnail
---

## Media Upload & Processing

**Impact: MEDIUM (proper media management for products and content)**

Use Shopware's media service for file uploads and processing. Handle thumbnails, private files, and media associations correctly.

**Incorrect (direct file handling):**

```php
// Bad: Direct file operations
move_uploaded_file($_FILES['image']['tmp_name'], '/var/www/public/media/image.jpg');

// Bad: Not using media service
$product->setCoverUrl('/media/image.jpg');
```

**Correct media upload service:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Content\Media\File\FileSaver;
use Shopware\Core\Content\Media\File\MediaFile;
use Shopware\Core\Content\Media\MediaService;
use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\Uuid\Uuid;

class MediaUploadService
{
    public function __construct(
        private readonly MediaService $mediaService,
        private readonly FileSaver $fileSaver,
        private readonly EntityRepository $mediaRepository,
        private readonly EntityRepository $mediaFolderRepository
    ) {}

    /**
     * Upload media from URL
     */
    public function uploadFromUrl(
        string $url,
        string $fileName,
        Context $context,
        ?string $folderId = null
    ): string {
        // Get folder or create default
        $folderId = $folderId ?? $this->getOrCreateFolder('My Plugin Media', $context);

        // Create media entity
        $mediaId = Uuid::randomHex();

        $this->mediaRepository->create([
            [
                'id' => $mediaId,
                'mediaFolderId' => $folderId
            ]
        ], $context);

        // Download and save file
        $this->mediaService->saveMediaFile(
            $this->downloadFile($url),
            $fileName,
            $context,
            'my_plugin_media',
            $mediaId
        );

        return $mediaId;
    }

    /**
     * Upload from file path
     */
    public function uploadFromFile(
        string $filePath,
        string $fileName,
        Context $context,
        ?string $folderId = null
    ): string {
        if (!file_exists($filePath)) {
            throw new \InvalidArgumentException('File not found: ' . $filePath);
        }

        $folderId = $folderId ?? $this->getOrCreateFolder('My Plugin Media', $context);

        // Create media entity
        $mediaId = Uuid::randomHex();

        $this->mediaRepository->create([
            [
                'id' => $mediaId,
                'mediaFolderId' => $folderId
            ]
        ], $context);

        // Create MediaFile from path
        $mediaFile = new MediaFile(
            $filePath,
            mime_content_type($filePath),
            pathinfo($filePath, PATHINFO_EXTENSION),
            filesize($filePath)
        );

        // Save with FileSaver
        $this->fileSaver->persistFileToMedia(
            $mediaFile,
            $fileName,
            $mediaId,
            $context
        );

        return $mediaId;
    }

    /**
     * Upload from uploaded file (controller context)
     */
    public function uploadFromRequest(
        UploadedFile $uploadedFile,
        Context $context,
        ?string $folderId = null
    ): string {
        $folderId = $folderId ?? $this->getOrCreateFolder('My Plugin Media', $context);

        $mediaId = Uuid::randomHex();

        $this->mediaRepository->create([
            [
                'id' => $mediaId,
                'mediaFolderId' => $folderId
            ]
        ], $context);

        $mediaFile = new MediaFile(
            $uploadedFile->getPathname(),
            $uploadedFile->getMimeType(),
            $uploadedFile->getClientOriginalExtension(),
            $uploadedFile->getSize()
        );

        $fileName = pathinfo($uploadedFile->getClientOriginalName(), PATHINFO_FILENAME);

        $this->fileSaver->persistFileToMedia(
            $mediaFile,
            $fileName,
            $mediaId,
            $context
        );

        return $mediaId;
    }

    /**
     * Get or create media folder
     */
    private function getOrCreateFolder(string $folderName, Context $context): string
    {
        // Check if folder exists
        $criteria = new Criteria();
        $criteria->addFilter(new EqualsFilter('name', $folderName));

        $folder = $this->mediaFolderRepository->search($criteria, $context)->first();

        if ($folder) {
            return $folder->getId();
        }

        // Create folder
        $folderId = Uuid::randomHex();

        // Get default configuration
        $configCriteria = new Criteria();
        $configCriteria->addFilter(new EqualsFilter('name', 'Default'));
        $config = $this->mediaFolderConfigRepository->search($configCriteria, $context)->first();

        $this->mediaFolderRepository->create([
            [
                'id' => $folderId,
                'name' => $folderName,
                'configurationId' => $config?->getId(),
                'configuration' => $config ? null : [
                    'createThumbnails' => true,
                    'keepAspectRatio' => true,
                    'thumbnailQuality' => 80,
                    'mediaThumbnailSizes' => [
                        ['width' => 400, 'height' => 400],
                        ['width' => 800, 'height' => 800],
                        ['width' => 1920, 'height' => 1920]
                    ]
                ]
            ]
        ], $context);

        return $folderId;
    }

    private function downloadFile(string $url): MediaFile
    {
        $tempFile = tempnam(sys_get_temp_dir(), 'media_');
        file_put_contents($tempFile, file_get_contents($url));

        $mimeType = mime_content_type($tempFile);
        $extension = $this->getExtensionFromMimeType($mimeType);

        return new MediaFile(
            $tempFile,
            $mimeType,
            $extension,
            filesize($tempFile)
        );
    }

    private function getExtensionFromMimeType(string $mimeType): string
    {
        return match ($mimeType) {
            'image/jpeg' => 'jpg',
            'image/png' => 'png',
            'image/gif' => 'gif',
            'image/webp' => 'webp',
            'application/pdf' => 'pdf',
            default => 'bin'
        };
    }
}
```

**Correct product media association:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class ProductMediaService
{
    public function __construct(
        private readonly EntityRepository $productRepository,
        private readonly EntityRepository $productMediaRepository,
        private readonly MediaUploadService $uploadService
    ) {}

    public function setProductCover(
        string $productId,
        string $mediaId,
        Context $context
    ): void {
        // Create product media association
        $productMediaId = Uuid::randomHex();

        $this->productMediaRepository->create([
            [
                'id' => $productMediaId,
                'productId' => $productId,
                'mediaId' => $mediaId,
                'position' => 1
            ]
        ], $context);

        // Set as cover
        $this->productRepository->update([
            [
                'id' => $productId,
                'coverId' => $productMediaId
            ]
        ], $context);
    }

    public function addProductImages(
        string $productId,
        array $mediaIds,
        Context $context
    ): void {
        $productMedia = [];
        $position = 1;

        foreach ($mediaIds as $mediaId) {
            $productMedia[] = [
                'id' => Uuid::randomHex(),
                'productId' => $productId,
                'mediaId' => $mediaId,
                'position' => $position++
            ];
        }

        if (!empty($productMedia)) {
            $this->productMediaRepository->create($productMedia, $context);
        }
    }

    public function uploadAndSetCover(
        string $productId,
        string $imageUrl,
        Context $context
    ): string {
        // Upload image
        $mediaId = $this->uploadService->uploadFromUrl(
            $imageUrl,
            'product-' . $productId,
            $context
        );

        // Set as cover
        $this->setProductCover($productId, $mediaId, $context);

        return $mediaId;
    }
}
```

**Correct thumbnail generation:**

```php
public function generateThumbnails(string $mediaId, Context $context): void
{
    $criteria = new Criteria([$mediaId]);
    $criteria->addAssociation('mediaFolder.configuration.mediaThumbnailSizes');

    $media = $this->mediaRepository->search($criteria, $context)->first();

    if (!$media || !$media->hasFile()) {
        return;
    }

    // Generate thumbnails via message queue
    $this->messageBus->dispatch(
        new GenerateThumbnailsMessage($mediaId)
    );
}
```

**Getting media URLs:**

```php
// In Twig template
{{ product.cover.media.url }}

// Thumbnail URL
{{ product.cover.media.thumbnails|first.url }}

// Specific thumbnail size
{% for thumbnail in product.cover.media.thumbnails %}
    {% if thumbnail.width == 400 %}
        <img src="{{ thumbnail.url }}" alt="{{ product.name }}">
    {% endif %}
{% endfor %}

// With sw_thumbnails
{% sw_thumbnails 'my-thumbnails' with {
    media: product.cover.media,
    sizes: {
        'default': '200px',
        'md': '400px',
        'lg': '800px'
    }
} %}
```

**Private media (protected downloads):**

```php
public function createPrivateMedia(
    string $filePath,
    string $fileName,
    Context $context
): string {
    // Get or create private folder
    $folderId = $this->getOrCreatePrivateFolder($context);

    return $this->uploadFromFile($filePath, $fileName, $context, $folderId);
}

private function getOrCreatePrivateFolder(Context $context): string
{
    $criteria = new Criteria();
    $criteria->addFilter(new EqualsFilter('name', 'My Plugin Private'));
    $criteria->addFilter(new EqualsFilter('configuration.private', true));

    $folder = $this->mediaFolderRepository->search($criteria, $context)->first();

    if ($folder) {
        return $folder->getId();
    }

    $folderId = Uuid::randomHex();

    $this->mediaFolderRepository->create([
        [
            'id' => $folderId,
            'name' => 'My Plugin Private',
            'configuration' => [
                'private' => true, // Private folder
                'createThumbnails' => false
            ]
        ]
    ], $context);

    return $folderId;
}
```

Reference: [Media Handling](https://developer.shopware.com/docs/guides/plugins/plugins/content/media/add-media-to-product.html)
