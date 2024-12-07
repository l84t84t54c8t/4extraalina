import asyncio
import shlex
import time


async def runcmd(cmd: str) -> tuple[str, str, int, int]:
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


async def convert_to_gif(file: str, is_video: bool = False) -> str:
    resultFileName = f"gif_{round(time.time())}.mp4"

    if is_video:
        cmd = f"ffmpeg -i '{file}' -c copy '{resultFileName}'"
    else:
        cmd = f"lottie_convert.py '{file}' '{resultFileName}'"

    await runcmd(cmd)

    return resultFileName
