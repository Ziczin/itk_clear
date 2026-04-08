# main.py
from fastapi import Response
from src.utils.logger import get_logs_jsonl, clear_logs_jsonl


async def download_logs(clear: bool = False):

    logs = get_logs_jsonl()
    content = "\n".join(logs)
    if content and not content.endswith("\n"):
        content += "\n"

    if clear:
        clear_logs_jsonl()

    return Response(
        content=content,
        media_type="application/x-ndjson",
        headers={"Content-Disposition": "attachment; filename=logs.jsonl"},
    )
