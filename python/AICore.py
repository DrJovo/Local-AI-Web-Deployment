import asyncio
import textwrap

async def Response(prompt):
    text = textwrap.dedent("""
        This is a placeholder response from the AI.

        # Heading 1

        ## Heading 2

        ### Heading 3

        **Bold** and *italic* text.

        ~~The world is flat.~~

        > Blockquote example.

        1. First item
        2. Second item

        - Unordered item 1
        - Unordered item 2

        `print("Code block example")`

        ```
        {
        "firstName": "John"
        }
        ```

        [Link Example](https://www.example.com)

        | Syntax | Description |
        | --- | --- |
        | Header | Title |
        | Paragraph | Text |
    """).strip()
    
    await asyncio.sleep(1)  # Simulate processing time
    return text