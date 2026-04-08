import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const PARTICLE_COUNT = 1800;

export default function VoidParticles() {
  const pointsRef = useRef();

  const { positions, velocities, phases } = useMemo(() => {
    const pos  = new Float32Array(PARTICLE_COUNT * 3);
    const vel  = new Float32Array(PARTICLE_COUNT * 3);
    const ph   = new Float32Array(PARTICLE_COUNT);
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      // Distribute in a large sphere shell
      const theta = Math.random() * Math.PI * 2;
      const phi   = Math.acos(2 * Math.random() - 1);
      const r     = 5.5 + Math.random() * 7;
      pos[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
      vel[i * 3]     = (Math.random() - 0.5) * 0.002;
      vel[i * 3 + 1] = (Math.random() - 0.5) * 0.002;
      vel[i * 3 + 2] = (Math.random() - 0.5) * 0.002;
      ph[i] = Math.random() * Math.PI * 2;
    }
    return { positions: pos, velocities: vel, phases: ph };
  }, []);

  useFrame(({ clock }) => {
    if (!pointsRef.current) return;
    const t   = clock.elapsedTime;
    const pos = pointsRef.current.geometry.attributes.position.array;
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const ph = phases[i];
      const ox  = Math.sin(t * 0.1 + ph) * 0.004;
      const oy  = Math.cos(t * 0.13 + ph * 1.4) * 0.004;
      const oz  = Math.sin(t * 0.08 + ph * 0.7) * 0.004;
      pos[i * 3]     += velocities[i * 3]     + ox;
      pos[i * 3 + 1] += velocities[i * 3 + 1] + oy;
      pos[i * 3 + 2] += velocities[i * 3 + 2] + oz;

      // Gentle boundary: repel back toward shell if too far/close
      const x = pos[i * 3], y = pos[i * 3 + 1], z = pos[i * 3 + 2];
      const dist = Math.sqrt(x * x + y * y + z * z);
      if (dist > 13 || dist < 4.5) {
        pos[i * 3]     *= 0.99;
        pos[i * 3 + 1] *= 0.99;
        pos[i * 3 + 2] *= 0.99;
      }
    }
    pointsRef.current.geometry.attributes.position.needsUpdate = true;
    // Slow rotation
    pointsRef.current.rotation.y = t * 0.012;
  });

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    return geo;
  }, [positions]);

  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        size={0.022}
        color="#4fd1c5"
        transparent
        opacity={0.5}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
}
