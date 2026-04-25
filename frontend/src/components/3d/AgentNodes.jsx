import { useRef, useMemo, useEffect, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";

const NODE_COUNT = 72;

// Agent labels cycled across the 72 fibonacci-sphere nodes — pulled from
// the catalog names so what users see in the 3D scene matches the
// products they'll interact with once signed in. Kept short; full names
// appear in the hover overlay.
const AGENT_ROLES = [
  "Chief Strategy",    "Marketing Lead",  "Content Creator",    "Social Manager",
  "Lead Research",     "Sales Closer",    "Cold Email Ops",     "Sales Engineer",
  "Full-Stack Eng.",   "Frontend Eng.",   "Backend Eng.",       "DevOps Lead",
  "Designer",          "Brand Designer",  "UX Researcher",      "Motion Designer",
  "Video Producer",    "Image Director",  "Voiceover Artist",   "Podcaster",
  "Analyst",           "Data Scientist",  "Business Intel.",    "Finance Ops",
  "Recruiter",         "People Ops",      "Customer Success",   "Support Agent",
  "Product Manager",   "QA Engineer",     "Security Analyst",   "Legal Advisor",
  "Operations Lead",   "Logistics",       "Supply Chain",       "Inventory",
  "E-commerce Mgr.",   "Retail Ops",      "Account Executive",  "Partnerships",
  "Investor Relations","PR Specialist",   "Copywriter",         "SEO Specialist",
  "Growth Hacker",     "Paid Media",      "Email Marketer",     "Influencer Ops",
  "Community Mgr.",    "Event Producer",  "Training Lead",      "Curriculum Dev.",
  "Translation",       "Localization",    "Research Scientist", "Grant Writer",
  "Bid Specialist",    "Procurement",     "Contract Mgr.",      "Risk Analyst",
  "Compliance",        "Auditor",         "Tax Specialist",     "Treasury",
  "Venture Scout",     "M&A Analyst",     "Due Diligence",      "Strategy Intern",
  "Executive Asst.",   "Scheduler",       "Note-taker",         "Transcriber",
];
const NODE_LABEL = (i) => AGENT_ROLES[i % AGENT_ROLES.length];
const CONNECTION_THRESHOLD = 3.8;

// Fibonacci sphere distribution — perfectly even spacing, not boring random
function fibonacciSphere(count, radius) {
  const points = [];
  const goldenRatio = (1 + Math.sqrt(5)) / 2;
  for (let i = 0; i < count; i++) {
    const theta = Math.acos(1 - (2 * (i + 0.5)) / count);
    const phi   = (2 * Math.PI * i) / goldenRatio;
    const r     = radius * (0.75 + Math.random() * 0.5); // some depth variation
    points.push(new THREE.Vector3(
      r * Math.sin(theta) * Math.cos(phi),
      r * Math.sin(theta) * Math.sin(phi),
      r * Math.cos(theta)
    ));
  }
  return points;
}

// Each node pulses at a slightly different phase — organic breathing.
// Hover: scales up 3×, emissive intensity triples, HTML label appears.
// Click: signals parent to lock this node in focus mode (handled upstream).
function NodeSphere({ position, color, phase, size, label, onSelect }) {
  const ref = useRef();
  const [hovered, setHovered] = useState(false);
  useFrame(({ clock }) => {
    if (!ref.current) return;
    const t = clock.elapsedTime;
    const breathScale = size * (0.85 + 0.15 * Math.sin(t * 1.2 + phase));
    const hoverScale = hovered ? breathScale * 3 : breathScale;
    // Smooth lerp toward target so hover feels tactile, not snappy.
    ref.current.scale.x += (hoverScale - ref.current.scale.x) * 0.25;
    ref.current.scale.y = ref.current.scale.z = ref.current.scale.x;
    ref.current.position.x = position.x + Math.sin(t * 0.3 + phase) * 0.08;
    ref.current.position.y = position.y + Math.cos(t * 0.25 + phase * 1.3) * 0.08;
    ref.current.position.z = position.z + Math.sin(t * 0.2 + phase * 0.7) * 0.08;
  });
  return (
    <group>
      <mesh
        ref={ref}
        position={position}
        onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = "pointer"; }}
        onPointerOut={() => { setHovered(false); document.body.style.cursor = "auto"; }}
        onClick={(e) => { e.stopPropagation(); onSelect && onSelect(label); }}
      >
        <sphereGeometry args={[size, 12, 12]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={hovered ? 3.6 : 1.2}
          roughness={0.1}
          metalness={0.8}
          transparent
          opacity={hovered ? 1 : 0.85}
        />
      </mesh>
      {hovered && (
        <Html
          position={position}
          center
          distanceFactor={8}
          style={{ pointerEvents: "none", userSelect: "none" }}
          occlude={false}
        >
          <div
            style={{
              background: "rgba(3, 7, 18, 0.92)",
              border: "1px solid rgba(79, 209, 197, 0.5)",
              borderRadius: 8,
              padding: "6px 10px",
              color: "#4fd1c5",
              fontFamily: "system-ui, -apple-system, sans-serif",
              fontSize: 11,
              fontWeight: 600,
              whiteSpace: "nowrap",
              backdropFilter: "blur(8px)",
              boxShadow: "0 0 20px rgba(79, 209, 197, 0.4)",
              transform: "translateY(-30px)",
            }}
          >
            {label}
          </div>
        </Html>
      )}
    </group>
  );
}

// Animated data particle flowing along an edge
function DataParticle({ start, end, speed, color }) {
  const ref = useRef();
  useFrame(({ clock }) => {
    if (!ref.current) return;
    const t = ((clock.elapsedTime * speed) % 1.0);
    ref.current.position.lerpVectors(start, end, t);
  });
  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.025, 4, 4]} />
      <meshBasicMaterial color={color} />
    </mesh>
  );
}

export default function AgentNodes({ mouseRef, onSelect }) {
  const groupRef   = useRef();
  const linesRef   = useRef();

  const { positions, colors, phases, sizes } = useMemo(() => {
    const pts = fibonacciSphere(NODE_COUNT, 4.2);
    const cols = pts.map(() => {
      const t = Math.random();
      return t < 0.33
        ? new THREE.Color("#4fd1c5") // teal
        : t < 0.66
        ? new THREE.Color("#7c3aed") // violet
        : new THREE.Color("#2563eb"); // blue
    });
    return {
      positions: pts,
      colors:    cols,
      phases:    pts.map(() => Math.random() * Math.PI * 2),
      sizes:     pts.map(() => 0.045 + Math.random() * 0.065),
    };
  }, []);

  // Build line geometry for all nearby node pairs
  const { linePositions, lineColors, edges } = useMemo(() => {
    const verts = [];
    const cols  = [];
    const edgePairs = [];
    for (let i = 0; i < positions.length; i++) {
      for (let j = i + 1; j < positions.length; j++) {
        const dist = positions[i].distanceTo(positions[j]);
        if (dist < CONNECTION_THRESHOLD) {
          verts.push(positions[i].x, positions[i].y, positions[i].z);
          verts.push(positions[j].x, positions[j].y, positions[j].z);
          const alpha = 1 - dist / CONNECTION_THRESHOLD;
          const c = new THREE.Color().lerpColors(
            new THREE.Color("#1e3a5f"),
            new THREE.Color("#4fd1c5"),
            alpha * 0.7
          );
          cols.push(c.r, c.g, c.b, alpha * 0.35);
          cols.push(c.r, c.g, c.b, alpha * 0.35);
          if (edgePairs.length < 40 && Math.random() < 0.18) {
            edgePairs.push({ start: positions[i].clone(), end: positions[j].clone() });
          }
        }
      }
    }
    return {
      linePositions: new Float32Array(verts),
      lineColors:    new Float32Array(cols),
      edges:         edgePairs,
    };
  }, [positions]);

  // Slow group rotation + subtle mouse lean
  useFrame(({ clock, mouse }) => {
    if (!groupRef.current) return;
    const t = clock.elapsedTime;
    groupRef.current.rotation.y = t * 0.04 + mouse.x * 0.15;
    groupRef.current.rotation.x = mouse.y * -0.1;
  });

  return (
    <group ref={groupRef}>
      {/* Connection lines */}
      <lineSegments ref={linesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            array={linePositions}
            count={linePositions.length / 3}
            itemSize={3}
          />
          <bufferAttribute
            attach="attributes-color"
            array={lineColors}
            count={lineColors.length / 4}
            itemSize={4}
          />
        </bufferGeometry>
        <lineBasicMaterial vertexColors transparent opacity={0.6} />
      </lineSegments>

      {/* Agent nodes — each hoverable + clickable with role label overlay */}
      {positions.map((pos, i) => (
        <NodeSphere
          key={i}
          position={pos}
          color={colors[i]}
          phase={phases[i]}
          size={sizes[i]}
          label={NODE_LABEL(i)}
          onSelect={onSelect}
        />
      ))}

      {/* Data stream particles along edges */}
      {edges.map((edge, i) => (
        <DataParticle
          key={i}
          start={edge.start}
          end={edge.end}
          speed={0.18 + Math.random() * 0.22}
          color={i % 2 === 0 ? "#a0f0e8" : "#a78bfa"}
        />
      ))}
    </group>
  );
}
