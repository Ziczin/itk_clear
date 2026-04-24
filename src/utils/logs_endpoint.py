from fastapi import Request, Response

from src.utils.logger import get_logs_jsonl


async def download_logs(request: Request):

    logs = get_logs_jsonl()
    content = "\n".join(logs)
    if content and not content.endswith("\n"):
        content += "\n"

    return Response(
        content=content,
        media_type="application/x-ndjson",
        headers={"Content-Disposition": "attachment; filename=logs.jsonl"},
    )
