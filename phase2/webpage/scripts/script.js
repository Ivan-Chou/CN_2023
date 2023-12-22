// Event Listeners
document.getElementById("reg").addEventListener("click", () => {
    // check if ID, PW valid
    let ID = document.getElementById("ID")
    const ID_format = new RegExp(ID.pattern)
    if(!ID_format.test(ID.value)){
        alert("ID 使用了非法字元，請檢查！");
        return
    }
    
    let PW = document.getElementById("PW")
    const PW_format = new RegExp(PW.pattern)
    if(!PW_format.test(PW.value)){
        alert("密碼使用了非法字元，請檢查！");
        return
    }

    fetch("http://localhost:51966/", {
        method: "POST",
        target: "/",
        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            "ID": ID.value,
            "PW": PW.value,
            "act": "reg"
        })
    }).then(response => {
        return response.json()
    }).then(data => {
        if(data["result"] == "0"){
            alert("註冊成功！！")
        }
        else{
            let reason = "";

            if(data["result"] == "1"){
                reason = "已經有人使用這個名稱了";
            }
            else{
                reason = `未知的錯誤 (admin only: reason = ${data["result"]})`;
            }

            alert(`註冊失敗...\n原因：${reason}`);
        }
    }).catch(err => {
        console.log(`<ERR> error = ${err}`);
    })
})
