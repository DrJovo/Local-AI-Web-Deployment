// Assigning to an undeclared variable throws an error instead of quietly creating a global
"use strict";

// What role the user has (guest or signed in)
let userRole = "guest";

// Is the user currently waiting for an AI response
let isSending = false;

// Store responses
class ChatHistory {
    // Public list declaration
    messages = JSON.parse(sessionStorage.getItem("chat")) || [];

    add(messageHTML, plainText, role) {
        const newMessage = { role: role, content: plainText, html: messageHTML };
        this.messages.push(newMessage);
    }
    remove(index) {
        this.messages.splice(index, 1);
    }
    get(index) {
        return this.messages[index];
    }
    getAll() {
        return this.messages;
    }
    count() {
        return this.messages.length;
    }
    update(index, contentHTML, plainText, role=null) {
        if (role == null) { 
            role = this.messages[index].role;
        }
        this.messages[index] = { role: role, content: plainText, html: contentHTML}
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


// -- Scale up prompt input field when overflowing -- //
var input_space = document.getElementById("input-space");
var input_field = document.getElementById("input-field");
var chat_space = document.getElementById("chat-space");

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
        sendMessage();
        return true;
    }
}


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


// -- Loading Chats -- //
function loadPromptInChat(message) {
    const div = document.createElement("div");

    const sanitizedMessage = sanitizeUserMessage(message);

    div.className = "user-chat";
    div.innerHTML = `
        <div>${sanitizedMessage}</div>
    `;

    chat_space.appendChild(div);

    return div;
}

function loadResponseInChat(id, message) {
    const div = document.createElement("div");

    div.className = "ai-chat";
    div.innerHTML = `
        <div class="loading-message" id="${id}-loading"></div>
        <div class="ai-message" id="${id}"></div>
        <div class="ai-actions">
            <button class="ai-copy-text" title="Copy all as plaintext" onclick="CopyText(this)">
                <svg class="copy-text-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                    <path fill="currentColor"
                        d="M192 0c-35.3 0-64 28.7-64 64l0 256c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-200.6c0-17.4-7.1-34.1-19.7-46.2L370.6 17.8C358.7 6.4 342.8 0 326.3 0L192 0zM64 128c-35.3 0-64 28.7-64 64L0 448c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-16-64 0 0 16-192 0 0-256 16 0 0-64-16 0z"/>
                </svg>
            </button>
            <button class="ai-copy-md" title="Copy all with formatting" onclick="CopyMarkdown(this)">
                <svg class="copy-md-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640">
                    <path fill="currentColor"
                        d="M392.8 65.2C375.8 60.3 358.1 70.2 353.2 87.2L225.2 535.2C220.3 552.2 230.2 569.9 247.2 574.8C264.2 579.7 281.9 569.8 286.8 552.8L414.8 104.8C419.7 87.8 409.8 70.1 392.8 65.2zM457.4 201.3C444.9 213.8 444.9 234.1 457.4 246.6L530.8 320L457.4 393.4C444.9 405.9 444.9 426.2 457.4 438.7C469.9 451.2 490.2 451.2 502.7 438.7L598.7 342.7C611.2 330.2 611.2 309.9 598.7 297.4L502.7 201.4C490.2 188.9 469.9 188.9 457.4 201.4zM182.7 201.3C170.2 188.8 149.9 188.8 137.4 201.3L41.4 297.3C28.9 309.8 28.9 330.1 41.4 342.6L137.4 438.6C149.9 451.1 170.2 451.1 182.7 438.6C195.2 426.1 195.2 405.8 182.7 393.3L109.3 320L182.6 246.6C195.1 234.1 195.1 213.8 182.6 201.3z"/>
                </svg>
            </button>
        </div>
    `;

    UpdateAIResponseInChat(div, message);

    chat_space.appendChild(div);

    return div;
}

function AddThoughtBubble(div) {
    let thoughtBubble = div.querySelector(".thought-bubble");
    if (!thoughtBubble) {
        thoughtBubble = document.createElement("div");
        thoughtBubble.innerHTML = `
            <div class="preview-thoughts">
                <div class="preview-inner-text"></div>
            </div>
            <div class="collapsible-thought-bubble">
                <div class="ai-thoughts" data-state="thinking"></div>
            </div>
            <button class="expand-thoughts" aria-expanded="false">Show thinking</button>
        `
        thoughtBubble.className = "thought-bubble";
        div.querySelector(".ai-message").before(thoughtBubble);
    }
    return thoughtBubble;
}

function UpdateLoadingMessageInChat(div, message) {
    const loadingDiv = div.querySelector(".loading-message");
    loadingDiv.textContent = message;
}

function UpdateAIThoughtsInChat(div, thoughts) {
    const thoughtDiv = div.querySelector(".ai-thoughts");
    const previewInnerDiv = div.querySelector(".preview-inner-text");
    if (thoughtDiv && previewInnerDiv) {
        previewInnerDiv.textContent = thoughts.split("\n").filter(l => l.trim() !== "").at(0) ?? "";
        thoughtDiv.innerHTML = DOMPurify.sanitize(
            marked.parse(thoughts)
        );
        Prism.highlightAllUnder(thoughtDiv);
    }
}

function UpdateAIResponseInChat(div, message) {
    const messageDiv = div.querySelector(".ai-message");
    messageDiv.innerHTML = DOMPurify.sanitize(
        marked.parse(message)
    );
    Prism.highlightAllUnder(messageDiv);
}

function ProcessAIResults(lines, state) {
    for (const line of lines) {
        if (!line) continue;
        
        // First event, remove loading message
        if (!state.gotFirstEvent) {
            state.gotFirstEvent = true;
            state.div.querySelector(".loading-message").remove();
        }

        const evt = JSON.parse(line); // evt.type, evt.text
        if (evt.type == "content") {
            state.answer += evt.text;
            UpdateAIResponseInChat(state.div, state.answer);
        }
        else if (evt.type == "thinking") {
            if (!state.thinking){
                state.thinking = true;
                state.bubble = AddThoughtBubble(state.div);
            }
            state.thoughts += evt.text;
            UpdateAIThoughtsInChat(state.div, state.thoughts);
        }
        else if (evt.type == "error") {
            state.error = evt.text;
            break;
        }
    }
}

// Load Chat History
// This first line calls the function after the whole script has run
document.addEventListener("DOMContentLoaded", loadChatHistory);
function loadChatHistory() {
    if (userRole === "guest") {
        // Loop over each message, and if it is from a user or the AI, display it
        for (let i=0; i < chatHistory.count(); i++) {
            const message = chatHistory.get(i);
            if (message.role == "user") {
                loadPromptInChat(message.html);
            }
            else if (message.role == "assistant") {
                loadResponseInChat(i, message.content);
            }
        }
    }

    scrollToBottom(true);
}


// -- Create user message -- //
function createPrompt(message) {
    loadPromptInChat(message);
    scrollToBottom(true);
}


// -- Create AI chat -- //

// Set up rendering for Markdown
const renderer = new marked.Renderer();

marked.use(markedKatex({
    throwOnError: false
}));
marked.setOptions({
    gfm: true,
    breaks: true,
    renderer: renderer
});

const turndownService = new TurndownService(); 
turndownService.escape = function escape(text) { return text; }

renderer.code = function(token) {
    const escapedCode = token.text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    
    const lang = (token.lang || "").toLowerCase()
        .replace("c++", "cpp")
        .replace("c#", "csharp")
        .replace("6502 assembly", "asm6502")
        .replace("asp.net", "aspnet"); // May want to add more

    return `<div class="code-block">
            <div class="code-header"><span class="code-header-language">${lang || ""}</span><button class="copy-code-btn">Copy</button></div>
            <pre class="line-numbers"><code class="language-${lang || ""}">${escapedCode}</code></pre>
            </div>`;
}

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
async function createAIResponse(promptHTML, text) {
    let pending = "";
    const loadingMessage = "Loading...";

    let responseState = { 
        answer: "", 
        thoughts: "", 
        gotFirstEvent: false,
        thinking: false,
        bubble: null, 
        div: null,
        index: null,
        error: null 
    };
    
    try {
        // Save prompt to session storage
        const sanitizedHTML = sanitizeUserMessage(promptHTML);
        chatHistory.add(sanitizedHTML, text, "user");

        // Get the array using the class method, then strip the html property
        const request = JSON.stringify({ 
            messages: chatHistory.getAll().map(({ html, ...rest }) => rest),
            model: "qwen3.5:9b",
            thinking: true
        });

        // Add a temporary response in the store to reserve the slot
        chatHistory.add("", "", "assistant");
        responseState.index = chatHistory.count() - 1;

        // Create the AI chat container
        responseState.div = loadResponseInChat(responseState.index, "");
        const messageDiv = responseState.div.querySelector(".ai-message");

        UpdateLoadingMessageInChat(responseState.div, loadingMessage);

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

                // Recieve JSON structured chunks
                pending += decoder.decode(value, { stream: true });
                const lines = pending.split("\n");
                pending = lines.pop();          // the last piece may be cut off; keep it for the next read
                ProcessAIResults(lines, responseState);

                // Errors
                if (responseState.error) {
                    break;
                }

                // Scroll to the bottom with instant scrolling as each chunk loads in
                scrollToBottom(false, false);
            }
            
            // Flush the decoder to remove any remaining bytes
            if (!responseState.error) {
                pending += decoder.decode();

                // Processes those remaining bytes
                const lines = pending.split("\n");
                ProcessAIResults(lines, responseState);
            }
            else {
                console.error(responseState.error);
                chatHistory.remove(responseState.index);
                chatHistory.remove(responseState.index-1);

                // Do not save the message, and delete the ID to be used by the next message
                messageDiv.removeAttribute("id");
            }

        } catch (error) {
            responseState.error = "\n\n*Error fetching AI response: " + error + "*";
            console.error(error);
        }

        // Remove loading message if it still there
        responseState.div.querySelector(".loading-message")?.remove();

        // Update the displayed text with the final response, and save it (not the thoughts, yet)
        UpdateAIResponseInChat(responseState.div, responseState.answer + (responseState.error || ""));
        if (!responseState.error) {
            chatHistory.update(responseState.index, "", responseState.answer);
            chatHistory.save();
        }
        
        // Handle errors
        else {
            chatHistory.remove(responseState.index);
            chatHistory.remove(responseState.index-1);

            // Delete the ID to be used by the next message
            messageDiv.removeAttribute("id");
        }

        // Update the thought div
        responseState.thinking = false;
        if (responseState.bubble) {
            responseState.div.querySelector(".ai-thoughts").setAttribute("data-state", "done");
        }

    } finally {
        isSending = false;        
        scrollToBottom(false, false);
    }
}

// Listen for clicks on the copy code buttons and copy the code to the clipboard
document.addEventListener("click", function(event) {
    const copyCodeBtn = event.target.closest(".copy-code-btn");
    if (copyCodeBtn) {
        // Copy the code
        const code = copyCodeBtn.closest(".code-block").querySelector("code");
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

// Listen for See More Thought button clicks and expand/collapse the thought bubble
document.addEventListener("click", function(event) {
    const clicked = event.target.closest(".expand-thoughts, .preview-thoughts")
    if (clicked) {
        const thoughtBubble = clicked.closest(".thought-bubble");
        const expandThoughtsBtn = thoughtBubble.querySelector(".expand-thoughts");
        const open = thoughtBubble.classList.toggle("open");
        expandThoughtsBtn.textContent = open ? "Collapse thinking" : "Show thinking";
        expandThoughtsBtn.setAttribute("aria-expanded", open);
    }
});

// -- Sanitation -- //
function sanitizeUserMessage(html) {
    return DOMPurify.sanitize(html, {
        ALLOWED_TAGS: [
            "br",
            "p",
            "div",
            "ul",
            "ol",
            "li",
            "a"
        ],

        ALLOWED_ATTR: [
            "href",
            "target",
            "rel",
            "title"
        ]
    });
}

// Make links open in a new tab
DOMPurify.addHook('afterSanitizeAttributes', function (node) {
    if (node.tagName === 'A') {
        node.setAttribute('target', '_blank');
        node.setAttribute('rel', 'noopener noreferrer');
    }
});


// Listen for paste and sanitize pasted text in the input field
input_field.addEventListener('paste', (event) => {
    // Stop the text from being pasted
    event.preventDefault();

    // Get HTML from the clipboard
    const clipboardHTML = event.clipboardData.getData("text/html");
    
    // If the HTML was unavailable, get the plaintext instead
    if (clipboardHTML.length < 1) {
        const clipboardPlaintext = event.clipboardData.getData("text/plain").trim();

        // Insert text
        document.execCommand("insertText", false, clipboardPlaintext);
    }
    else {
        // Sanitize the text
        const cleanedHTML = sanitizeUserMessage(clipboardHTML);

        // Insert text
        document.execCommand("insertHTML", false, cleanedHTML);
    }
});


// -- Send message -- //
function sendMessage() {
    const html = input_field.innerHTML;
    const text = input_field.innerText.trim();

    if (!isSending && text.length > 0) {
        isSending = true;
        input_field.innerHTML = "";
        chat_space.classList.remove("typing");
        input_field.classList.remove("typing");

        const cleanHTML = sanitizeUserMessage(html);
        const markdown = turndownService.turndown(cleanHTML);

        createPrompt(cleanHTML);
        createAIResponse(cleanHTML, markdown);
    }
}


// -- Copy text -- //
function CopyText(btn) {
    const chat = btn.closest(".ai-chat");
    const message = chat.querySelector(".ai-message");

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
    const chat = btn.closest(".ai-chat");
    const message = chat.querySelector(".ai-message");

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