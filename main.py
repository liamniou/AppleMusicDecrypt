import asyncio
import argparse
import sys

from creart import add_creator

loop = asyncio.new_event_loop()

from src.logger import LoggerCreator
add_creator(LoggerCreator)
from src.config import ConfigCreator
add_creator(ConfigCreator)
from src.api import APICreator
add_creator(APICreator)
from src.grpc.manager import WMCreator
add_creator(WMCreator)
from src.measurer import MeasurerCreator
add_creator(MeasurerCreator)

from src.cmd import InteractiveShell

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Apple Music Decrypt")
    parser.add_argument("url", nargs="?", help="URL to download (if provided, runs non-interactively)")
    parser.add_argument("-c", "--codec",
                        choices=["alac", "ec3", "aac", "aac-binaural", "aac-downmix", "aac-legacy", "ac3"],
                        default="alac")
    parser.add_argument("-f", "--force", default=False, action="store_true")
    parser.add_argument("-l", "--language", default=None)
    parser.add_argument("--include-participate-songs", default=False, dest="include", action="store_true")

    args = parser.parse_args()

    cmd = InteractiveShell(loop)

    if args.url:
        # Non-interactive mode: download and exit
        from creart import it
        from src.config import Config
        from src.measurer import Measurer
        language = args.language or it(Config).region.language
        try:
            loop.run_until_complete(cmd.do_download([args.url], args.codec, args.force, language, args.include))
            # Wait for tasks to start
            loop.run_until_complete(asyncio.sleep(3))
            # Wait for all song tasks to complete (Measurer tracks actual downloads)
            while it(Measurer).tasks_count() > 0:
                loop.run_until_complete(asyncio.sleep(1))
            # Grace period for final saves
            loop.run_until_complete(asyncio.sleep(2))
        except KeyboardInterrupt:
            pass
        sys.exit(0)
    else:
        # Interactive mode
        try:
            loop.run_until_complete(cmd.start())
        except KeyboardInterrupt:
            loop.stop()
