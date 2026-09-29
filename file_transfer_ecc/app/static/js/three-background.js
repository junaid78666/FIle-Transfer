/**
 * app/static/js/three-background.js — Interactive Three.js Cryptographic Visualizer
 * =================================================================================
 * Renders:
 * 1. Hero Ambient Background: Floating NIST P-256 Cryptographic Lattice & Nodes
 * 2. Interactive 3D Curve Visualizer: 3D Elliptic Curve Point Addition & ECDH Geometry
 */

document.addEventListener('DOMContentLoaded', () => {
  if (typeof THREE === 'undefined') {
    console.warn('[ThreeJS] THREE library not loaded. Visualizer fallback active.');
    return;
  }

  initInteractiveCurveExplorer();
});

/**
 * 1. Hero Ambient Background (delegated to GSAP hero-gsap.js)
 */
function initHeroBackground() {
  // GSAP engine active in hero-gsap.js
}

/**
 * 2. Interactive 3D Elliptic Curve Visualizer
 * Real-time 3D model of Weierstrass curve point addition (P + Q = R)
 */
function initInteractiveCurveExplorer() {
  const container = document.getElementById('interactive-curve-container');
  if (!container) return;

  const width = container.clientWidth || 700;
  const height = container.clientHeight || 380;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0B1329);

  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  camera.position.set(0, 8, 38);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  // Curve Group
  const curveGroup = new THREE.Group();
  scene.add(curveGroup);

  // Generate 3D Elliptic Curve: y^2 = x^3 - 3x + 5 in 3D
  const curvePointsLeft = [];
  const curvePointsRight = [];

  for (let x = -2.2; x <= 4.5; x += 0.06) {
    const rhs = Math.pow(x, 3) - 3 * x + 5;
    if (rhs >= 0) {
      const y = Math.sqrt(rhs);
      curvePointsRight.push(new THREE.Vector3(x * 3.5, y * 2.4, 0));
      curvePointsLeft.push(new THREE.Vector3(x * 3.5, -y * 2.4, 0));
    }
  }

  const matRed = new THREE.LineBasicMaterial({ color: 0xE5322D, linewidth: 2 });
  const matCyan = new THREE.LineBasicMaterial({ color: 0x38BDF8, linewidth: 2 });

  if (curvePointsRight.length > 1) {
    const geoR = new THREE.BufferGeometry().setFromPoints(curvePointsRight);
    const lineR = new THREE.Line(geoR, matRed);
    curveGroup.add(lineR);
  }

  if (curvePointsLeft.length > 1) {
    const geoL = new THREE.BufferGeometry().setFromPoints(curvePointsLeft);
    const lineL = new THREE.Line(geoL, matCyan);
    curveGroup.add(lineL);
  }

  // Add 3D Spheres for P (Alice), Q (Bob), and R (ECDH Shared Point)
  function createPointNode(x, y, z, color, labelText) {
    const sphereGeo = new THREE.SphereGeometry(0.7, 16, 16);
    const sphereMat = new THREE.MeshBasicMaterial({ color });
    const mesh = new THREE.Mesh(sphereGeo, sphereMat);
    mesh.position.set(x, y, z);
    curveGroup.add(mesh);
    return mesh;
  }

  // Key nodes on curve
  createPointNode(3.5, 4.8, 0, 0xE5322D, 'P (Alice)');
  createPointNode(7.0, 8.2, 0, 0x38BDF8, 'Q (Bob)');
  createPointNode(10.5, -11.2, 0, 0x10B981, 'R = P + Q (Shared Secret)');

  // Secant Line connecting P and Q extending to -R
  const secantGeo = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 1.4, 0),
    new THREE.Vector3(14, 15.2, 0),
  ]);
  const secantMat = new THREE.LineDashedMaterial({
    color: 0xF59E0B,
    dashSize: 0.8,
    gapSize: 0.4,
  });
  const secantLine = new THREE.Line(secantGeo, secantMat);
  secantLine.computeLineDistances();
  curveGroup.add(secantLine);

  // Reflection line down to R
  const reflectGeo = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(10.5, 11.2, 0),
    new THREE.Vector3(10.5, -11.2, 0),
  ]);
  const reflectMat = new THREE.LineDashedMaterial({
    color: 0x10B981,
    dashSize: 0.6,
    gapSize: 0.3,
  });
  const reflectLine = new THREE.Line(reflectGeo, reflectMat);
  reflectLine.computeLineDistances();
  curveGroup.add(reflectLine);

  // Coordinate Grid Helper
  const gridHelper = new THREE.GridHelper(34, 17, 0x334155, 0x1E293B);
  gridHelper.rotation.x = Math.PI / 2;
  curveGroup.add(gridHelper);

  // Orbit controls via mouse drag
  let isDragging = false;
  let previousMousePosition = { x: 0, y: 0 };

  container.addEventListener('mousedown', (e) => {
    isDragging = true;
    previousMousePosition = { x: e.clientX, y: e.clientY };
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });

  container.addEventListener('mousemove', (e) => {
    if (!isDragging) return;

    const deltaX = e.clientX - previousMousePosition.x;
    const deltaY = e.clientY - previousMousePosition.y;

    curveGroup.rotation.y += deltaX * 0.008;
    curveGroup.rotation.x += deltaY * 0.008;

    previousMousePosition = { x: e.clientX, y: e.clientY };
  });

  // Responsive Resize
  window.addEventListener('resize', () => {
    const newWidth = container.clientWidth || 700;
    const newHeight = container.clientHeight || 380;
    camera.aspect = newWidth / newHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(newWidth, newHeight);
  });

  // Animation Loop
  function animate() {
    requestAnimationFrame(animate);

    if (!isDragging) {
      curveGroup.rotation.y += 0.004;
    }

    renderer.render(scene, camera);
  }

  animate();
}
