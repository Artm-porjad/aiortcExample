var pc = null;

function negotiate(pc, send_offer) {
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
        if (send_offer){
            var offer = pc.localDescription;
            return fetch('/sub', {
                body: JSON.stringify({
                    sdp: send_offer,
                    type: offer.type,
                }),
                headers: {
                    'Content-Type': 'application/json'
                },
                method: 'POST'
            });
        } else{
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
        }

    }).then(function(response) {
        return response.json();
    }).then(function(answer) {
        return pc.setRemoteDescription(answer);
    }).catch(function(e) {
        alert(e);
    });
}

function publish() {
    fetch('/publish').then((resp) => {
        if (resp.status === 200) {
            console.log("accepted")
        } else {
            console.log(resp.status);
        }
    });
}

function start() {
    var config = {
        sdpSemantics: 'unified-plan'
    };

    if (document.getElementById('use-stun').checked) {
        config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];
    }

    pc1 = new RTCPeerConnection(config);

    // connect audio / video
    pc1.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
        } else {
            document.getElementById('audio').srcObject = evt.streams[0];
        }
    });

    document.getElementById('start').style.display = 'none';
    negotiate(pc1);
    publish();
    document.getElementById('stop').style.display = 'inline-block';
}

function connecting() {
    var config = {
        sdpSemantics: 'unified-plan'
    };

    if (document.getElementById('use-stun').checked) {
        config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];
    }

    pc2 = new RTCPeerConnection(config);

    // connect audio / video
    pc2.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video') {
            document.getElementById('video1').srcObject = evt.streams[0];
        } else {
            document.getElementById('audio1').srcObject = evt.streams[0];
        }
    });
    messageInputBox = document.getElementById('offer');
    var message = messageInputBox.value;

    negotiate(pc2, message);
}


function stop() {
    document.getElementById('stop').style.display = 'none';

    // close peer connection
    setTimeout(function() {
        pc.close();
    }, 500);
}

