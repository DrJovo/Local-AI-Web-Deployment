import asyncio

async def Response(prompt):
    await asyncio.sleep(1)  # Simulate processing time
    return f"AI Response to: {prompt}\n> Very cool."