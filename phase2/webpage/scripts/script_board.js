// global var.
let latest = 0

// functions
function newElementWithClass(label, className="", textContent="", children=[]){
    let ret = document.createElement(label);
    
    if(className != ""){
        ret.classList.add(className);
    }

    if(textContent != ""){
        ret.textContent = textContent;
    }

    if(children != []){
        for(let i = 0; i < children.length; i++){
            ret.appendChild(children[i]);
        }
    }

    return ret;
}

function appendPost(author, time, content) {
    let message = newElementWithClass("div", "message", "", [
        newElementWithClass("div", "metadata", "", [
            newElementWithClass("span", "","作者："),
            newElementWithClass("span", "author", author),
            newElementWithClass("span", "","時間："),
            newElementWithClass("span", "pub_time", time)
        ]),
        newElementWithClass("div", "article", "", [
            newElementWithClass("span", "content", content)
        ])
    ]);

    document.getElementById("bulletin").appendChild(message)    
}

function renewBulletin(){
    // fetch new posts
    fetch("https://localhost:51966", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "act": "renew",
            "latest": String(latest)
        })
   }).then(response => {
        return response.json();
   }).then(data => {
        for(let i = 0; i < data.length; i++){
            appendPost(data[i]["author"], data[i]["time"], data[i]["content"]);
        }

        latest += data.length;

        if(document.getElementById("board_empty") != null && latest > 0){
            document.getElementById("board_empty").remove();
        }
   })
}

// main

// always renew for the 1st time
renewBulletin();