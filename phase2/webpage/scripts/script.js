// Event Listeners
document.getElementById("reg_btn").addEventListener("click", () => {
    for (let i = 0; i < document.getElementsByClassName("login_form").length; i++){
        document.getElementsByClassName("login_form")[i].style.visibility = "collapse"
    }

    for (let i = 0; i < document.getElementsByClassName("reg_form").length; i++){
        document.getElementsByClassName("reg_form")[i].style.visibility = "visible"
    }
})

document.getElementById("login_btn").addEventListener("click", () => {
    for (let i = 0; i < document.getElementsByClassName("login_form").length; i++){
        document.getElementsByClassName("login_form")[i].style.visibility = "visible"
    }

    for (let i = 0; i < document.getElementsByClassName("reg_form").length; i++){
        document.getElementsByClassName("reg_form")[i].style.visibility = "collapse"
    }
})

