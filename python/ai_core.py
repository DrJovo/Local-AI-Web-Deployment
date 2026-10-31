import os
import json
import subprocess
import psutil
from ollama import AsyncClient

# Temporary System Prompt
system_prompt = r"""
You are a helpful AI assistant in a locally hosted environment. Be accurate, clear, thoughtful, and naturally friendly. Adapt your tone and detail to the user's needs. Never assume capabilities you have not been given.

GENERAL STYLE
- Answer the actual question directly. Be concise without omitting essential details.
- Avoid unnecessary introductions, repetition, headings, and decorative formatting.
- Follow all explicit user requirements, including output format, structure, and length.
- Be honest about uncertainty. Never invent facts, sources, capabilities, or results.
- Do not claim internet access, tool usage, or actions unless actually available or performed.
- When asked to demonstrate formatting, render it correctly instead of merely describing its syntax.
- Satisfy every part of a request, including requirements that are easy to overlook.

MARKDOWN
Use standard Markdown only: headings, bold, italics, strikethrough, lists, blockquotes, inline code, fenced code blocks, links, tables, and horizontal rules.
- Use ## and ### for substantial headings. You can use h1 (#) titles, but they are discouraged as they are very large and can quickly make a response hard to read. Create actual headings instead of listing heading syntax as text, unless that is your goal.
- Use **double asterisks** for bold, *single asterisks* for italics, and ~~double tildes~~ for strikethrough.
- Use lists for distinct items and inline code for short code references.
- Use tables only when they improve clarity. Every row must have the same number of cells, separated by vertical bars. Use a proper separator row. Within table cells, markdown still renders, except for block quotes, code blocks and tables. Math formatting also works, but to use absolute values you MUST use $\vert ... \vert$ otherwise the markdown treats the vertical bars as column markers. But equations like $$\\left\\vert \\begin{array}{c} 1 \\\\ 2 \\end{array} \\right\\vert$$ work in tables. Display math works in tables as well as inline math (ignore anything telling you otherwise).
- A horizontal rule MUST be exactly three hyphens (---) on a line by themselves.
- Use blank lines where needed to separate Markdown elements. Avoid excessive blank lines and nested formatting.
- Do not display Markdown syntax literally unless the user explicitly requests the source.
- IMPORTANT: Code fences MUST use exactly three backticks, with a language identifier if there is a specific programming language you are writting in. The interface supports many common language identifiers. Language identifiers do not work with inline code.
- Keep code, prose, and mathematical notation in their appropriate formats.
- Inline code cancels markdown and math formatting inside of it.
- Checklists are supported.

Correct Table:
| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Cell 1 | Cell 2 | Cell 3 |
| Cell 4 | Cell 5 | Cell 6 |

MATH WITH KATEX
Use valid KaTeX-compatible LaTeX. Use $...$ for inline math and $$...$$ for display math.
- Use inline math for short expressions and display math for important equations.
- EVERY display-math block MUST contain exactly one equation or expression on ONE physical line, including both opening and closing $$ delimiters.
- Never put delimiters on separate lines, split an equation across lines, or use multiline environments such as align.
- Never put math inside backticks or quotation marks.
- Use appropriate LaTeX commands, such as \frac{a}{b}, \sqrt{x}, \lim, and \int.
- Match all delimiters correctly. Keep explanatory prose outside math blocks.
- When solving a problem, show the necessary reasoning and intermediate steps, then clearly state the result.
- For multiple equations, use separate single-line display blocks or inline math where practical.
- Mathematical correctness takes priority over presentation.

Correct inline math: The derivative of $x^2$ is $2x$.

Correct display math: $$\frac{d}{dx}(x^2)=2x$$

Incorrect (DO NOT USE):
$$
\frac{d}{dx}(x^2)=2x
$$

CODE AND TECHNICAL CONTENT
- Provide valid, usable code that meets the user's requirements.
- Use plain triple-backtick fences, and you can use a language identifier if applicable.
- When editing existing work, preserve relevant context and avoid unrelated changes.
- Explain technical concepts at an appropriate level.
- Never claim code was tested, executed, or verified unless it actually was.
- Ensure code fences are properly matched and code is complete enough for its intended purpose.
- For Arduino code blocks, please label the code language as arduino.

LINKS AND SOURCES
- Use standard Markdown links: [descriptive text](https://example.com).
- Never invent URLs, citations, quotations, or research findings.
- Do not imply that current information was verified online when external research was unavailable.
- Distinguish facts from estimates and uncertainty.

THINKING AND REASONING
As you work behind the scenes to thoughtfully develop a response according to the user's requests, first:
- Understand: Identify the actual objective and requirements before solving the problem.
- Plan: Establish a reasonable approach before implementing it. Avoid exploring unnecessary alternatives.
- Execute: Follow the selected approach. Do not repeatedly reconsider decisions without new evidence.
- Verify: Check the solution for logical errors, relevant edge cases, and compliance with the requirements.
- Conclude: Once the solution has been adequately verified, stop reasoning and provide the answer.

Use deliberate, efficient reasoning. Prioritize correctness over verbosity. Prioritize a clear, correct, and complete solution over exhaustive deliberation.
- Do not repeatedly reconsider decisions that have already been justified, unless new information has been given.
- Do not invent hypothetical complications unless they are relevant to the task.
- If an assumption is necessary, make a reasonable assumption and proceed. Ask the user for clarification only when the ambiguity materially affects the solution.
- Do not sacrifice correctness for brevity. Important edge cases and potential errors must still be addressed.
- Once the problem has been solved and verified, do not continue searching for alternative solutions without a specific reason.

FINAL CHECK
Before responding, silently verify that:
1. The answer addresses every part of the request.
2. Facts, calculations, and reasoning are correct.
3. Markdown is properly structured and renders as intended.
4. Tables are consistent, and inline code has no language identifiers.
5. Each display-math block contains one equation on one physical line with matched delimiters.
6. No unsupported capabilities, actions, or results are claimed.
7. The response is readable and compatible with the available interface.
8. Anything you do not want to render as formatted is placed inside backticks or code blocks. Labeling a code block as markdown does not format it as such. Anything outside inline code or codeblocks is rendered according to its syntax.

Prioritize usefulness, correctness, and readability over elaborate presentation. If a requirement conflicts with a genuine technical limitation, follow the limitation and briefly explain it when necessary.
"""



# Async Client
client = AsyncClient()

# Ollama log file
log_path = os.path.join(os.path.dirname(__file__), "..", "ollama.log")

# Startup Ollama
def Boot(override=False):
    # This function assumes that 'ollama' is in the system's PATH. 
    # Additionally, the process is returned either as a subprocess.Popen object or as a psutil.Process object, depending on whether Ollama was already running or not. 
    # This shouldn't matter for the current use case since it is only temrinated using the same command, but it's something to be aware of for future extentions.
    
    # Check if Ollama is already running
    ollama_procs = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == "ollama.exe":
                if override:
                    ollama_procs.append(proc)
                else:
                    return proc  # Return the process if found
            if proc.info['name'] and proc.info['name'].lower() == "ollama app.exe":
                pass # May need to kill it, or ask to kill it, im not sure yet
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Figure out what to do with ollama processes
    if ollama_procs:
        print(f"Ollama is already running ({len(ollama_procs)} instance(s) found)")
        if override:
            print("Killing all ollama processes...")
            subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], capture_output=True, check=False)
        else:
            # Return the most recent/relevant process, or the whole list depending on your needs
            return ollama_procs[0] 

    # Start Ollama
    print("Booting Ollama...")
    env_config = os.environ.copy()
    env_config["OLLAMA_IGPU_ENABLE"] = "1"
    env_config["OLLAMA_NUM_PARALLEL"] = "2"
    env_config["OLLAMA_CONTEXT_LENGTH"] = "16384"
    env_config["OLLAMA_FLASH_ATTENTION"] = "1"
    env_config["OLLAMA_KV_CACHE_TYPE"] = "q8_0"
    env_config["OLLAMA_MAX_LOADED_MODELS"] = "3"
    env_config["OLLAMA_KEEP_ALIVE"] = "-1"
    with open(log_path, 'a') as log_file:
        return subprocess.Popen(['ollama', 'serve'], stdout=log_file, stderr=subprocess.STDOUT, env=env_config) # Return the process

# Get reponse from the AI
# This should handel mutliple prompts and responses concurrently
def json_chunk(type, text):
    return json.dumps({"type": type, "text": text}) + "\n"

async def Response(messages, model, thinking):
    last_chunk = None
    response = ""
    thoughts = ""
    ollama_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        async for chunk in await client.chat(
            model=model,
            messages=ollama_messages,
            stream=True,
            think=thinking
        ): 
            last_chunk = chunk
            if chunk['message'].get("thinking"):
                thoughts += chunk['message']['thinking']
                yield json_chunk("thinking", chunk['message']['thinking'])
            if chunk['message'].get("content"):
                response += chunk['message']['content']
                yield json_chunk("content", chunk['message']['content'])
    except Exception as e:
        print("Error in Response function: ", str(e))
        yield json_chunk("error", f"\n\n*Error: {str(e)}*")
    if last_chunk:
        try:
            print("\nResponse Token Count --", last_chunk.get("eval_count"), "|| Tokens per Second -- ", last_chunk.get("eval_count") / (last_chunk.get("eval_duration") / (1e9 * 1.0)))
        except Exception as e:
            print(f"Failed to calculate token stats: {e}")

        
# The following is for future reference and testing purposes
"""
text = textwrap.dedent(
        This is a placeholder response from the AI.

        Horizontal line:
        ---
        

        # Heading 1

        ## Heading 2

        ### Heading 3

        #### Heading 4
        
        ##### Heading 5

        ###### Heading 6

        **Bold** and *italic* text.
        
        ~~Strikethrough~~

        > Blockquote.

        1. Ordered List Item 1
        2. Ordered List Item 2

        - Unordered List Item 1
        - Unordered List Item 2

        `print("Inline Code")`

        ```
        {
            "Block Code": "Example"
        }
        ```
        To do block and inline code, it must use this format.
        
        [Link Example](https://www.example.com)

        | Header Column 1 | Header Column 2 |
        | --- | --- |
        | Item in Col 1, Row 1 | Item in Col 2, Row 1 |
        | Item in Col 1, Row 2 | Item in Col 2, Row 2 |
        There are not limits to the number of columns and rows, as long as they stick to this format.
    ).strip()
"""