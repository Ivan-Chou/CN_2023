// reference: https://www.youtube.com/watch?v=DvlyzDZDEq4
// global var.
const sock = io.connect("http://localhost:51967")

const call_area = document.getElementById("call_area") || areas[2]
const roomSelection = call_area.querySelector("#roomSelection")
const cameraDisplay = call_area.querySelector("#cameraDisplay")

const peer_self = new Peer(getUserName())

const camera_self = createUserCam(peer_self.id)
camera_self.querySelector(".camera").muted = true
const stream_self = new MediaStream();

const peer_conns = {} // media connection from others
const peer_cams = {} // user_cam elements from others

let cam_on = true; // whether camera of this client is operating

let currRoomID = "" // the room ID of current room

// functions
function setCameraOff(user_cam){
    // set camera height to 0
    user_cam.querySelector(".camera").style.height = "0px"
    
    // set alternative text to "visible" 
    user_cam.querySelector(".NoImg").style.display = "flex"
}

function setCameraOn(user_cam){
    // similar to setCameraOff, just set the height back
    user_cam.querySelector(".camera").style.height = "90%"
    
    user_cam.querySelector(".NoImg").style.display = "none"
}

function createUserCam(userID){
    // newElementWithClass(label, className="", textContent="", children=[])

    let camera = newElementWithClass("div", "user_cam", "", [
        newElementWithClass("video", "camera", "", []),
        newElementWithClass("div", "NoImg", "無畫面", []),
        newElementWithClass("span", "username_of_cam", userID, [])
    ])

    return camera;
}

function addVideoStream(user_cam, stream) {
    // append media stream to the video element in user_cam element
    let video = user_cam.querySelector(".camera")
    
    video.srcObject = stream

    video.addEventListener("loadedmetadata", () => {
        video.play()
    })
}

function bindUserCam(userID, conn){
    // bind the connection & camera HTML element to corresponding userID
    
    // if others have sent their camera status
    let other_cam_stat = ""

    if(peer_cams.hasOwnProperty(userID)){
        // no video is coming => set camera to "off"
        other_cam_stat = peer_cams[userID]
    }
    
    peer_cams[userID] = createUserCam(userID);
    
    if(other_cam_stat != ""){
        if(other_cam_stat == "on"){
            setCameraOn(peer_cams[userID])
        }
        else if(other_cam_stat == "off"){
            setCameraOff(peer_cams[userID])
        }
        else{
            console.log(`ERR: other_cam_stat neither "on" nor "off": ${other_cam_stat}`)
        }
    }

    conn.on("stream", vidStream => {
        console.log(`Now stream from ${userID}`)

        addVideoStream(peer_cams[userID], vidStream)

        if(other_cam_stat == ""){
            setCameraOn(peer_cams[userID])
        }
    })

    cameraDisplay.querySelector("#camera_hook").appendChild(peer_cams[userID])

    // console.log("emit ready, time = " + Date.now())

    // for connectToNewUser(), there is a gap between .call() and .on("stream"). if answer arrive at middle => lost
    sock.emit("ready", JSON.stringify({
        "roomID": currRoomID,
        "receiver": peer_self.id,
        "sender": userID
    }))
}

function connectToNewUser(userID) {
    peer_conns[userID] = peer_self.call(userID, stream_self)

    console.log("(connectToNewUser) in peer_conns: " + peer_conns.hasOwnProperty(userID))

    bindUserCam(userID, peer_conns[userID])

    sock.emit((cam_on ? "cam_on" : "cam_off"), JSON.stringify({
        "userID" : peer_self.id,
        "roomID" : currRoomID
    }))
}

function genRoomId(){
    let ret = ["", "", ""]

    for(let i = 0; i < 3; i++){
        for(let j = 0; j < 3; j++){
            ret[i] += String.fromCharCode( Math.floor(26 * Math.random() + "a".charCodeAt(0)) )
        }
    }

    return ret.join("-")
}

function setCamera(roomID){
    navigator.mediaDevices.getUserMedia({
        video: true, // can set false for phone
        audio: true
    }).then(stream => {
        for(let i = 0; i < stream.getVideoTracks().length; i++){
            stream_self.addTrack(stream.getVideoTracks()[i])
        }
        for(let i = 0; i < stream.getAudioTracks().length; i++){
            stream_self.addTrack(stream.getAudioTracks()[i])
        }

        addVideoStream(camera_self, stream_self)

        cameraDisplay.querySelector("#camera_hook").appendChild(camera_self)

        if(stream_self.getVideoTracks().length == 0){
            setCameraOff(camera_self)
            cam_on = false
        }
        else{
            setCameraOn(camera_self)
            cam_on = true
        }

        // wait after stream_self settled
        sock.emit("join_room", JSON.stringify({
            "roomID": roomID,
            "userID": userID // should be username
        }))
    }).catch(err => {
        console.log(err);
    })

    userID = peer_self.id

    roomSelection.remove()
    call_area.appendChild(cameraDisplay)

    cameraDisplay.querySelector("#roomID").textContent = roomID;
}

// binding
sock.on("user_disconnected", userID => {
    if (peer_conns.hasOwnProperty(userID)){ 
        peer_conns[userID].close()
        delete peer_conns[userID]
    }

    if(peer_cams.hasOwnProperty(userID)){
        peer_cams[userID].remove()
        delete peer_cams[userID]
    }
})

sock.on("other_cam_off", userID => {
    console.log(`peer: ${userID} camera off`)
    
    if(peer_cams.hasOwnProperty(userID)){
        setCameraOff(peer_cams[userID])
    }
    else{
        peer_cams[userID] = "off"
    }
})

sock.on("other_cam_on", userID => {
    console.log(`peer: ${userID} camera on`)
    
    if(peer_cams.hasOwnProperty(userID)){
        setCameraOn(peer_cams[userID])
    }
    else{
        peer_cams[userID] = "on"
    }
})

sock.on("user_connected", userID => {
    console.log(`connected by ${userID}`)
    connectToNewUser(userID)
})

sock.on("receiver_ready", data => {
    if(data["sender"] == peer_self.id){
        console.log("receiver : " + data["receiver"])

        if(peer_conns.hasOwnProperty(data["receiver"])){
            // console.log("is in, time = " + Date.now())
            peer_conns[ data["receiver"] ].answer(stream_self)
        }
        else{
            peer_conns[ data["receiver"] ] = "receiver_ready"
        }
    }
})

peer_self.on("call", caller_conn => {
    // caller_conn.answer(stream_self)
    if(peer_conns[caller_conn.peer] == "receiver_ready"){
        // console.log("answer after call & ready, time = " + Date.now())
        caller_conn.answer(stream_self)
    }

    peer_conns[caller_conn.peer] = caller_conn

    bindUserCam(caller_conn.peer, caller_conn)
})

call_area.querySelector("#btn_create").addEventListener("click", () => {
    currRoomID = genRoomId()
    setCamera(currRoomID)
})

call_area.querySelector("#btn_join").addEventListener("click", () => {
    currRoomID = roomSelection.querySelector("#join_roomID").value;
    
    if(currRoomID != ""){
        setCamera(currRoomID)
    }
    else{
        alert("房號不能為空！！")
    }
})

cameraDisplay.querySelector("#camera_on").addEventListener("click", () => {
    if(cam_on){
        // notify others
        sock.emit("cam_off", JSON.stringify({
            "userID" : peer_self.id,
            "roomID" : currRoomID
        }))

        // close self camera
        setCameraOff(camera_self)

        // disable & clean the track
        let videoTracksLength = stream_self.getVideoTracks().length
        for(let i = 0; i < videoTracksLength; i++){
            stream_self.getVideoTracks()[i].stop()
        }
        // change text
        cameraDisplay.querySelector("#camera_on").textContent = "開啟鏡頭"

        cam_on = false;
    }
    else{
        // get new stream
        navigator.mediaDevices.getUserMedia({
            "video" : true
        }).then(stream => {
            let videoTracksLength = stream_self.getVideoTracks().length
            for(let i = 0; i < videoTracksLength; i++){
                // note that we always remove [0] so as to prevent the issue of removing and increasing index at the same time
                // also, we remove tracks at here instead of together with stop() for the need of "auto establishing channel"
                stream_self.removeTrack(stream_self.getVideoTracks()[0])
            }

            for(let i = 0; i < stream.getVideoTracks().length; i++){
                stream_self.addTrack(stream.getVideoTracks()[i])
            }

            // replace senders
            for (const conn of Object.values(peer_conns)){
                // getSenders: [0] -> audio, [1] -> video
                // we assume that user only have 1 camera input at a time, so always replace with videoTracks[0]
                conn.peerConnection.getSenders()[1].replaceTrack(stream_self.getVideoTracks()[0])
            }
        })

        // open self camera
        setCameraOn(camera_self)

        // last, notify others
        sock.emit("cam_on", JSON.stringify({
            "userID" : peer_self.id,
            "roomID" : currRoomID
        }))

        // then set text content
        cameraDisplay.querySelector("#camera_on").textContent = "關閉鏡頭"

        cam_on = true
    }
})

// main
// at first => only roomSelection
cameraDisplay.remove()