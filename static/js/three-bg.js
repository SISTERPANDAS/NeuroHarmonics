// Subtle three.js background used on all pages
(function(){
  try {
    const canvas = document.getElementById('three-bg');
    if (!canvas) return;

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 4;

    // Particles group
    const group = new THREE.Group();
    scene.add(group);

    const geom = new THREE.SphereGeometry(0.06, 8, 8);
    const baseColor = 0xa855f7; // purple-ish

    for (let i = 0; i < 40; i++) {
      const mat = new THREE.MeshBasicMaterial({ color: baseColor, transparent: true, opacity: 0.06 });
      const m = new THREE.Mesh(geom, mat);
      m.position.x = (Math.random() - 0.5) * 10;
      m.position.y = (Math.random() - 0.5) * 6;
      m.position.z = (Math.random() - 0.5) * 6;
      m.scale.setScalar(Math.random() * 1.5 + 0.5);
      group.add(m);
    }

    function onResize(){
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
    }

    window.addEventListener('resize', onResize);

    // animate
    let t = 0;
    function animate(){
      t += 0.002;
      group.rotation.y = t * 0.5;
      group.children.forEach((child, idx) => {
        child.position.y += Math.sin(t * (0.5 + idx * 0.01)) * 0.002;
      });
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }

    // style canvas to sit behind content
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.zIndex = '-1';
    canvas.style.pointerEvents = 'none';

    animate();
  } catch (e) {
    console.warn('three-bg failed', e);
  }
})();
