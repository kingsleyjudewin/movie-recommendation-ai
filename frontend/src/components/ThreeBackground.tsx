import { useRef, useMemo, Suspense, useEffect, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import * as THREE from "three";

function useMouseParallax() {
  const [mouse, setMouse] = useState({ x: 0, y: 0 });
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      setMouse({
        x: (e.clientX / window.innerWidth - 0.5) * 2,
        y: (e.clientY / window.innerHeight - 0.5) * 2,
      });
    };
    window.addEventListener("mousemove", handler);
    return () => window.removeEventListener("mousemove", handler);
  }, []);
  return mouse;
}

function GlassPlate({ position, rotation, scale, speed }: {
  position: [number, number, number];
  rotation: [number, number, number];
  scale: number;
  speed: number;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const mouse = useMouseParallax();

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const t = clock.getElapsedTime();
    meshRef.current.rotation.x = rotation[0] + Math.sin(t * speed * 0.3) * 0.05 + mouse.y * 0.08;
    meshRef.current.rotation.y = rotation[1] + t * speed * 0.01 + mouse.x * 0.08;
    meshRef.current.rotation.z = rotation[2] + Math.cos(t * speed * 0.2) * 0.03;
    meshRef.current.position.y = position[1] + Math.sin(t * speed * 0.5) * 0.15;
  });

  return (
    <mesh ref={meshRef} position={position} scale={scale}>
      <planeGeometry args={[2.5, 2.5, 1, 1]} />
      <meshStandardMaterial
        color="#2a3245"
        transparent
        opacity={0.12}
        roughness={0.3}
        metalness={0.7}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

function PlayButtonShape() {
  const groupRef = useRef<THREE.Group>(null);
  const mouse = useMouseParallax();

  const triangleGeo = useMemo(() => {
    const shape = new THREE.Shape();
    shape.moveTo(-0.4, -0.5);
    shape.lineTo(-0.4, 0.5);
    shape.lineTo(0.5, 0);
    shape.closePath();
    return new THREE.ShapeGeometry(shape);
  }, []);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    const t = clock.getElapsedTime();
    groupRef.current.rotation.y = Math.sin(t * 0.08) * 0.15 + mouse.x * 0.1;
    groupRef.current.rotation.x = Math.cos(t * 0.06) * 0.08 + mouse.y * 0.1;
    groupRef.current.scale.setScalar(1 + Math.sin(t * 0.4) * 0.02);
  });

  return (
    <group ref={groupRef} position={[0, 0, -3]}>
      {/* Outer ring */}
      <mesh>
        <ringGeometry args={[1.8, 2, 64]} />
        <meshStandardMaterial
          color="#3a4560"
          transparent
          opacity={0.08}
          roughness={0.2}
          metalness={0.8}
          side={THREE.DoubleSide}
        />
      </mesh>
      {/* Inner triangle */}
      <mesh geometry={triangleGeo} position={[0.05, 0, 0.01]}>
        <meshStandardMaterial
          color="#4a5a75"
          transparent
          opacity={0.06}
          roughness={0.3}
          metalness={0.6}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}

function Lights() {
  const mouse = useMouseParallax();
  const lightRef = useRef<THREE.DirectionalLight>(null);

  useFrame(() => {
    if (lightRef.current) {
      lightRef.current.position.x = 5 + mouse.x * 2;
      lightRef.current.position.y = 5 + mouse.y * 1.5;
    }
  });

  return (
    <>
      <ambientLight intensity={0.2} />
      <directionalLight
        ref={lightRef}
        position={[5, 5, 5]}
        intensity={0.35}
        color="#d6c6b8"
      />
      <pointLight position={[-4, -2, 3]} intensity={0.12} color="#8090a0" />
      <pointLight position={[3, 3, -2]} intensity={0.08} color="#d6c6b8" />
    </>
  );
}

export default function ThreeBackground() {
  return (
    <div className="fixed inset-0 z-0">
      <Canvas
        camera={{ position: [0, 0, 5], fov: 45 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true }}
        style={{
          background: "linear-gradient(135deg, #141822, #1b2230, #2a3245)",
        }}
      >
        <Suspense fallback={null}>
          <Lights />
          <PlayButtonShape />
          <Float speed={0.8} rotationIntensity={0.1} floatIntensity={0.3}>
            <GlassPlate position={[-2, 1, -1.5]} rotation={[0.3, 0.5, 0.1]} scale={1.2} speed={0.7} />
          </Float>
          <Float speed={0.6} rotationIntensity={0.1} floatIntensity={0.2}>
            <GlassPlate position={[2.5, -0.5, -2]} rotation={[-0.2, -0.3, 0.2]} scale={1.5} speed={0.5} />
          </Float>
          <Float speed={1} rotationIntensity={0.05} floatIntensity={0.15}>
            <GlassPlate position={[0, -1.5, -2.5]} rotation={[0.1, 0.8, -0.1]} scale={0.9} speed={0.9} />
          </Float>
        </Suspense>
      </Canvas>
    </div>
  );
}
