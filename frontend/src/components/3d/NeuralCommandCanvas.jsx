import { Suspense, useRef, useState, useEffect } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Environment, AdaptiveDpr } from "@react-three/drei";
import { EffectComposer, Bloom, ChromaticAberration } from "@react-three/postprocessing";
import { BlendFunction } from "postprocessing";
import * as THREE from "three";
import NeuralCore from "./NeuralCore";
import AgentNodes from "./AgentNodes";
import VoidParticles from "./VoidParticles";

// Slow cinematic auto-orbit + scroll parallax
function CameraRig({ scrollY }) {
  const { camera } = useThree();
  const targetPos   = useRef(new THREE.Vector3(0, 0, 13));
  const currentPos  = useRef(new THREE.Vector3(0, 0, 13));

  useFrame(({ clock, mouse }) => {
    const t = clock.elapsedTime;
    const scroll = scrollY.current || 0;

    targetPos.current.set(
      mouse.x * 0.8,
      mouse.y * 0.5 + scroll * -0.002,
      13 + scroll * 0.004
    );
    currentPos.current.lerp(targetPos.current, 0.04);
    camera.position.copy(currentPos.current);
    camera.lookAt(0, 0, 0);
  });
  return null;
}

// Ambient pulsing ring around the core
function CoreRing({ idx }) {
  const ref = useRef();
  const phase = idx * (Math.PI * 2) / 3;
  useFrame(({ clock }) => {
    if (!ref.current) return;
    const t = clock.elapsedTime;
    const s = 1 + 0.06 * Math.sin(t * 0.9 + phase);
    ref.current.scale.setScalar(s);
    ref.current.rotation.z = t * 0.08 * (idx % 2 === 0 ? 1 : -1) + phase;
    ref.current.rotation.x = Math.sin(t * 0.05 + phase) * 0.3;
    ref.current.material.opacity = 0.12 + 0.05 * Math.sin(t * 1.1 + phase);
  });
  const radius = 2.1 + idx * 0.55;
  return (
    <mesh ref={ref} rotation={[Math.PI / 2 + idx * 0.3, 0, 0]}>
      <torusGeometry args={[radius, 0.008, 8, 120]} />
      <meshBasicMaterial
        color={idx === 0 ? "#4fd1c5" : idx === 1 ? "#7c3aed" : "#2563eb"}
        transparent
        opacity={0.15}
        depthWrite={false}
      />
    </mesh>
  );
}

function Scene({ scrollY, onSelectAgent }) {
  return (
    <>
      <CameraRig scrollY={scrollY} />

      {/* Deep void lighting */}
      <ambientLight intensity={0.06} />
      <pointLight position={[0, 0, 0]} intensity={3.5} color="#2563eb" distance={8} decay={2} />
      <pointLight position={[6, 4, 3]} intensity={1.2} color="#4fd1c5" distance={12} decay={2} />
      <pointLight position={[-5, -3, -4]} intensity={0.8} color="#7c3aed" distance={10} decay={2} />

      {/* Orbital rings around the core */}
      {[0, 1, 2].map(i => <CoreRing key={i} idx={i} />)}

      {/* The central AI brain */}
      <NeuralCore />

      {/* 72 agent nodes orbiting — interactive: hover shows role label,
          click bubbles up to the LandingPage which displays a toast or
          routes to the agent catalog. */}
      <AgentNodes onSelect={onSelectAgent} />

      {/* Ambient void particles */}
      <VoidParticles />

      {/* Post-processing */}
      <EffectComposer>
        <Bloom
          intensity={1.4}
          luminanceThreshold={0.2}
          luminanceSmoothing={0.9}
          blendFunction={BlendFunction.ADD}
          mipmapBlur
        />
        <ChromaticAberration
          blendFunction={BlendFunction.NORMAL}
          offset={[0.0004, 0.0004]}
        />
      </EffectComposer>

      <AdaptiveDpr pixelated />
    </>
  );
}

export default function NeuralCommandCanvas({ scrollY, onSelectAgent }) {
  return (
    <Canvas
      camera={{ position: [0, 0, 13], fov: 58, near: 0.1, far: 100 }}
      gl={{
        antialias: true,
        alpha: true,
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.1,
      }}
      style={{ background: "transparent" }}
    >
      <Suspense fallback={null}>
        <Scene scrollY={scrollY} onSelectAgent={onSelectAgent} />
      </Suspense>
    </Canvas>
  );
}
