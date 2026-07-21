import asyncio
import textwrap
import subprocess
import psutil

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
    return subprocess.Popen(['ollama', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) # Return the process

# Get reponse from the AI
async def Response(prompt):
    text = textwrap.dedent("""
        This is a placeholder response from the AI.

        ---
        

        # Heading 1

        ## Heading 2

        ### Heading 3

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
        
        [Link Example](https://www.example.com)

        | Header Column 1 | Header Column 2 |
        | --- | --- |
        | Item in Col 1, Row 1 | Item in Col 2, Row 1 |
        | Item in Col 1, Row 2 | Item in Col 2, Row 2 |
    """).strip()
    
    await asyncio.sleep(1)  # Simulate processing time
    return text