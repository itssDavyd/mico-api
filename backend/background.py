import threading
from uuid import uuid4

process_status = {}


def start_background_task(func, *args, **kwargs):
    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()


def create_process_id():
    process_id = str(uuid4())
    process_status[process_id] = {"status": "processing", "pdf_path": None}
    return process_id
