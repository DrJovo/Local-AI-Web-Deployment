import asyncio
import textwrap

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