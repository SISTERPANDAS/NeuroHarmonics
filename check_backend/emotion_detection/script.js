// =============================
// THREE JS GALAXY BACKGROUND
// =============================

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
75,
window.innerWidth / window.innerHeight,
0.1,
1000
);

const renderer = new THREE.WebGLRenderer({
canvas: document.getElementById('bg'),
alpha:true
});

renderer.setSize(window.innerWidth, window.innerHeight);
camera.position.z = 5;

// STAR FIELD
const starsGeometry = new THREE.BufferGeometry();
const starVertices = [];

for (let i = 0; i < 6000; i++) {
    starVertices.push(
        (Math.random()-0.5)*2000,
        (Math.random()-0.5)*2000,
        (Math.random()-0.5)*2000
    );
}

starsGeometry.setAttribute(
'position',
new THREE.Float32BufferAttribute(starVertices,3)
);

const starsMaterial = new THREE.PointsMaterial({
color: 0x00eaff,
size: 0.7
});

const starField = new THREE.Points(starsGeometry, starsMaterial);
scene.add(starField);

// ANIMATE GALAXY
function animate(){
    requestAnimationFrame(animate);

    starField.rotation.x += 0.0005;
    starField.rotation.y += 0.001;

    renderer.render(scene,camera);
}
animate();

// RESIZE
window.addEventListener('resize',()=>{
    renderer.setSize(window.innerWidth,window.innerHeight);
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
});


// =============================
// WEBCAM + EMOTION DETECTION
// =============================

const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('captureBtn');
const resultDiv = document.getElementById('result');

// START CAMERA
navigator.mediaDevices.getUserMedia({ video:true })
.then(stream=>{
    video.srcObject = stream;
})
.catch(err=>{
    resultDiv.textContent = 'Camera Error: '+err;
});

// CAPTURE IMAGE
captureBtn.addEventListener('click',()=>{

    canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);

    const imageData = canvas.toDataURL('image/png');

    resultDiv.textContent = "Analyzing emotion...";

    fetch('/predict',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({image:imageData})
    })
    .then(res=>res.json())
    .then(data=>{
        resultDiv.textContent = "🌌 Detected Emotion: "+data.emotion;
    })
    .catch(err=>{
        resultDiv.textContent = "Error: "+err;
    });

});