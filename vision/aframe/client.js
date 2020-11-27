var pc = null;

function negotiate() {
    pc.addTransceiver('video', {direction: 'recvonly'});
    pc.addTransceiver('audio', {direction: 'recvonly'});
    return pc.createOffer().then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        var offer = pc.localDescription;
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function(response) {
        return response.json();
    }).then(function(answer) {
        return pc.setRemoteDescription(answer);
    }).catch(function(e) {
        alert(e);
    });
}

function start_client(use_stun) {
    var config = {
        sdpSemantics: 'unified-plan'
    };
    if (use_stun) {
        config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];
    }
    pc = new RTCPeerConnection(config);

    // connect audio / video
    pc.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video') {
            console.log("received at vid");
            var zzz = evt.streams[0];
            console.log(zzz);
            document.getElementById('video').srcObject = zzz;
        } else {
            console.log("received at aud ");
            var zzz = evt.streams[0];
            console.log(zzz);
            document.getElementById('audio').srcObject = evt.streams[0];
        }
    });

    negotiate();
}

function stop() {
    // close peer connection
    setTimeout(function() {
        pc.close();
    }, 500);
}
