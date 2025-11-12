import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from app.utils.image_upload import delete_temp_file

CLEANUP_QUEUE: asyncio.Queue = asyncio.Queue()
DELAY_MINUTES = 30

def schedule_deletion(file_path: str):
    """Adds a file path and a scheduled time to the cleanup queue."""
    scheduled_time = datetime.now() + timedelta(minutes=DELAY_MINUTES)
    
    CLEANUP_QUEUE.put_nowait({
        "file_path": file_path,
        "scheduled_time": scheduled_time,
    })
    print(f"Cleanup scheduled for {file_path} at {scheduled_time.isoformat()}")

async def cleanup_worker():
    """
    A background worker that continuously checks the queue and deletes files
    once their scheduled time has passed.
    """
    print("Background cleanup worker started.")
    
    pending_items: List[Dict[str, Any]] = []

    while True:
        try:
            current_time = datetime.now()
            
            ready_items = [item for item in pending_items if item["scheduled_time"] <= current_time]
            pending_items = [item for item in pending_items if item["scheduled_time"] > current_time]

            try:
                new_item = await asyncio.wait_for(CLEANUP_QUEUE.get(), timeout=0.1)
                pending_items.append(new_item)
            except asyncio.TimeoutError:
                pass 

            for item in ready_items:
                print(f"Attempting delayed cleanup for {item['file_path']}")
                await delete_temp_file(item["file_path"])
                CLEANUP_QUEUE.task_done()

            if not pending_items and CLEANUP_QUEUE.empty():
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"Error in cleanup worker: {e}")
            await asyncio.sleep(30)