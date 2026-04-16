---
title: Build Field Plugins with SDK
impact: HIGH
impactDescription: enables custom editor experiences
tags: plugin, field-plugin, sdk, extension
---

## Build Field Plugins with SDK

**Impact: HIGH (enables custom editor experiences)**

Use the `@storyblok/field-plugin` SDK to build custom field plugins. It handles communication with Storyblok, provides type safety, and includes development tools.

**Incorrect (manual postMessage handling):**

```jsx
// Bad: Manual postMessage without SDK
const CustomField = () => {
  const [value, setValue] = useState('');

  useEffect(() => {
    // Manual, error-prone implementation
    window.addEventListener('message', (e) => {
      if (e.data.action === 'loaded') {
        setValue(e.data.story.content.myField);
      }
    });

    window.parent.postMessage({
      action: 'tool-changed',
      value: value
    }, '*');
  }, [value]);

  return <input value={value} onChange={(e) => setValue(e.target.value)} />;
};
```

**Correct (using @storyblok/field-plugin):**

```jsx
// Good: React field plugin with SDK
import { useFieldPlugin } from '@storyblok/field-plugin/react';

const ColorPickerField = () => {
  const { data, actions, type } = useFieldPlugin();

  if (type !== 'loaded') {
    return <div>Loading...</div>;
  }

  const { content } = data;

  const handleColorChange = (color) => {
    actions.setContent(color);
  };

  return (
    <div className="color-picker">
      <input
        type="color"
        value={content || '#000000'}
        onChange={(e) => handleColorChange(e.target.value)}
      />
      <span>{content}</span>
    </div>
  );
};

export default ColorPickerField;
```

```jsx
// Good: Complex field plugin with validation
import { useFieldPlugin } from '@storyblok/field-plugin/react';

const LocationPickerField = () => {
  const { data, actions, type } = useFieldPlugin();

  if (type !== 'loaded') {
    return <div>Loading...</div>;
  }

  const { content, options } = data;
  const location = content || { lat: 0, lng: 0, address: '' };

  const handleLocationChange = async (lat, lng) => {
    // Validate coordinates
    if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
      return;
    }

    // Reverse geocode (example)
    const address = await reverseGeocode(lat, lng);

    actions.setContent({
      lat,
      lng,
      address
    });
  };

  const handleModalOpen = () => {
    actions.setModalOpen(true);
  };

  return (
    <div className="location-picker">
      <div className="preview">
        <span>{location.address || 'No location selected'}</span>
        <button onClick={handleModalOpen}>Select Location</button>
      </div>

      {data.isModalOpen && (
        <div className="modal">
          <MapComponent
            lat={location.lat}
            lng={location.lng}
            onSelect={handleLocationChange}
          />
          <button onClick={() => actions.setModalOpen(false)}>Close</button>
        </div>
      )}
    </div>
  );
};
```

```jsx
// Good: Vue field plugin
<template>
  <div class="icon-picker">
    <div class="selected" v-if="content">
      <component :is="content" />
      <span>{{ content }}</span>
    </div>
    <div class="grid">
      <button
        v-for="icon in icons"
        :key="icon"
        @click="selectIcon(icon)"
        :class="{ active: content === icon }"
      >
        <component :is="icon" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { useFieldPlugin } from '@storyblok/field-plugin/vue3';

const { data, actions, type } = useFieldPlugin();
const content = computed(() => data.value?.content);

const icons = ['home', 'user', 'settings', 'mail', 'phone'];

const selectIcon = (icon) => {
  actions.setContent(icon);
};
</script>
```

**manifest.json configuration:**

```json
{
  "options": [
    {
      "name": "apiKey",
      "type": "text",
      "description": "API key for external service"
    },
    {
      "name": "defaultValue",
      "type": "text",
      "description": "Default color value"
    },
    {
      "name": "showPreview",
      "type": "boolean",
      "description": "Show color preview"
    }
  ]
}
```

**Field plugin actions:**

| Action | Description | Usage |
|--------|-------------|-------|
| `setContent(value)` | Update field value | Main data storage |
| `setModalOpen(bool)` | Toggle modal state | Complex editors |
| `requestAICompletion(prompt)` | AI-powered content | Text generation |

**Development workflow:**

```bash
# Create new field plugin
npx @storyblok/field-plugin create my-plugin

# Start development with sandbox
npm run dev

# Deploy to Storyblok
npm run deploy
```

Reference: [Field Plugin Development](https://www.storyblok.com/docs/plugins/field-plugins/development)
