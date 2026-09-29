/**
 * app/static/js/hero-gsap.js — GSAP Interactive Hero Background Animation Engine
 * ==============================================================================
 * Powers:
 * 1. Ambient Cryptographic Glow Orbs (Dynamic organic floating via GSAP timelines)
 * 2. Weierstrass Elliptic Curve Data Streams (Continuous dashed offset flowing)
 * 3. Cryptographic Node Pulses (Radar expansions on P, Q, and Shared Secret R)
 * 4. Floating Parallax Chips (Multi-layered 3D depth reaction to cursor)
 * 5. Staggered Hero Entrance Orchestration
 */

document.addEventListener('DOMContentLoaded', () => {
  if (typeof gsap === 'undefined') {
    console.warn('[GSAP] Library not detected. Skipping hero GSAP initialization.');
    return;
  }

  const heroSection = document.getElementById('hero-section');
  const heroBg = document.getElementById('hero-gsap-bg');
  if (!heroSection || !heroBg) return;

  initHeroEntrance();
  initAmbientFloatingLoops();
  initCurveDataFlow();
  initNodePulses();
  initParallaxInteraction(heroSection);
});

/**
 * 1. Hero Entrance Timeline
 * Orchestrates a smooth, premium entrance for hero elements and background geometry
 */
function initHeroEntrance() {
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

  // Initial states
  gsap.set('.gsap-glow-orb', { scale: 0.5, opacity: 0 });
  gsap.set('.gsap-chip', { y: 25, opacity: 0, scale: 0.85 });
  gsap.set('.gsap-curve', { opacity: 0 });
  gsap.set('.gsap-nodes-group', { opacity: 0, scale: 0.9, transformOrigin: 'center center' });

  tl.to('.gsap-glow-orb', {
    scale: 1,
    opacity: 0.45,
    duration: 1.6,
    stagger: 0.25,
    ease: 'power2.out'
  })
  .to('.gsap-curve', {
    opacity: 1,
    duration: 1.2,
    stagger: 0.2
  }, '-=1.0')
  .to('.gsap-nodes-group', {
    opacity: 1,
    scale: 1,
    duration: 1.0,
    ease: 'back.out(1.4)'
  }, '-=0.8')
  .to('.gsap-chip', {
    y: 0,
    opacity: 1,
    scale: 1,
    duration: 0.9,
    stagger: 0.12,
    ease: 'back.out(1.6)'
  }, '-=0.7');

  // Hero Content Entrance
  const heroBadge = document.querySelector('.hero-badge');
  const heroTitle = document.querySelector('.hero-title');
  const heroDesc = document.querySelector('.hero-description');
  const heroActions = document.querySelectorAll('.hero-actions .btn');

  if (heroBadge) {
    gsap.from(heroBadge, {
      y: -20,
      opacity: 0,
      duration: 0.7,
      ease: 'power3.out',
      delay: 0.2
    });
  }

  if (heroTitle) {
    gsap.from(heroTitle, {
      y: 30,
      opacity: 0,
      duration: 0.85,
      ease: 'power3.out',
      delay: 0.35
    });
  }

  if (heroDesc) {
    gsap.from(heroDesc, {
      y: 20,
      opacity: 0,
      duration: 0.75,
      ease: 'power3.out',
      delay: 0.5
    });
  }

  if (heroActions.length > 0) {
    gsap.from(heroActions, {
      y: 20,
      opacity: 0,
      duration: 0.65,
      stagger: 0.15,
      ease: 'back.out(1.7)',
      delay: 0.65
    });
  }
}

/**
 * 2. Ambient Floating Loops
 * Organic breathing and floating movement for background glow orbs and chips
 */
function initAmbientFloatingLoops() {
  const orbPrimary = document.querySelector('.orb-primary');
  const orbSecondary = document.querySelector('.orb-secondary');
  const orbTertiary = document.querySelector('.orb-tertiary');

  if (orbPrimary) {
    gsap.to(orbPrimary, {
      x: 55,
      y: -35,
      scale: 1.12,
      duration: 7,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut'
    });
  }

  if (orbSecondary) {
    gsap.to(orbSecondary, {
      x: -45,
      y: 40,
      scale: 0.88,
      duration: 8.5,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
      delay: 1
    });
  }

  if (orbTertiary) {
    gsap.to(orbTertiary, {
      x: 35,
      y: 35,
      scale: 1.15,
      duration: 6.5,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
      delay: 0.5
    });
  }

  // Floating chips levitation
  const chips = document.querySelectorAll('.gsap-chip');
  chips.forEach((chip, index) => {
    const randomY = 10 + (index % 3) * 4;
    const randomRot = (index % 2 === 0 ? 1 : -1) * (2 + (index % 3));
    const randomDur = 3.2 + (index * 0.4);

    gsap.to(chip, {
      y: `+=${randomY}`,
      rotation: `+=${randomRot}`,
      duration: randomDur,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
      delay: index * 0.3
    });
  });
}

/**
 * 3. Weierstrass Elliptic Curve Data Streams
 * Animates the strokeDashoffset continuously to simulate packets traversing the curve
 */
function initCurveDataFlow() {
  const curve1 = document.querySelector('.gsap-curve-1');
  const curve2 = document.querySelector('.gsap-curve-2');
  const secant = document.querySelector('.gsap-secant-line');

  if (curve1) {
    gsap.to(curve1, {
      strokeDashoffset: -200,
      duration: 9,
      repeat: -1,
      ease: 'none'
    });
  }

  if (curve2) {
    gsap.to(curve2, {
      strokeDashoffset: 180,
      duration: 11,
      repeat: -1,
      ease: 'none'
    });
  }

  if (secant) {
    gsap.to(secant, {
      strokeDashoffset: -120,
      duration: 6,
      repeat: -1,
      ease: 'none'
    });
  }
}

/**
 * 4. Node Pulses
 * Emits radar-like wave rings from cryptographic points P, Q, and Shared Secret R
 */
function initNodePulses() {
  const pulseRings = document.querySelectorAll('.gsap-node-pulse');
  pulseRings.forEach((ring, index) => {
    gsap.to(ring, {
      attr: { r: 32 },
      opacity: 0,
      strokeWidth: 0.5,
      duration: 2.2,
      repeat: -1,
      ease: 'power1.out',
      delay: index * 0.7
    });
  });
}

/**
 * 5. Interactive Parallax & Magnetic Cursor Reactivity
 * Smooth 3D depth tilting and parallax coordinates responding to pointer moves
 */
function initParallaxInteraction(heroSection) {
  const chips = document.querySelectorAll('.gsap-chip');
  const orbs = document.querySelectorAll('.gsap-glow-orb');
  const svg = document.querySelector('.gsap-ecc-svg');

  // Quick smooth setters for high performance 60fps tracking
  let mouseX = 0;
  let mouseY = 0;

  heroSection.addEventListener('mousemove', (e) => {
    const rect = heroSection.getBoundingClientRect();
    const nx = ((e.clientX - rect.left) / rect.width - 0.5) * 2; // -1 to 1
    const ny = ((e.clientY - rect.top) / rect.height - 0.5) * 2; // -1 to 1

    mouseX = nx;
    mouseY = ny;

    // Parallax floating chips based on depth data attribute
    chips.forEach((chip) => {
      const depth = parseFloat(chip.getAttribute('data-depth')) || 0.05;
      gsap.to(chip, {
        x: mouseX * depth * 350,
        y: mouseY * depth * 350,
        duration: 1.4,
        ease: 'power2.out',
        overwrite: 'auto'
      });
    });

    // Parallax ambient glow orbs
    orbs.forEach((orb, i) => {
      const factor = (i + 1) * 18;
      gsap.to(orb, {
        x: mouseX * factor,
        y: mouseY * factor,
        duration: 2.2,
        ease: 'power1.out',
        overwrite: 'auto'
      });
    });

    // 3D perspective tilt on SVG curve plane
    if (svg) {
      gsap.to(svg, {
        rotationY: mouseX * 8,
        rotationX: -mouseY * 8,
        transformPerspective: 1000,
        transformOrigin: '50% 50%',
        duration: 1.8,
        ease: 'power2.out',
        overwrite: 'auto'
      });
    }
  });

  // Smooth return to center when cursor leaves the hero section
  heroSection.addEventListener('mouseleave', () => {
    chips.forEach((chip) => {
      gsap.to(chip, {
        x: 0,
        y: 0,
        duration: 2.0,
        ease: 'power2.out',
        overwrite: 'auto'
      });
    });

    orbs.forEach((orb) => {
      gsap.to(orb, {
        x: 0,
        y: 0,
        duration: 2.5,
        ease: 'power2.out',
        overwrite: 'auto'
      });
    });

    if (svg) {
      gsap.to(svg, {
        rotationY: 0,
        rotationX: 0,
        duration: 2.0,
        ease: 'power2.out',
        overwrite: 'auto'
      });
    }
  });
}
