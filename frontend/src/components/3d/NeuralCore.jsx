import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const vertexShader = `
  uniform float uTime;
  uniform float uPulse;
  varying vec3 vNormal;
  varying vec3 vPosition;
  varying float vDisplacement;

  // Simplex-like noise
  vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 permute(vec4 x) { return mod289(((x*34.0)+10.0)*x); }
  vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

  float snoise(vec3 v) {
    const vec2 C = vec2(1.0/6.0, 1.0/3.0);
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
    vec3 i  = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);
    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;
    i = mod289(i);
    vec4 p = permute(permute(permute(
      i.z + vec4(0.0, i1.z, i2.z, 1.0))
      + i.y + vec4(0.0, i1.y, i2.y, 1.0))
      + i.x + vec4(0.0, i1.x, i2.x, 1.0));
    float n_ = 0.142857142857;
    vec3 ns = n_ * D.wyz - D.xzx;
    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);
    vec4 x = x_ *ns.x + ns.yyyy;
    vec4 y = y_ *ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);
    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);
    vec4 s0 = floor(b0)*2.0 + 1.0;
    vec4 s1 = floor(b1)*2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));
    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
    vec3 p0 = vec3(a0.xy, h.x);
    vec3 p1 = vec3(a0.zw, h.y);
    vec3 p2 = vec3(a1.xy, h.z);
    vec3 p3 = vec3(a1.zw, h.w);
    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
    p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
  }

  void main() {
    vNormal = normalize(normalMatrix * normal);
    vPosition = position;

    float n1 = snoise(position * 1.8 + uTime * 0.25);
    float n2 = snoise(position * 3.5 - uTime * 0.18);
    float n3 = snoise(position * 6.0 + uTime * 0.4);

    float displacement = n1 * 0.28 + n2 * 0.14 + n3 * 0.06;
    displacement += uPulse * 0.12 * sin(uTime * 3.0);
    vDisplacement = displacement;

    vec3 newPos = position + normal * displacement;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(newPos, 1.0);
  }
`;

const fragmentShader = `
  uniform float uTime;
  uniform float uPulse;
  varying vec3 vNormal;
  varying vec3 vPosition;
  varying float vDisplacement;

  void main() {
    vec3 viewDir = normalize(cameraPosition - vPosition);
    float rim = 1.0 - max(dot(viewDir, vNormal), 0.0);
    rim = pow(rim, 2.2);

    // Core deep color: midnight navy
    vec3 coreColor = vec3(0.01, 0.02, 0.08);
    // Rim: electric cyan-violet
    vec3 rimColor = mix(
      vec3(0.28, 0.68, 1.0),  // cyan-blue
      vec3(0.55, 0.25, 1.0),  // violet
      sin(vDisplacement * 8.0 + uTime * 0.8) * 0.5 + 0.5
    );

    // Displacement-driven luminance hotspots
    float hotspot = smoothstep(0.1, 0.4, vDisplacement);
    vec3 hotColor = vec3(0.6, 0.9, 1.0);

    vec3 finalColor = coreColor;
    finalColor = mix(finalColor, rimColor, rim * 0.9);
    finalColor = mix(finalColor, hotColor, hotspot * 0.4);
    finalColor += uPulse * 0.08 * vec3(0.3, 0.7, 1.0);

    float alpha = 0.88 + rim * 0.12;
    gl_FragColor = vec4(finalColor, alpha);
  }
`;

export default function NeuralCore({ pulse = 0 }) {
  const meshRef = useRef();
  const uniforms = useMemo(() => ({
    uTime:  { value: 0 },
    uPulse: { value: 0 },
  }), []);

  useFrame(({ clock }) => {
    uniforms.uTime.value  = clock.elapsedTime;
    uniforms.uPulse.value = pulse;
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.0015;
      meshRef.current.rotation.x += 0.0008;
    }
  });

  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[1.85, 64]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        transparent
        side={THREE.FrontSide}
      />
    </mesh>
  );
}
