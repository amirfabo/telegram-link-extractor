import sys
import json
import time
import os
import asyncio
import re
import csv
import platform
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.messages import GetWebPageRequest
from telethon.tl.types import InputMessagesFilterUrl 
from telethon.tl.types import WebPage

SCRIPT_FILE_DIR = os.path.dirname(__file__)

settings_file_path = os.path.join(SCRIPT_FILE_DIR, 'settings.json')
if not os.path.exists(settings_file_path):
    print("[ERR] settings.json does not exist.")
    sys.exit(1)

with open(settings_file_path) as settings_file:
    JSON_SETTINGS = json.load(settings_file)

MAIN_MSG = (
    "[GENERAL]\n\n" \
    f"• Messages before: {JSON_SETTINGS['general']['offset_date'] or 'N/A'}\n" \
    "• Status: {status!r}\n\n" \
    "{additional_info}"
)

CHAT_LOG_SECTION = (
    "[Chats]\n\n" \
    "• Current ID: {chat_id}\n" \
    "• Total: {total}\n" \
    "• Checked: {checked} ({progress:.2f}%)\n\n"
)

URL_LOG_SECTION = (
    "[Urls]\n\n" \
    "• Found: {total}\n" \
    "• Valid: {valid} ({progress:.2f}%)\n"
)

def update_screen(message: str) -> None:
    os.system(clear_cmd)
    print(message)

async def get_webpage(client, url):
    for _ in range(2):
        try:
            webpage_response = await client(GetWebPageRequest(url=url, hash=0))

        except:
            return None
        
        await asyncio.sleep(1.0)

    return webpage_response

async def get_dialogs(client):
    archived_dialogs = await client.get_dialogs(archived=True)
    non_archived_dialogs = await client.get_dialogs(archived=False)
    return [*archived_dialogs, *non_archived_dialogs]

async def authorize() -> TelegramClient:
    session_filename = None
    for item in os.listdir(SCRIPT_FILE_DIR):
        if item.endswith(".session"):
            session_filename = item.replace(".session", "")
            break

    if session_filename is None:
        session_filename = f"tg_session-{time.strftime('%H_%M_%S')}"

    client = TelegramClient(
        session=os.path.join(SCRIPT_FILE_DIR, session_filename),
        api_id=JSON_SETTINGS['auth']['api_id'],
        api_hash=JSON_SETTINGS['auth']['api_hash'],
        flood_sleep_threshold=1,
        receive_updates=False,
    )

    try:
        await client.start()

    except Exception as err:
        print(
            "An error occurred :(\n\n"
            "it maybe happen due to reasons:\n\n"
            "- unregistered or revoked session file.\n"
            "- invalid api_id/api_hash.\n"
        )
        sys.exit(1)

    return client

async def main():
    update_screen(MAIN_MSG.format(status='Logging In', additional_info='').strip())
    async with await authorize() as client:
        update_screen(MAIN_MSG.format(status='Getting chats', additional_info='').strip())
        dialogs = await get_dialogs(client=client)
        if not dialogs:
            print("\n\n[ERROR] Your account does not have any chat to extract urls.")
            return

        dialog_count = len(dialogs)
        
        url_rows = []
        valid_url_count = 0

        pattern = r"https:\/\/t(elegram)?\.me\/(joinchat\/)?[A-Za-z0-9\-_]+"
        offset_date = JSON_SETTINGS['general']['offset_date']
        if offset_date is not None and re.match(r"^20[12][0-9]\-[01][1-9]\-[0-3][1-9]$", offset_date):
            year, month, day = map(int, offset_date.split('-'))
            offset_param = datetime(year=year, month=month, day=day)

        else:
            offset_param = None

        update_screen(MAIN_MSG.format(status='Extracting urls', additional_info=''))
        for number, dialog in enumerate(dialogs, start=1):
            found_url_count = len(url_rows)

            update_screen(
                MAIN_MSG.format(
                    status='Extracting urls',
                    additional_info=CHAT_LOG_SECTION.format(
                        total=dialog_count,
                        checked=number,
                        progress=(number * 100) / dialog_count,
                        chat_id=dialog.entity.id,
                    ) + (URL_LOG_SECTION.format(
                        total=found_url_count,
                        valid=valid_url_count,
                        progress=(valid_url_count * 100) / found_url_count,
                    ) if found_url_count else "")
                )
            )

            if (dialog.is_group or dialog.is_channel) and not dialog.entity.creator:
                continue
            
            async for message in client.iter_messages(
                entity=dialog.entity,
                filter=InputMessagesFilterUrl(),
                offset_date=offset_param,
            ):
                urls = [m.group() for m in re.finditer(pattern, message.message)]
                for url in urls:
                    response = await get_webpage(client=client, url=url)
                    if response is None or not isinstance(response.webpage, WebPage):
                        row = (url, None, None)

                    else:
                        row = (url, response.webpage.type.replace('telegram_', '').upper(), response.webpage.title)
                        valid_url_count += 1

                    url_rows.append(row)
                    await asyncio.sleep(2.0)

            with open(
                file=os.path.join(SCRIPT_FILE_DIR, JSON_SETTINGS['output']['path']),
                mode='w', newline='', encoding='utf-8') as output_file:

                writer = csv.writer(output_file)
                writer.writerow(['URL', 'Type', 'Title'])
                for row in url_rows:
                    writer.writerow(row)

    update_screen(
        MAIN_MSG.format(
            status='Done',
            additional_info=CHAT_LOG_SECTION.format(
                total=dialog_count,
                checked=number,
                progress=(number * 100) / dialog_count,
                chat_id=dialog.entity.id,
            ) + (URL_LOG_SECTION.format(
                    total=len(url_rows),
                    valid=valid_url_count,
                    progress=(valid_url_count * 100) / len(url_rows),
            ) if url_rows else "No any tg link found from chats.")
        ).strip()
    )

    input('\n\nPress any key to continue...')

if __name__ == '__main__':
    if platform.system().lower() == "windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        clear_cmd = "cls"

    else:
        clear_cmd = "clear"

    try:
        asyncio.run(main())

    except (KeyboardInterrupt, SystemExit) as e:
        sys.exit(0)