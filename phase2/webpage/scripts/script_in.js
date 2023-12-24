// global var.
let userAt = 0; // 0 -> bulletin, 1 -> post_area, 2 -> call_area

const areas = [document.getElementById("bulletin"), document.getElementById("post_area"), document.getElementById("call_area")]

// functions
function changeDisplay(newpos){
    areas[userAt].remove();

    userAt = newpos;

    document.getElementById("display_board").appendChild(areas[userAt]);
}

function getUserName(){
    let cookies = document.cookie.split("; ")

    for(let i = 0; i < cookies.length; i++){
        let pairs = cookies[i].split("=");

        if(pairs[0] == "Coffee"){
            return pairs[1].split("-")[0]
        }
    }
}

// Event Listeners
document.getElementById("logout").addEventListener("click", () => {
    alert("已登出\n將返回未登入頁面");
})

document.getElementById("btn_bulletin").addEventListener("click", () => {
   renewBulletin();

    changeDisplay(0);
})

document.getElementById("btn_message").addEventListener("click", () => {
    // if time enough, set color
    changeDisplay(1);
})

document.getElementById("btn_call").addEventListener("click", () => {
    changeDisplay(2);
})

document.getElementById("post_submit").addEventListener("click", () => {
    fetch("http://localhost:51966/loggedin", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "post_content": document.getElementById("post_content").value,
            "act": "post"
        })
    }).then(response => {
        return response.json();
    }).then(data => {
        if(data["post_stat"] == "ok"){
            alert("發文成功！！")
        }
        else{
            alert(`發文失敗...\n原因：${data[post_stat]}`)
        }
    }).catch(err => {
        console.log(err)
    })
})

// main

// default stat: bulletin
post_area.remove()
call_area.remove()

// set username
document.getElementById("username").textContent = getUserName();