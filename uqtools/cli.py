import argparse as ap
from pathlib import Path

from .env import Env
from .examgrabber import exam_grabber
from .timetable import Timetable


def setup_timetable(sub: ap._SubParsersAction) -> None:
    desc = "Get and convert your UQ timetable into a pretty PDF"
    timetable = sub.add_parser("timetable", aliases=["tt"], description=desc, help=desc)

    timetable.add_argument(
        "-o", "--out",
        help="Output file (default: generated)",
    )
    timetable.add_argument(
        "-p", "--time-size",
        type=int,
        default=60,
        choices=[30, 60],
        help="The time size (default: %(default)s)",
    )
    timetable.add_argument(
        "-e", "--excel",
        action="store_true",
        help="Output Excel file instead of PDF",
    )
    timetable.add_argument(
        "-s", "--semester",
        choices=["S1", "S2", "S3"],
        help="Manually set the semester (default: current)",
    )
    timetable.add_argument(
        "-y", "--year",
        choices=["even", "odd"],
        help="Manually set the year (default: current)",
    )
    timetable.add_argument(
        "-v", "--open",
        action="store_true",
        help="Open the file after writing it",
    )


def setup_exam(sub: ap._SubParsersAction) -> None:
    desc = "Download Past UQ exams"
    exam = sub.add_parser("exam", aliases=["eg"], description=desc, help=desc)

    exam.add_argument(
        "courses",
        type=lambda x: [course for course in x.split(",")],
        help="Comma separated list of courses",
    )
    exam.add_argument(
        "-o", "--out",
        type=Path,
        default=Path.cwd(),
        help=f"Base out directory.",
    )
    exam.add_argument(
        "-n", "--no-overwrite",
        action="store_false",
        dest="overwrite",
        help="Don't overwrite existing files",
    )


def setup_argparse() -> ap.Namespace:
    root = ap.ArgumentParser(
        description="Collection of tools to scrap UQ.\nUse 'uqtools <CMD> --help' for more info",
        formatter_class=ap.RawTextHelpFormatter
    )
    root.add_argument(
        "-t", "--timeout",
        type=int,
        default=5,
        help="Set the timeout for requests (default: 5)",
    )
    root.add_argument(
        "-b", "--no-headless",
        action="store_false",
        dest="headless",
        help="Don't use headless mode",
    )
    root.add_argument(
        "-u", "--username",
        help="UQ username if not storing in .env file"
    )
    root.add_argument(
        "-p", "--password",
        help="UQ password if not storing in .env file"
    )

    sub = root.add_subparsers(dest="cmd", metavar="CMD")
    setup_exam(sub)
    setup_timetable(sub)
    Env.setup_args(sub)
    return root.parse_args()


def main():
    args = setup_argparse()

    if args.cmd == "env":
        Env.config_env(args)
        return

    env = Env(args.username, args.password, args.timeout, args.headless)
    if args.cmd in ["exam", "eg"]:
        exam_grabber(env, args.courses, args.out, args.overwrite)
    elif args.cmd in ["timetable", "tt"]:
        tt = Timetable(env, args.semester, args.year)
        tt.write(args.out, args.excel, args.time_size, args.open)
