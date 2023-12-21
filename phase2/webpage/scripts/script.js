// Event Listeners
document.getElementById("reg_btn").addEventListener("click", () => {
    document.getElementById("login_form").style.visibility = "collapse";
    document.getElementById("reg_form").style.visibility = "visible";
})

document.getElementById("login_btn").addEventListener("click", () => {
    document.getElementById("login_form").style.visibility = "visible";
    document.getElementById("reg_form").style.visibility = "collapse";
})

