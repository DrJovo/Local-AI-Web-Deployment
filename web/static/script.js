// -- Scale up prompt input field when clicked -- //
var input_space = document.getElementById("input_space");
var input_field = document.getElementById("input_field");
var chat_space = document.getElementById("chat_space");

// When in focus, grow big
input_field.addEventListener("focus", function () {
    chat_space.classList.add("typing");
    input_field.classList.add("typing");
});

// When clicked off, shrink
input_field.addEventListener("blur", function () {
    chat_space.classList.remove("typing");
    input_field.classList.remove("typing");
});