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


// -- Create user chat -- //
function createPrompt(message) {
    const div = document.createElement("div");

    div.className = "user_chat";
    div.innerHTML = `
        <div>${message}</div>
    `;

    chat_space.appendChild(div);
}


// -- Create AI chat -- //
function createAIResponse(message) {
    const div = document.createElement("div");

    div.className = "ai_chat";
    div.innerHTML = `
        <p>${message}</p>   

        <button class="ai_copy" onclick="CopyText(this)">
            <svg id="copy_icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                <path fill="currentColor"
                    d="M192 0c-35.3 0-64 28.7-64 64l0 256c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-200.6c0-17.4-7.1-34.1-19.7-46.2L370.6 17.8C358.7 6.4 342.8 0 326.3 0L192 0zM64 128c-35.3 0-64 28.7-64 64L0 448c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-16-64 0 0 16-192 0 0-256 16 0 0-64-16 0z"/>
            </svg>
        </button>
    `;

    chat_space.appendChild(div);
}


// -- Send message -- //
function SendMessage() {
    var html = input_field.innerHTML;
    
    if (html.length > 0) {
        input_field.innerHTML = "";

        createPrompt(html);
        createAIResponse("This is an example AI response.");
    }
}


// -- Copy text -- //
function CopyText(btn) {
  const text = btn.previousElementSibling.textContent; 
  navigator.clipboard.writeText(text)
}