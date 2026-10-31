# Next Steps & Recommendations

A running reference of what's left to do, roughly in priority order. Each item describes *what* and *why*; the *how* is yours to write. Finished items move to [Completed](#completed) at the bottom.

_Last updated: 2026-10-30_

---

## 1. Fix first (bugs)

- [ ] **The thought-bubble click handler throws on every click elsewhere on the page**: [script.js](web/static/script.js)
  - The listener is on `document`, so it runs for *every* click.
  - `clicked.closest(...)` runs before the `if (clicked)` check. Any click that isn't on a bubble (the input box, a copy button, empty space) calls `.closest` on `null` and throws.
  - Return early as soon as `clicked` is `null`.
  - The second `const thoughtBubble` inside the `if` repeats the first one and can go.
- [ ] **Long chats get stuck with 422 errors**: [schemas.py](python/schemas.py)
  - Each message is capped at 12,000 characters, and a request at 200 messages.
  - One long code answer (about 3,000 tokens) is enough. It gets saved, every later request includes it, and the server answers 422.
  - sessionStorage survives reloads, so that tab can't chat again until its history is cleared.
  - Two parts:
    1. Trim what the browser sends (see §6A).
    2. Limit the request's *total* size rather than each message, or raise the cap for assistant messages.
- [ ] **The system prompt teaches broken LaTeX**: the table rule in [ai_core.py](python/ai_core.py)
  - The prompt is a raw string (`r"""`), so the model sees exactly what's typed.
  - `\\left\\vert` reaches it as two backslashes, and in LaTeX `\\` means "new line". Models copy examples.
  - Halve every run of backslashes in that example. The `\\\\` between rows becomes `\\`, LaTeX's row break.
- [ ] **"Copy all as plaintext" garbles math and includes code headers**: `CopyText`
  - KaTeX renders every formula twice: hidden MathML for screen readers, plus the visible HTML. `innerText` reads both, so `$x^2$` copies as "𝑥 2 x 2". (Verified.)
  - The code-block header text ("python Copy") gets copied as well.
  - Copy from a clone with `.katex-mathml` and `.code-header` removed.
  - `innerText` only produces line breaks for elements that are in the page. On a detached clone it acts like `textContent`, so attach the clone offscreen briefly, like `fallbackCopy` does with its textarea.
- [ ] **"Copy with formatting" fails on unfinished or failed replies**: `CopyMarkdown`
  - On an errored message it throws, because the error path removed the `id`.
  - While a reply is streaming, its history entry is still `""`, so it copies nothing.
  - Hide or disable `.ai-actions` until the reply has finished successfully.
- [ ] **Line-number border color isn't applied**: `.line-numbers .line-numbers_rows` in [style.css](web/static/style.css) still has one underscore. Prism's class is `line-numbers-rows`.
- [ ] **The page doesn't fit phones**: `.main-content { width: 1000px }`, declared twice.
  - Anyone on your network using a phone gets a page wider than their screen.
  - Make 1000px a *maximum* instead of a fixed width.
- [ ] **Corrupt sessionStorage stops the whole script**: `ChatHistory.messages`
  - If `JSON.parse` throws on line 13, nothing after it runs.
  - Wrap it in try/catch and start with an empty history.
- [ ] **Language-name cleanup** (partly done): `renderer.code`
  - Done: lowercasing and the symbol aliases (`c++`, `c#`, …).
  - Still to do:
    - Take the **first word** only. The info string can carry more, as in `python title=x`.
    - Check `typeof Prism.languages[id] === "object"`. Check the type, because `Prism.languages` also contains helper functions.
    - Fall back to `plaintext` when the language is unknown.
  - `Object.keys(Prism.languages)` in the Console lists everything your bundle knows.

## 2. Thought bubble: finishing touches

- [ ] **Turn the two `transition` lines back on** (`.preview-thoughts` and `.collapsible-thought-bubble`). They're commented out, so opening and closing jumps instead of animating.
- [ ] **Decide what the preview line shows.**
  - `.at(0)` shows the *first* line of thinking, and never changes after it.
  - `.at(-1)` shows the newest line.
- [ ] **Answer tables get the thoughts' spacing.**
  - The selector list that sets `margin-bottom: 0.5rem` for `.ai-thoughts p, ul, ol…` also includes `.ai-message table, th, td`.
  - It comes later in the file, so it overrides your answer-table margin. That part was probably meant to say `.ai-thoughts`.
  - Margins on `td`/`th` (table cells) and on inline `a` elements have no effect, so those entries can go.
- [ ] **Inline code inside thoughts is unstyled**: `.ai-message :not(pre) > code` only targets the answer. Do the same check for headings and lists, if you want the thoughts to match.
- [ ] **Move `data-state` from `.ai-thoughts` to `.thought-bubble`**, so the preview and the button can react to it too.
- [ ] _Later:_ the "thinking…" animation, for example a shimmer on the preview text. Use `[data-state="thinking"]` as the switch, and respect `@media (prefers-reduced-motion: reduce)`.
- [ ] _Later, maybe:_ save the thoughts with the reply. Only if you want them visible after a reload. Today they're intentionally thrown away.

## 3. Before committing

- [ ] `git add` the untracked libraries: `web/static/katex/`, `marked-katex-extension.js`, `prism.js`, `prism.css`. A fresh clone is broken without them.
- [ ] Trim `katex/` (3.1 MB) down to what `index.html` actually loads: `katex.min.js`, `katex.min.css`, `fonts/`. The `.mjs` files, unminified copies, `katex-swap*` and `contrib/` aren't used.
- [ ] Add a `THIRD_PARTY_NOTICES.md` listing each bundled library, its version and its license:
  - marked v15.0.12 (MIT)
  - DOMPurify (Apache-2.0 / MPL-2.0)
  - Turndown (MIT)
  - Prism 1.30.0 (MIT)
  - KaTeX (MIT)
  - marked-katex-extension 5.1.13 (MIT)
- [ ] Consider several smaller commits instead of one big one: rename, thinking bubble, server events, libraries. That makes it easier to find which change broke something later.
- [ ] Test checklist:
  - [ ] **Code blocks:** with a language, with no language, with `c++`, and indented (no fences)
  - [ ] **Streaming reply:** highlighted, no flicker, padding correct
  - [ ] **Thinking on:** "Loading…" disappears at the first event, the bubble appears only once thinking starts, the preview updates, and Show/Collapse thinking works
  - [ ] **Thinking off,** and a model that can't think: no bubble, no Console errors
  - [ ] **Two replies in a row:** each bubble toggles on its own
  - [ ] **Page refresh:** history re-renders with formatting, no bubbles, copy buttons present
  - [ ] **Copy:** code-block Copy (no line numbers), Copy all as plaintext, Copy with formatting
  - [ ] **Error path:** stop the server mid-reply, then send again after restarting
  - [ ] **Math:** inline, display, and inside a table
  - [ ] **DevTools:** Network → Slow 3G (forces lines to arrive cut in half), and a phone-width viewport
  - [ ] **Console:** no red errors after clicking around the page

## 4. Code blocks & formatting polish

- [ ] Add `data-manual` to the `<script>` tag for `prism.js`, so your render function is the only place highlighting happens. Today Prism also highlights the whole page once on load.
- [ ] **Dark mode never shows:** `:root { color-scheme: light; }` locks every `light-dark()` to its light value.
  - Use `light dark` to follow the OS, or a `data-` attribute on `<html>` for your own toggle.
  - Replace the `green` dark-mode placeholders.
- [ ] **Align messages by class, not position:** `.chat-space > div:nth-child(odd)`. Any extra element in the chat (a notice, a divider, a "new chat" marker) flips the alignment of every message after it.
- [ ] _Later:_ multiple code themes are just blocks of variable values, such as `:root[data-code-theme="…"] { … }`.
  - Switch themes with `document.documentElement.dataset`.
  - Remember the choice in `localStorage` (inside a try/catch).
- [ ] _Optional:_ line-number geometry variables (column width and gap). The plugin's `padding-left`, `left` and `width` must change together.
- [ ] _Optional:_ register the renderer with `marked.use({ renderer: { code(token) {…} } })` instead of `new marked.Renderer()` + `setOptions`.
- [ ] _Deferred:_ the header bottom border.

## 5. Performance

### Browser
- [ ] **Render at most once per frame.**
  - Every token re-runs marked → DOMPurify → Prism over the *whole* answer and the *whole* thoughts, so the cost grows with every token.
  - Use `requestAnimationFrame` to batch everything that arrived since the last frame into one render.
  - Throttle the whole render together; never skip only the highlight step.
- [ ] **Don't render thoughts nobody can see.**
  - While the bubble is collapsed, update only the preview.
  - Render the full thoughts when it's opened, and once at the end.
  - Thinking often runs to thousands of tokens.
- [ ] _Later:_ incremental rendering. Use `marked.lexer` to split the text into blocks, and re-render only the last (still-growing) block.

### Server & model
- [ ] **Keep the start of every request identical.**
  - Ollama reuses work it already did for an unchanged prefix (prefix caching).
  - The system prompt is about 1,200 tokens, so it should never change between requests: no timestamps or usernames in it.
- [ ] **Trim history in big steps, not one message at a time.**
  - Dropping one old message per turn changes the start of every request, so the whole prompt has to be processed again each time (prefill runs at about 350 tok/s here).
  - Dropping a large chunk at once keeps the start stable for many turns.
- [ ] **Cap reply length** with `options={"num_predict": …}`, so one user can't tie up the model.
  - Keep `num_ctx` / `num_gpu` / `num_thread` constant, because changing them reloads the model.
- [ ] **Expect queueing.** qwen3.5 (a hybrid architecture) runs one request at a time no matter what `OLLAMA_NUM_PARALLEL` says. Other users wait behind it.
  - _Later:_ an `asyncio.Semaphore` or queue in the server, so it can tell the browser "you're #2 in line".
- [ ] _Database phase:_ index `messages(chat_id)` and `chats(user_id)`, and paginate long chat lists and histories.

## 6. Input & interaction

- [ ] **Enter-to-send:** `onkeypress` and `event.keyCode` are deprecated.
  - Use `keydown` and `event.key === "Enter"`.
  - Skip when `event.isComposing` is true. People typing Chinese, Japanese or Korean press Enter to confirm a character, and today that sends the message.
- [ ] **Stop button.**
  - The server already cancels the Ollama request when the browser disconnects, so only the browser side is missing: an `AbortController` passed to `fetch` as `signal`.
  - An abort shows up as an `AbortError` in your catch. Treat it as "stopped", not as a failure, and decide whether to keep the partial answer.
- [ ] **Auto-scroll:**
  - The 10 ms `programmaticScroll` flag is shorter than a smooth scroll, so smooth scrolls can look like the user scrolling.
  - Consider detecting the user's intent directly (`wheel`, `touchmove`, keyboard), or the `scrollend` event.
- [ ] **Accessibility:**
  - The send button is only an icon, so give it an `aria-label`.
  - The input box has no label or placeholder (a CSS `:empty::before` placeholder works for `contenteditable`).

## 7. GUI & shutdown robustness ([main.py](python/main.py))

- [ ] **`stop_server()`**:
  - Give each step its own try/except.
  - Treat "process already gone" (`psutil.NoSuchProcess`) as success.
  - Use `wait(timeout)` → `kill()` instead of a bare `wait()`.
  - Kill the **process tree**: Ollama starts `llama-server.exe` as a child.
  - Set the saved process variables back to `None` so a second call does nothing.
- [ ] **Only stop what you started.** When Ollama was already running (the tray app), `Boot()` returns *that* process and `stop_server()` kills it. Have `Boot()` report whether it started Ollama itself.
- [ ] **The GUI says "up" without checking.**
  - If the port is invalid or already in use, uvicorn exits immediately and the label still says "up".
  - Add a health check: `app.after(2000, check)` that schedules itself again, using `server_process.poll()` / `psutil.Process.is_running()`. Update the status label when something dies.
- [ ] **Validate and remember the port.**
  - Check that it's a number in a sensible range before starting.
  - `update_status` re-reads the entry box, so editing it while running shows a wrong address. Store the port used at start.
- [ ] **The server only starts from the project root.** `python.server:app` can only be imported when the working directory is the project folder. Pass `cwd=` to `Popen`, computed from `__file__`.
- [ ] **`report_callback_except`** shuts down the whole app on *any* button error, and does it before printing the error.
  - Decide on a policy: show an error for normal buttons, force-close only if shutdown itself failed.
  - Use `traceback.print_exception(...)` to print it properly.
- [ ] **The `finally` block** calls `force_shutdown()` → `app.destroy()` on a window that's already destroyed.
  - Split "stop processes" from "destroy window," and call only the first one there.
  - Consider `atexit.register(...)` as a backup.
- [ ] **Light mode:** the `tkinter.Frame(..., bg="#242424")` frames stay dark when the theme is light. `CTkFrame` follows the theme.
- [ ] **Crash recovery:**
  - Write the PIDs you started to a file, and delete the file on a clean shutdown.
  - On startup, stop any leftovers, checking the process **name** first because Windows reuses PIDs.
  - _Later:_ Windows Job Objects.
- [ ] Move the database code out of the GUI. It belongs in the server process (see §9B).

## 8. Ollama & server ([ai_core.py](python/ai_core.py), [server.py](python/server.py))

- [ ] **The tray app** is still a `pass` in `Boot()`.
  - The override kills `ollama.exe`, but the tray app (`ollama app.exe`) can restart its own server and take port 11434.
  - Your `env=` settings are then silently gone. At least print a warning; quit the tray app while testing.
- [ ] **Memory check:** look at `ollama ps` (SIZE) and the `-c` / `-np` values in the `starting llama-server` log line.
  - `MAX_LOADED_MODELS=3` keeps up to three models in memory at once.
  - With `KEEP_ALIVE=-1` they never unload, so picking llama3.2 once keeps both models in memory.
- [ ] **Keep the model list in one place.**
  - Today it's in the schema's `Literal[...]` *and* hard-coded in `script.js`.
  - Also record which models can think: Ollama rejects `think=True` for llama3.2, so that combination comes back as an error event.
  - _Later:_ a `GET /api/models` endpoint that serves the allowed list and its capabilities to the page.
- [ ] **Error events send `str(e)` to the browser.** That's fine on your own network for now. Once there are accounts, send a generic message and keep the details in the server log.
- [ ] The stub `/api/chats/{id}/messages` endpoint passes the whole request dict as the messages, and defaults `thinking` to `""`. Rewrite it in the database phase.
- [ ] _Optional:_ `creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS` on the Ollama `Popen`, so it steps aside when you're using the PC.

## 9. Roadmap

### A. Quick wins
- [ ] Guest "New Chat" button (clear `sessionStorage` and the chat area).
- [ ] **Limit how much history gets sent** (`.slice(-N)`, or a character/token budget). This fixes the stuck-chat 422 in §1, and it keeps long chats inside the context window. Trim in big steps (§5).

### B. Database phase
- [ ] `requirements.txt`:
  - Add `aiosqlite` and `argon2-cffi` (it currently has only `argon2-cffi-bindings`).
  - Remove `netifaces2`; nothing imports it.
  - `pip show opentelemetry-api` shows whether anything needs that one ("Required-by").
- [ ] Rewrite [database.py](python/database.py). Problems to fix:
  - It's synchronous `sqlite3` with a global connection, used from the GUI process.
  - The session `token` is an `INTEGER PRIMARY KEY`. That auto-increments, so tokens can be guessed. It should be a random **text** token, ideally stored hashed.
  - `username` has no `UNIQUE`.
  - `DROP TABLE IF EXISTS ?` is invalid: placeholders can't stand in for table names.
  - The `sqlite_master` check is redundant with `CREATE TABLE IF NOT EXISTS`.
  - `messages` needs a nullable `html` column (store the Markdown source, keep the HTML optional).
- [ ] Plain SQL schema, WAL mode, `PRAGMA foreign_keys=ON` on **every** connection, and `?` placeholders everywhere.
- [ ] Create the tables in the FastAPI **lifespan**. Use one connection per request through a dependency.
- [ ] Delete `database.db` after the schema changes.
- [ ] Build the chat endpoints first with a hard-coded user 1, then add accounts.

### C. Accounts
- [ ] `register` / `login` / `logout` / `me` endpoints.
- [ ] Hash passwords with argon2 inside `asyncio.to_thread` (hashing is slow and would block the event loop).
- [ ] Session tokens from `secrets.token_urlsafe`, in an `httponly`, `samesite=lax` cookie with `max_age`.
- [ ] A current-user dependency, and ownership checks on every query (`AND user_id = ?`).
- [ ] Rate-limit login attempts.

### D. Frontend for accounts
- [ ] Sign-in / register UI, and a guest option.
- [ ] Sidebar chat list, switching chats, and creating, renaming and deleting chats.
- [ ] Use real database message IDs instead of history indexes for DOM ids. This also removes the "remove the id after an error" workaround.

### E. Later
- [ ] Context-window management (count tokens, trim or summarize old messages).
- [ ] Save partial replies if the user disconnects or presses Stop mid-stream.
- [ ] HTTPS on the LAN. `navigator.clipboard` only works in a secure context, which is why `fallbackCopy` exists.
- [ ] Stats panel (tokens/sec, context used).
- [ ] One-file installer: install Ollama, pull the model, install dependencies, launch.

## 10. Small cleanup (any time)

- [ ] **script.js:**
  - The error cleanup (removing the message pair and the `id`) appears twice. It's harmless only by luck: the second pair of `remove()` calls points past the end of the array, where `splice` does nothing. Keep the copy after the try/catch.
  - `state.thinking` tracks the same fact as `state.bubble`, so keep one. Setting `responseState.thinking = false` at the end has no effect.
  - `responseState` can be `const`: you change its properties, never the variable itself.
  - `input_space` is unused.
  - Every reply, including reloaded ones, gets an empty `.loading-message` div, because it's in the shared template.
- [ ] **style.css:**
  - `.chat-space::before` (invisible leftover).
  - `width: 1000px` declared twice, and a `;;`.
  - `height: fit-content` on `.thought-bubble`.
  - Unused `@font-face` rules (harmless: browsers only download fonts that are used).
- [ ] **main.py:** `server_toggle_frame` is packed twice, and `server_status_frame` and `interface` are unused.
- [ ] **ai_core.py:** typo "writting" in the system prompt.

---

## Completed

- [x] **snake_case → kebab-case rename** across `index.html`, `style.css` and `script.js`. The one leftover is in §1.
- [x] **Copy buttons stayed inside `.ai-message`:** fixed the missing quote in `id="${id}"`.
- [x] **Indented code blocks crashed rendering:** `token.lang` now defaults to `""`.
- [x] **Streaming code is highlighted**, by one render function (marked → DOMPurify → innerHTML → Prism).
- [x] **Left padding before highlighting:** `.code-block pre` has its own padding.
- [x] **Code-block layout:** header, line-number alignment and colors.
- [x] **Tokens-per-second print can't crash the stream.**
- [x] **History is saved after the final decoder flush**, so no bytes are lost.
- [x] **422 on the second message:** the reply is now written into history before saving.
- [x] **Removed the unused `textwrap` import.**
- [x] **GPU in use:** `OLLAMA_IGPU_ENABLE=1`, all 33 layers on Vulkan.
- [x] **Thinking display:**
  - `think=` is passed to Ollama.
  - The server sends NDJSON events (`thinking` / `content` / `error`), with thinking first and media type `application/x-ndjson`.
  - The browser buffers cut-off lines, keeps one state object, removes "Loading…" at the first event, and adds the bubble lazily.
  - The bubble has a one-line preview and a collapsible drawer, plus a Show/Collapse button with `aria-expanded`.
- [x] **Errors are their own event**, never saved as the reply. Cleanup is decided after the try/catch.
- [x] **Model allowlist:** the schema's `Literal[...]` limits which models can be requested.
- [x] **Show/Collapse thinking hover color.**

---

## Principles to keep in mind

- **Never block the event loop.** Use async libraries, or `asyncio.to_thread` for slow synchronous work.
- **Store the source (Markdown) and render through one function.** Every view gets the same result.
- **Sanitize before `innerHTML`; highlight after.**
- **One fact, one variable.** Two variables tracking the same thing (`thinking` and `bubble`) eventually disagree.
- **Record errors where they happen; decide what to do in one place.**
- **Listeners on `document` run for every click.** Return early when the click isn't yours.
- **CSS: library styles first, yours last.** When specificity ties, the later stylesheet wins.
- **If you want to style it, give it an element.** Bare text inside a grid or flex container gets an invisible box that no selector can reach.
- **A space in a selector means "inside".** `.a.b` is one element with both classes; `.a .b` is a `.b` inside an `.a`.
- **Let content and padding size things.** Avoid fixed heights and absolute positioning for layout.
- **Debug in DevTools first:**
  - Console for errors.
  - Network → Response / Payload for requests.
  - Styles panel: crossed-out rules lost, and ⚠ means invalid.
- **Only stop processes you started.** Treat "already gone" as success.
