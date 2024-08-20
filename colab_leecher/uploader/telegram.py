# copyright 2023 © Xron Trix | https://github.com/Xrontrix10


import logging
from PIL import Image
from asyncio import sleep
from os import path as ospath
from datetime import datetime
from pyrogram.errors import FloodWait
from colab_leecher.utility.variables import BOT, Transfer, BotTimes, Messages, MSG, Paths
from colab_leecher.utility.helper import sizeUnit, fileType, getTime, status_bar, thumbMaintainer, videoExtFix

async def progress_bar(current, total):
    global status_msg, status_head
    upload_speed = 4 * 1024 * 1024
    elapsed_time_seconds = (datetime.now() - BotTimes.task_start).seconds
    if current > 0 and elapsed_time_seconds > 0:
        upload_speed = current / elapsed_time_seconds
    eta = (Transfer.total_down_size - current - sum(Transfer.up_bytes)) / upload_speed
    percentage = (current + sum(Transfer.up_bytes)) / Transfer.total_down_size * 100
    await status_bar(
        down_msg=Messages.status_head,
        speed=f"{sizeUnit(upload_speed)}/s",
        percentage=percentage,
        eta=getTime(eta),
        done=sizeUnit(current + sum(Transfer.up_bytes)),
        left=sizeUnit(Transfer.total_down_size),
        engine="Pyrofork 💥",
    )


async def upload_file(file_path, real_name):
    global Transfer, MSG
    BotTimes.task_start = datetime.now()
    caption = f"<{BOT.Options.caption}>{BOT.Setting.prefix} {real_name} {BOT.Setting.suffix}</{BOT.Options.caption}>"
    type_ = fileType(file_path)

    f_type = type_ if BOT.Options.stream_upload else "document"

    # Upload the file
    try:
        if f_type == "video":
            # For Renaming to mp4
            if not BOT.Options.stream_upload:
                file_path = videoExtFix(file_path)
            # Generate Thumbnail and Get Duration
            thmb_path, seconds = thumbMaintainer(file_path)
            with Image.open(thmb_path) as img:
                width, height = img.size

            MSG.sent_msg = await MSG.sent_msg.reply_video(
                video=file_path,
                supports_streaming=True,
                width=width,
                height=height,
                caption=caption,
                thumb=thmb_path,
                duration=int(seconds),
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id,
            )

        elif f_type == "audio":
            thmb_path = None if not ospath.exists(Paths.THMB_PATH) else Paths.THMB_PATH
            MSG.sent_msg = await MSG.sent_msg.reply_audio(
                audio=file_path,
                caption=caption,
                thumb=thmb_path if thmb_path is not None else None,  # Check for None before assigning
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id,
            )

        elif f_type == "document":
            if ospath.exists(Paths.THMB_PATH):
                thmb_path = Paths.THMB_PATH
            elif type_ == "video":
                thmb_path, _ = thumbMaintainer(file_path)
            else:
                thmb_path = None

            MSG.sent_msg = await MSG.sent_msg.reply_document(
                document=file_path,
                caption=caption,
                thumb=thmb_path if thmb_path is not None else None,  # Check for None before assigning
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id,
            )

        elif f_type == "photo":
            MSG.sent_msg = await MSG.sent_msg.reply_photo(
                photo=file_path,
                caption=caption,
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id,
            )

        Transfer.sent_file.append(MSG.sent_msg)
        Transfer.sent_file_names.append(real_name)

    except FloodWait as e:
        await sleep(5)  # Wait 5 seconds before Trying Again
        await upload_file(file_path, real_name)
    except Exception as e:
        logging.error(f"Error When Uploading : {e}")
