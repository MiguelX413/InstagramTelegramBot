#!/usr/bin/env python3
import logging
import os
from typing import Set, Optional

from telegram import Update
from telegram.ext import (
    Updater,
    InlineQueryHandler,
    CommandHandler,
    CallbackContext,
    Dispatcher,
)

from instagram import InstagramHandler


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Hi, lmao", quote=True)


def main(token: str, ig_user: str, whitelist: Set[int]) -> None:
    updater = Updater(token, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher

    instagram_handler = InstagramHandler(ig_user, whitelist)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("p", instagram_handler.posts))
    dispatcher.add_handler(CommandHandler("storyitem", instagram_handler.story_item))

    dispatcher.add_handler(InlineQueryHandler(instagram_handler.inlinequery))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Runs TG bot")
    if "TG_TOKEN" not in os.environ:
        parser.add_argument(
            "token",
            action="store",
            type=str,
            help="Telegram Token for the bot",
        )
    whitelist_group = parser.add_mutually_exclusive_group(required=True)
    whitelist_group.add_argument(
        "--uid",
        action="append",
        dest="whitelist",
        metavar="Telegram User ID",
        type=int,
        help="Telegram User IDs authorized to use this bot",
    )
    whitelist_group.add_argument(
        "--no-whitelist",
        action="store_const",
        const=None,
        dest="whitelist",
        help="Allow all Telegram Users to use this bot (This could cause rate limiting by Meta)",
    )
    login = parser.add_mutually_exclusive_group(required=True)
    login.add_argument(
        "--no-login",
        action="store_const",
        const=None,
        dest="ig_user",
        help="Runs without an Instagram account (Not recommended, quickly limited)",
    )
    login.add_argument(
        "--user",
        action="store",
        dest="ig_user",
        metavar="Instagram User",
        type=str,
        help="Username through which Instaloader is ran",
    )
    parser.add_argument(
        "--no-rich",
        action="store_false",
        dest="rich",
        help="Disables rich output",
    )
    parser.add_argument(
        "--log-file",
        action="store_true",
        dest="logfile",
        help="Output to log file",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enabled Debugging mode",
    )
    args = parser.parse_args()

    do_rich = True
    if args.rich:
        try:
            from rich.logging import RichHandler
        except ModuleNotFoundError:
            do_rich = False
    else:
        do_rich = False

    if do_rich:
        logging_handlers = [RichHandler(rich_tracebacks=True)]
    else:
        logging_handlers = [logging.StreamHandler()]

    if args.logfile:
        logging_handlers.append(logging.FileHandler("IgTgBot.log"))

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=logging_handlers,
    )

    logging.info(args)
    logging.info("do_rich: %s", do_rich)
    if "TG_TOKEN" in os.environ:
        logging.info("TG_TOKEN: %s", os.environ.get("TG_TOKEN"))

    if args.whitelist is None:
        user_whitelist: Optional[Set[int]] = None
        logging.info("No authorized users specified")
    else:
        user_whitelist: Optional[Set[int]] = set(args.whitelist)
        logging.info("Authorized users: %s", user_whitelist)

    main(
        os.environ.get("TG_TOKEN") if "TG_TOKEN" in os.environ else args.token,
        args.ig_user,
        user_whitelist,
    )
