// -- Scale up prompt input field when overflowing -- //
var input_space = document.getElementById("input_space");
var input_field = document.getElementById("input_field");
var chat_space = document.getElementById("chat_space");

function CheckOverflow() {
    const isOverflowing = input_field.scrollHeight > input_field.clientHeight;
    if (isOverflowing && !input_field.classList.contains("typing")) {
        chat_space.classList.add("typing");
        input_field.classList.add("typing");
    }
    else if (!isOverflowing && input_field.innerHTML.length < 1) {
        chat_space.classList.remove("typing");
        input_field.classList.remove("typing");
    }
    window.requestAnimationFrame(CheckOverflow);
}

window.requestAnimationFrame(CheckOverflow);


// -- Send message -- //
function SendMessage() {
    var text = input_field.textContent;
    input_field.textContent = "";
}