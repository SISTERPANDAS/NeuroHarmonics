/**
 * Three.js – Slowly rotating neural network sphere (background only).
 * Nodes and edges form a 3D sphere; all content styling is done with CSS.
 */
(function () {
  "use strict";
  var canvas = document.getElementById("three-neural-sphere");
  if (!canvas) return;

  var scene, camera, renderer, sphereGroup;
  var clock = { start: Date.now() };

  function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 4.2;
    renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);

    var geometry = new THREE.IcosahedronGeometry(1.2, 2);
    var positions = geometry.attributes.position;
    var nodeCount = positions.count;
    var maxDist = 0.45;
    var edgePositions = [];
    for (var i = 0; i < nodeCount; i++) {
      var ax = positions.getX(i), ay = positions.getY(i), az = positions.getZ(i);
      for (var j = i + 1; j < nodeCount; j++) {
        var bx = positions.getX(j), by = positions.getY(j), bz = positions.getZ(j);
        var dx = ax - bx, dy = ay - by, dz = az - bz;
        if (Math.sqrt(dx * dx + dy * dy + dz * dz) < maxDist) {
          edgePositions.push(ax, ay, az, bx, by, bz);
        }
      }
    }

    var edgeGeometry = new THREE.BufferGeometry();
    edgeGeometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array(edgePositions), 3));
    var lineMaterial = new THREE.LineBasicMaterial({
      color: 0x5eead4,
      transparent: true,
      opacity: 0.22,
    });
    var lines = new THREE.LineSegments(edgeGeometry, lineMaterial);

    var nodeMaterial = new THREE.PointsMaterial({
      color: 0x9d4edd,
      size: 0.028,
      transparent: true,
      opacity: 0.9,
      sizeAttenuation: true,
    });
    var points = new THREE.Points(geometry.clone(), nodeMaterial);

    sphereGroup = new THREE.Group();
    sphereGroup.add(lines);
    sphereGroup.add(points);
    scene.add(sphereGroup);

    window.addEventListener("resize", onResize);
    animate();
  }

  function onResize() {
    if (!camera || !renderer) return;
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  function animate() {
    requestAnimationFrame(animate);
    if (!renderer || !scene || !camera) return;
    var t = (Date.now() - clock.start) * 0.00012;
    sphereGroup.rotation.y = t;
    sphereGroup.rotation.x = Math.sin(t * 0.7) * 0.1;
    renderer.render(scene, camera);
  }

  if (typeof THREE !== "undefined") {
    init();
  } else {
    var s = document.createElement("script");
    s.src = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js";
    s.onload = init;
    document.head.appendChild(s);
  }
})();
