// Assigning to an undeclared variable throws an error instead of quietly creating a global
"use strict";

// What role the user has (guest or signed in)
let user_role = "guest";


// -- Scale up prompt input field when overflowing -- //
var input_space = document.getElementById("input_space");
var input_field = document.getElementById("input_field");
var chat_space = document.getElementById("chat_space");

input_field.addEventListener("input", () => {
    const isEmpty = input_field.innerHTML === "" || input_field.innerHTML === "<br>" || input_field.innerHTML === "<div><br></div>";
    if (isEmpty) {
        chat_space.classList.remove("typing");
        input_field.classList.remove("typing");
    }
    else {
        const isOverflowing = input_field.scrollHeight > input_field.clientHeight;
        if (isOverflowing && !input_field.classList.contains("typing")) {
            chat_space.classList.add("typing");
            input_field.classList.add("typing");
        }
    }
});

// -- Make Shift+Enter create a new line in the input field, and Enter send the message -- //
function checkEnter(event) {
    if (event.keyCode == "13" && !event.shiftKey) {
        event.preventDefault();
        SendMessage();
        return true;
    }
}

// -- Create user message -- //
function createPrompt(message) {
    const div = document.createElement("div");

    div.className = "user_chat";
    div.innerHTML = `
        <div>${message}</div>
    `;

    chat_space.appendChild(div);

    scrollToBottom(true);
}


// -- Create AI chat -- //

// Store responses
class ChatHistory {
    // Public list declaration
    messages = JSON.parse(sessionStorage.getItem("chat")) || [];

    add(message, role) {
        const newMessage = { role: role, content: message };
        this.messages.push(newMessage);
    }
    get(index) {
        return this.messages[index];
    }
    getAll() {
        return this.messages;
    }
    update(index, content, role=null) {
        if (role == null) { 
            role = this.messages[index].role;
        }
        this.messages[index] = { role: role, content: content }
    }
    clear() {
        this.messages = [];
    }
    save() {
        sessionStorage.setItem("chat", JSON.stringify(this.messages));
        console.log('Updated Session Storage:', JSON.parse(sessionStorage.getItem("chat")));
    }
}
const chatHistory = new ChatHistory();

// Set up rendering for Markdown
const renderer = new marked.Renderer();
marked.setOptions({
    gfm: true,
    breaks: true,
    renderer
});

renderer.code = function(token) {
    const escapedCode = token.text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    return `<div class="code-block">
            <button class="copy-code-btn">Copy</button>
            <pre><code class="language-${token.lang || ""}">${escapedCode}</code></pre>
            </div>`;
};

// Call the AI as a guest
async function GetResponseAsGuest(request){
    // Get response
    const result = await fetch("/api/guest/respond", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: request
    });
    
    // return the result
    return result;
}

// Create AI response
async function createAIResponse(prompt) {
    let response = "";
    const loadingMessage = "Loading...";
    
    try {
        // Save prompt to session storage
        chatHistory.add(prompt, "user");

        // Build request body
        const request = JSON.stringify({ messages: chatHistory.getAll()});

        // Add a temporary response in the store to reserve the slot
        chatHistory.add("", "assistant");
        const responseIndex = chatHistory.messages.length - 1;

        // Create the AI chat container
        const div = document.createElement("div");

        div.className = "ai_chat";
        div.innerHTML = `
            <div class="ai_message" id=${responseIndex}></div>

            <div class="ai_actions">
                <button class="ai_copy_text" title="Copy all as plaintext" onclick="CopyText(this)">
                    <svg id="copy_text_icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                        <path fill="currentColor"
                            d="M192 0c-35.3 0-64 28.7-64 64l0 256c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-200.6c0-17.4-7.1-34.1-19.7-46.2L370.6 17.8C358.7 6.4 342.8 0 326.3 0L192 0zM64 128c-35.3 0-64 28.7-64 64L0 448c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-16-64 0 0 16-192 0 0-256 16 0 0-64-16 0z"/>
                    </svg>
                </button>
                <button class="ai_copy_md" title="Copy all with formatting" onclick="CopyMarkdown(this)">
                    <svg id="copy_md_icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640">
                        <path fill="currentColor"
                            d="M392.8 65.2C375.8 60.3 358.1 70.2 353.2 87.2L225.2 535.2C220.3 552.2 230.2 569.9 247.2 574.8C264.2 579.7 281.9 569.8 286.8 552.8L414.8 104.8C419.7 87.8 409.8 70.1 392.8 65.2zM457.4 201.3C444.9 213.8 444.9 234.1 457.4 246.6L530.8 320L457.4 393.4C444.9 405.9 444.9 426.2 457.4 438.7C469.9 451.2 490.2 451.2 502.7 438.7L598.7 342.7C611.2 330.2 611.2 309.9 598.7 297.4L502.7 201.4C490.2 188.9 469.9 188.9 457.4 201.4zM182.7 201.3C170.2 188.8 149.9 188.8 137.4 201.3L41.4 297.3C28.9 309.8 28.9 330.1 41.4 342.6L137.4 438.6C149.9 451.1 170.2 451.1 182.7 438.6C195.2 426.1 195.2 405.8 182.7 393.3L109.3 320L182.6 246.6C195.1 234.1 195.1 213.8 182.6 201.3z"/>
                    </svg>
                </button>
            </div>
        `;

        // Give it a temporary loading message
        const messageDiv = div.querySelector(".ai_message");
        messageDiv.innerHTML = loadingMessage;

        chat_space.appendChild(div);

        scrollToBottom();

        // Get the AI's response from the backend
        try {
            const result = await GetResponseAsGuest(request);

            if (!result.ok) {
                throw new Error(`HTTP error ${result.status}`);
            }

            const reader = result.body.getReader();
            const decoder = new TextDecoder("utf-8");

            while (true) {
                const { done, value } = await reader.read();
                
                // When the last chunk is received, break the loop
                if (done) {
                    break;
                }

                // Decode the chunk and append it to the response
                response += decoder.decode(value, { stream: true });

                // Sanitize and render the response as Markdown as it streams in
                messageDiv.innerHTML = DOMPurify.sanitize(
                    marked.parse(response)
                );

                // Scroll to the bottom with instant scrolling as each chunk loads in
                scrollToBottom(false, false);
            }
            
            // Flush the decoder to remove any remaining bytes
            response += decoder.decode();

        } catch (error) {
            response += "\n\n*Error fetching AI response.*";
            console.error(error);
        }


        // Update the response in the response store
        chatHistory.update(responseIndex, response);

        // Run one final sanitization and Markdown rendering after the full response is received
        messageDiv.innerHTML = DOMPurify.sanitize(
            marked.parse(response)
        );

        // Save the chat history to the browser; disappears when the tab closes
        chatHistory.save();
        
    } finally {
        isSending = false
        scrollToBottom(false, false);
    }
}

// Listen for clicks on the copy code buttons and copy the code to the clipboard
document.addEventListener("click", function(event) {
    const copyCodeBtn = event.target.closest(".copy-code-btn");
    if (copyCodeBtn) {
        // Copy the code
        const code = copyCodeBtn.parentElement.querySelector("code");
        try {
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(code.textContent);
            } else {
                fallbackCopy(code.textContent);
            }

            console.log("Copied");
        }
        catch (err) {
            console.error(err);
        }

        // Change the button text to "Copied!" for 1.5 seconds
        copyCodeBtn.textContent = "Copied!";
            setTimeout(() => {
                copyCodeBtn.textContent = "Copy";
            }, 1500); 
    }
});


// -- Scroll to bottom of AI message on prompt send -- //
// Check if the user is scrolling
let isUserScrolling = false;
let programmaticScroll = false;
chat_space.onscroll = (event) => {
    if (programmaticScroll) return;
    const isAtBottom = chat_space.scrollHeight - chat_space.scrollTop <= chat_space.clientHeight + 5;
    if (isAtBottom) {
        isUserScrolling = false;
    } else {
        isUserScrolling = true;
    }
}

// If the user is not scrolling, automatically scroll to the bottom of the chat space
function scrollToBottom(ignoreScrollCheck = false, smoothScroll = true) {
    if (!isUserScrolling || ignoreScrollCheck) {
        programmaticScroll = true;
        isUserScrolling = false;
        chat_space.scrollTo({top: chat_space.scrollHeight, behavior: smoothScroll ? "smooth" : "auto"});
        
        // Reset the programmatic flag right after the layout updates
        setTimeout(() => {
            programmaticScroll = false;
        }, 10);
    }
}


// -- Sanitation -- //
function sanitizeMessage(html) {
    return DOMPurify.sanitize(html, {
        ALLOWED_TAGS: [
            "br",
            "p",
            "div",
            "b",
            "strong",
            "i",
            "em",
            "u"
        ],

        ALLOWED_ATTR: [
            "href",
            "target",
            "rel",
            "title",
            "class",
        ]
    });
}


// -- Send message -- //
let isSending = false;
function SendMessage() {
    var html = input_field.innerHTML;
    const text = input_field.innerText.trim();

    if (!isSending && text.length > 0) {
        isSending = true;
        input_field.innerHTML = "";
        chat_space.classList.remove("typing");
        input_field.classList.remove("typing");

        const clean_html = sanitizeMessage(html);

        createPrompt(clean_html);
        createAIResponse(text);
    }
}


// -- Copy text -- //
function CopyText(btn) {
    const chat = btn.closest(".ai_chat");
    const message = chat.querySelector(".ai_message");

    const text = message.innerText;

    try {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text);
        } else {
            fallbackCopy(text);
        }

        console.log("Copied");
    }
    catch (err) {
        console.error(err);
    }
}

function CopyMarkdown(btn) {
    const chat = btn.closest(".ai_chat");
    const message = chat.querySelector(".ai_message");

    const id = message.id;
    const markdown = chatHistory.get(id).content;

    try {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(markdown);
        } else {
            fallbackCopy(markdown);
        }

        console.log("Copied");
    }
    catch (err) {
        console.error(err);
    }
}

function fallbackCopy(text) {
    const textarea = document.createElement("textarea");

    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";

    document.body.appendChild(textarea);

    textarea.select();
    document.execCommand("copy");

    document.body.removeChild(textarea);
}