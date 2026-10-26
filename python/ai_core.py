import os
import textwrap
import subprocess
import psutil
from ollama import AsyncClient

# Async Client
client = AsyncClient()

# Ollama log file
log_path = os.path.join(os.path.dirname(__file__), "..", "ollama.log")

# Startup Ollama
def Boot():
    # This function assumes that 'ollama' is in the system's PATH. 
    # Additionally, the process is returned either as a subprocess.Popen object or as a psutil.Process object, depending on whether Ollama was already running or not. 
    # This shouldn't matter for the current use case since it is only temrinated using the same command, but it's something to be aware of for future extentions.
    
    # Check if Ollama is already running
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == "ollama.exe":
                print("Ollama is already running")
                return proc  # Return the process if found
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Start Ollama
    print("Booting Ollama...")
    with open(log_path, 'a') as log_file:
        return subprocess.Popen(['ollama', 'serve'], stdout=log_file, stderr=subprocess.STDOUT) # Return the process

# Get reponse from the AI
# This should handel mutliple prompts and responses concurrently
async def Response(messages):
    last_chunk = None
    response = ""

    try:
        async for chunk in await client.chat(
            model='llama3.2:3b',
            messages=messages,
            stream=True
        ): 
            last_chunk = chunk
            response += chunk['message']['content']
            yield chunk['message']['content']
    except Exception as e:
        print("Error in Response function: ", str(e))
        yield f"\n\nError: {str(e)}\n"
    if last_chunk:
        # If the AI responds with absolutely nothing, put something in
        if response == "":
            yield " "
        print("\nResponse Token Count --", last_chunk.get("eval_count"))

        
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