//Three Vars
import * as THREE from 'https://unpkg.com/three/build/three.module.js';
import {VRButton} from 'https://threejsfundamentals.org/threejs/resources/threejs/r122/examples/jsm/webxr/VRButton.js';

const renderer = new THREE.WebGLRenderer();

var url = ""

renderer.setSize( window.innerWidth, window.innerHeight );

document.body.appendChild( renderer.domElement );

document.body.appendChild(VRButton.createButton(renderer));

var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(35, window.innerWidth / window.innerHeight, 0.1, 10000);

var geometry = new THREE.SphereGeometry( -10, 10, 10);

const loader = new THREE.TextureLoader()



camera.position.set(0, 0, 0);

scene.background = new THREE.Color("blue");
renderer.xr.enabled = true;

renderer.setPixelRatio(window.devicePixelRatio);
//Websocket Vars

var target_fps = 24;

var request_start_time = performance.now();
var start_time = performance.now();
var time = 0;
var request_time = 0;
var time_smoothing = 0.9; // larger=more smoothing
var request_time_smoothing = 0.2; // larger=more smoothing
var target_time = 1000 / target_fps;


var wsProtocol = (location.protocol === "https:") ? "wss://" : "ws://";

var path = location.pathname;
if(path.endsWith("index.html"))
{
    path = path.substring(0, path.length - "index.html".length);
}
if(!path.endsWith("/")) {
    path = path + "/";
}
var ws = new WebSocket(wsProtocol + location.host + path + "websocket");
ws.binaryType = 'arraybuffer';

function requestImage() {
    request_start_time = performance.now();
    ws.send('more');
}

ws.onopen = function() {
    console.log("connection was established");
    start_time = performance.now();
    requestImage();
};

ws.onmessage = function(evt) {
    var arrayBuffer = evt.data;
    var blob  = new Blob([new Uint8Array(arrayBuffer)], {type: "image/jpeg"});
    

    var end_time = performance.now();
    var current_time = end_time - start_time;
    // smooth with moving average
    time = (time * time_smoothing) + (current_time * (1.0 - time_smoothing));
    start_time = end_time;
    var fps = Math.round(1000 / time);
    
    var current_request_time = performance.now() - request_start_time;
    // smooth with moving average
    request_time = (request_time * request_time_smoothing) + (current_request_time * (1.0 - request_time_smoothing));
    var timeout = Math.max(0, target_time - request_time);

    setTimeout(requestImage, timeout);
    url = window.URL.createObjectURL(blob)
    var texture = loader.load( url );
    var material = new THREE.MeshBasicMaterial( { map: texture } );
    var mesh = new THREE.Mesh(geometry, material);
    mesh.material = material;
    scene.add(mesh);  
    //window.URL.revokeObjectURL(url)


};
renderer.setAnimationLoop(function () {
   
    renderer.render(scene, camera);
});