---
name: remotion-video
version: 1.0.0
description: Remotion video programming with React - compositions, animations, Lambda rendering, audio, Tailwind, and programmatic video creation
tags: [remotion, video, react, typescript, animation, lambda, rendering, motion]
---

# Remotion Video

Create videos programmatically using React. Every frame is a React component rendered to an image and assembled into a video.

## Setup

```bash
# Create new project
npx create-video@latest

# Add to existing project
npm install remotion @remotion/player @remotion/cli

# Lambda rendering
npm install @remotion/lambda

# Tailwind support
npm install @remotion/tailwind

# Development preview
npx remotion studio
```

---

## Core Concepts

```typescript
// Root.tsx - register all compositions
import { Composition } from "remotion";
import { MyVideo } from "./MyVideo";
import { Intro } from "./Intro";

export const RemotionRoot = () => (
  <>
    <Composition
      id="MyVideo"
      component={MyVideo}
      durationInFrames={300}    // 10 seconds at 30fps
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        title: "Hello World",
        accent: "#ff4d4d",
      }}
    />
    <Composition
      id="Intro"
      component={Intro}
      durationInFrames={90}
      fps={30}
      width={1280}
      height={720}
    />
  </>
);

// MyVideo.tsx - the video component
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

interface MyVideoProps {
  title: string;
  accent: string;
}

export const MyVideo: React.FC<MyVideoProps> = ({ title, accent }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps, width, height } = useVideoConfig();

  // frame: current frame number (0-indexed)
  // durationInFrames: total frames
  // fps: frames per second
  // Calculate time: const timeInSeconds = frame / fps;

  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a2e" }}>
      <h1 style={{ color: accent, fontSize: 80 }}>{title}</h1>
      <p>Frame: {frame}</p>
    </AbsoluteFill>
  );
};
```

---

## Animations and Interpolation

```typescript
import {
  useCurrentFrame,
  interpolate,
  spring,
  Easing,
  AbsoluteFill,
} from "remotion";

export const AnimatedScene: React.FC = () => {
  const frame = useCurrentFrame();

  // interpolate: map frame range to value range
  const opacity = interpolate(
    frame,
    [0, 30],                       // input: frames 0-30
    [0, 1],                        // output: 0 to 1
    { extrapolateRight: "clamp" }  // don't go beyond 1
  );

  const slideX = interpolate(
    frame,
    [0, 45],
    [-200, 0],
    {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  const scale = interpolate(frame, [0, 20], [0.5, 1], {
    easing: Easing.bezier(0.34, 1.56, 0.64, 1),  // spring-like
    extrapolateRight: "clamp",
  });

  // spring: physics-based spring animation (always starts at 0, moves to 1)
  const springValue = spring({
    frame,                    // current frame
    fps: 30,
    config: {
      damping: 12,            // higher = less bounce
      stiffness: 100,         // higher = faster
      mass: 1,
    },
    delay: 15,                // start spring after N frames
    durationInFrames: 60,     // limit spring duration
  });

  const springScale = interpolate(springValue, [0, 1], [0.8, 1]);

  return (
    <AbsoluteFill>
      <div
        style={{
          opacity,
          transform: `translateX(${slideX}px) scale(${springScale})`,
          position: "absolute",
          top: "50%",
          left: "50%",
          translate: "-50% -50%",
        }}
      >
        <h1 style={{ color: "white", fontSize: 72 }}>Animated Title</h1>
      </div>
    </AbsoluteFill>
  );
};
```

---

## Sequences and Timing

```typescript
import { Sequence, Series, Loop, AbsoluteFill, useCurrentFrame } from "remotion";

// Sequence: render child component starting at a specific frame
export const TimelineVideo: React.FC = () => (
  <AbsoluteFill>
    {/* Intro plays from frame 0 */}
    <Sequence from={0} durationInFrames={60}>
      <IntroScene />
    </Sequence>

    {/* Main content plays from frame 60 */}
    <Sequence from={60} durationInFrames={180} name="Main">
      <MainScene />
    </Sequence>

    {/* Outro plays from frame 240 */}
    <Sequence from={240} durationInFrames={60}>
      <OutroScene />
    </Sequence>

    {/* Layout sequence: shift child's frame to start at 0 */}
    <Sequence from={120} layout="none">
      {/* This component receives frame 0 at the 120th video frame */}
      <OverlayBadge />
    </Sequence>
  </AbsoluteFill>
);

// Series: automatically chains sequences back-to-back
export const SeriesExample: React.FC = () => (
  <Series>
    <Series.Sequence durationInFrames={60}>
      <IntroScene />
    </Series.Sequence>
    <Series.Sequence durationInFrames={180}>
      <MainScene />
    </Series.Sequence>
    <Series.Sequence durationInFrames={60}>
      <OutroScene />
    </Series.Sequence>
  </Series>
);

// Loop: repeat a component N times
export const LoopExample: React.FC = () => (
  <Loop durationInFrames={30} times={5}>
    <BlinkingDot />
  </Loop>
);
```

---

## Audio and Video Assets

```typescript
import {
  Audio,
  Video,
  Img,
  staticFile,
  OffthreadVideo,
  useCurrentFrame,
  interpolate,
} from "remotion";

export const MediaScene: React.FC = () => {
  const frame = useCurrentFrame();

  const audioVolume = interpolate(frame, [0, 30, 270, 300], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      {/* Background music with fade in/out */}
      <Audio
        src={staticFile("background-music.mp3")}
        volume={audioVolume}
        startFrom={30}   // skip first 1 second of audio
        endAt={270}      // stop audio at this audio frame
        loop
      />

      {/* Audio from URL */}
      <Audio src="https://cdn.example.com/sfx/click.wav" volume={0.5} />

      {/* Background video (use OffthreadVideo for better performance) */}
      <OffthreadVideo
        src={staticFile("background.mp4")}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
        muted
        loop
      />

      {/* Image */}
      <Img
        src={staticFile("logo.png")}
        style={{ width: 200, position: "absolute", top: 40, right: 40 }}
      />

      {/* Remote image */}
      <Img src="https://picsum.photos/800/600" style={{ width: 800 }} />
    </AbsoluteFill>
  );
};
```

---

## Tailwind CSS in Remotion

```typescript
// remotion.config.ts - enable Tailwind
import { Config } from "@remotion/cli/config";
import { enableTailwind } from "@remotion/tailwind";

Config.overrideWebpackConfig((config) => enableTailwind(config));

// Now use Tailwind classes in your video components
export const TailwindScene: React.FC<{ title: string }> = ({ title }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill className="bg-gradient-to-br from-purple-900 to-indigo-900 flex items-center justify-center">
      <div
        className="text-center"
        style={{ opacity }}
      >
        <h1 className="text-8xl font-bold text-white mb-4">{title}</h1>
        <p className="text-2xl text-purple-300">Remotion + Tailwind</p>
        <div className="mt-8 flex gap-4 justify-center">
          <span className="px-6 py-3 bg-white text-purple-900 rounded-full font-semibold">
            Feature One
          </span>
          <span className="px-6 py-3 border-2 border-white text-white rounded-full font-semibold">
            Feature Two
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

---

## Lambda Rendering

```typescript
// Deploy Lambda function (run once)
import { deployFunction, deploySite, getOrCreateBucket } from "@remotion/lambda";

async function deploy() {
  const { bucketName } = await getOrCreateBucket({ region: "us-east-1" });

  const { functionName } = await deployFunction({
    region: "us-east-1",
    timeoutInSeconds: 120,
    memorySizeInMb: 2048,
    createCloudWatchLogGroup: true,
    skipCreatingFunction: false,
  });

  const { serveUrl } = await deploySite({
    bucketName,
    entryPoint: "./src/index.ts",
    region: "us-east-1",
    siteName: "my-video-site",
  });

  return { functionName, serveUrl };
}

// Render a video via Lambda
import { renderMediaOnLambda, getRenderProgress } from "@remotion/lambda";

async function renderVideo(props: { title: string; accent: string }) {
  const { renderId, bucketName } = await renderMediaOnLambda({
    region: "us-east-1",
    functionName: "remotion-render-3-3-82-mem2048mb-disk2048mb-120sec",
    serveUrl: "https://remotionlambda-xxx.s3.us-east-1.amazonaws.com/sites/my-video-site/index.html",
    composition: "MyVideo",
    inputProps: props,
    codec: "h264",
    imageFormat: "jpeg",
    maxRetries: 1,
    framesPerLambda: 20,
    privacy: "public",   // or "private"
    outName: `output-${Date.now()}.mp4`,
  });

  // Poll for progress
  while (true) {
    const progress = await getRenderProgress({
      renderId,
      bucketName,
      functionName: "remotion-render-3-3-82-mem2048mb-disk2048mb-120sec",
      region: "us-east-1",
    });

    if (progress.done) {
      console.log("Output URL:", progress.outputFile);
      break;
    }
    if (progress.fatalErrorEncountered) {
      throw new Error(progress.errors[0].message);
    }

    console.log(`Progress: ${Math.round(progress.overallProgress * 100)}%`);
    await new Promise((r) => setTimeout(r, 2000));
  }
}
```

---

## Player Component (Browser Preview)

```tsx
import { Player } from "@remotion/player";
import { MyVideo } from "./MyVideo";

export const VideoPlayer: React.FC = () => (
  <Player
    component={MyVideo}
    inputProps={{ title: "Hello World", accent: "#ff4d4d" }}
    durationInFrames={300}
    fps={30}
    compositionWidth={1920}
    compositionHeight={1080}
    style={{ width: "100%", aspectRatio: "16/9" }}
    controls
    autoPlay
    loop
    showVolumeControls
    doubleClickToFullscreen
    spaceKeyToPlayOrPause
    clickToPlay
  />
);
```

---

## Dynamic Data Visualization

```typescript
import { useCurrentFrame, interpolate, AbsoluteFill } from "remotion";

interface BarChartProps {
  data: { label: string; value: number; color: string }[];
}

export const AnimatedBarChart: React.FC<BarChartProps> = ({ data }) => {
  const frame = useCurrentFrame();
  const maxValue = Math.max(...data.map((d) => d.value));

  return (
    <AbsoluteFill className="bg-gray-900 p-20 flex items-end gap-8 justify-center">
      {data.map((item, i) => {
        // Stagger bar animations by index
        const delay = i * 5;
        const progress = interpolate(frame, [delay, delay + 40], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });

        const barHeight = (item.value / maxValue) * 400 * progress;

        return (
          <div key={item.label} className="flex flex-col items-center gap-4">
            <div
              style={{
                width: 80,
                height: barHeight,
                backgroundColor: item.color,
                borderRadius: "8px 8px 0 0",
              }}
            />
            <span className="text-white text-xl font-semibold">{item.label}</span>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
```

---

## Best Practices

- **Use `useCurrentFrame()` for all time-based logic**: never use `Date.now()` or `setTimeout` in components
- **Deterministic rendering**: same frame must always produce the same output; avoid random values without seeds
- **`staticFile()` for local assets**: put media in `public/` directory, reference with `staticFile("name.mp4")`
- **`OffthreadVideo` over `Video`**: `OffthreadVideo` is faster and more reliable for video backgrounds
- **Clamp extrapolation**: almost always use `extrapolateLeft: "clamp", extrapolateRight: "clamp"` to prevent unexpected values outside the keyframe range
- **Memoize expensive components**: use `React.memo` and `useMemo` for data-heavy scenes
- **Test compositions in Studio**: use `npx remotion studio` for rapid iteration before Lambda
- **Bundle size matters for Lambda**: avoid large dependencies; prefer Remotion's built-in primitives
- **Stagger animations**: delay each element's animation by `i * N` frames for natural cascading effects
- **Separate concerns**: create one React component per "scene" and compose them in a main composition

## Models to Use

- **claude-opus-4-5**: Designing complex video compositions, data visualization systems, multi-scene architecture
- **claude-sonnet-4-5**: Implementing animations, interpolation logic, Lambda deployment scripts, scene components
- **claude-haiku-3-5**: Simple scene components, boilerplate sequences, quick animation snippets
