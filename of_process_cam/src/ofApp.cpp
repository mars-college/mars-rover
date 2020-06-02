#include "ofApp.h"

//--------------------------------------------------------------
void ofApp::setup(){
    
    // code based on https://forum.openframeworks.cc/t/convert-dual-fisheye-video-to-equirectangular-with/24182
    
    camWidth = 1920;
    camHeight = 1080;
    
    ofSetWindowShape(1600, 900);

    ofDisableArbTex(); // important
    
    // find cam
    devices = theta.listDevices();
    bool isDeviceConnected = false;
    for(int i = 0; i < devices.size(); i++){
        if(devices[i].deviceName == "RICOH THETA S"){
            theta.setDeviceID(devices[i].id);
            isDeviceConnected = true;
            ofLog() << i << ": " << devices[i].deviceName << endl;
        }
    }
    if(!isDeviceConnected){
        ofLog(OF_LOG_ERROR, "RICOH THETA S is not found.");
    }
    
    // setup sphere
    sphere = ofSpherePrimitive(camHeight, 64).getMesh();
    for(int i=0;i<sphere.getNumTexCoords();i++){
        sphere.setTexCoord(i, ofVec2f(1.0) - sphere.getTexCoord(i));
    }
    for(int i=0;i<sphere.getNumNormals();i++){
        sphere.setNormal(i, sphere.getNormal(i) * ofVec3f(-1));
    }
    
    // GUI
    offset.set("uvOffset", ofVec4f(0,0.0,0,0.0), ofVec4f(-0.1), ofVec4f(0.1));
    radius.set("radius", 0.445, 0.0, 1.0);
    showSphere.set("showSphere", false);
    thetaParams.add(offset);
    thetaParams.add(radius);
    gui.setup(thetaParams);
    gui.setName("360 streamer");
    gui.add(showSphere);
    
    
    // SETUP ASSETS
    theta.initGrabber(camWidth, camHeight);
    shader.load("shadersGL2/equirectanguler.vert",
                "shadersGL2/equirectanguler.frag");
    fbo.allocate(camWidth, camHeight);
}

//--------------------------------------------------------------
void ofApp::update(){
    theta.update();
    
    if (theta.isFrameNew()) {
        fbo.begin();
        ofClear(0);
        shader.begin();
        shader.setUniformTexture("mainTex", theta.getTexture(), 0);
        shader.setUniforms(thetaParams);
        theta.draw(0, 0, camWidth, camHeight);
        shader.end();
        fbo.end();
    }

}

//--------------------------------------------------------------
void ofApp::draw(){
    ofBackground(0);
    
    if (showSphere) {
        ofEnableDepthTest();
        cam.begin();
        fbo.getTexture().bind();
        sphere.draw();
        fbo.getTexture().unbind();
        cam.end();
    }
    else {
        fbo.draw(175, 20, 1280, 720);
    }
    
    ofDisableDepthTest();

    gui.draw();
}

//--------------------------------------------------------------
void ofApp::keyPressed(int key){

}

//--------------------------------------------------------------
void ofApp::keyReleased(int key){

}

//--------------------------------------------------------------
void ofApp::mouseMoved(int x, int y ){

}

//--------------------------------------------------------------
void ofApp::mouseDragged(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mousePressed(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mouseReleased(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mouseEntered(int x, int y){

}

//--------------------------------------------------------------
void ofApp::mouseExited(int x, int y){

}

//--------------------------------------------------------------
void ofApp::windowResized(int w, int h){

}

//--------------------------------------------------------------
void ofApp::gotMessage(ofMessage msg){

}

//--------------------------------------------------------------
void ofApp::dragEvent(ofDragInfo dragInfo){ 

}
