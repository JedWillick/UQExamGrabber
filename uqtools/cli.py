import argparse
import json
from pathlib import Path
from typing import Union

from .env import Env
from .examgrabber import exam_grabber
from .grade import grade
from .timetable import timetable


def main() -> int:
    parser = setup_argparse()
    args = parser.parse_args()
    if args.cmd is None:
        parser.print_help()
        return 1

    if args.cmd == "env":
        Env.config_env(args)
        return 0

    env = Env(args.username, args.password, args.timeout, args.headless)
    if args.cmd in ["exam", "eg"]:
        exam_grabber(
            env,
            args.courses,
            baseOutDir=args.out,
            force=args.force,
            max_exams=args.max,
        )
    elif args.cmd in ["timetable", "tt"]:
        timetable(
            env,
            out=args.out,
            time_size=args.time_size,
            semester=args.semester,
            year=args.year,
            inject=args.inject,
            fetch=args.fetch,
            orientation=args.orientation,
            store=args.store,
        )
    elif args.cmd in ["grade", "gr"]:
        return grade(
            args.courses,
            out=args.out,
            sem=args.sem,
            year=args.year,
        )
    return 0


def read_json(path: Union[str, Path]):
    try:
        return json.loads(Path(path).read_text())
    except Exception as e:
        raise argparse.ArgumentTypeError(f"Invalid json file: {e}")


def setup_timetable(sub: argparse._SubParsersAction) -> None:
    desc = "Get and convert your UQ timetable into a pretty PDF"
    timetable = sub.add_parser("timetable", aliases=["tt"], description=desc, help=desc)

    timetable.add_argument(
        "-o",
        "--out",
        type=Path,
        help="Output file (default: generated)",
    )
    timetable.add_argument(
        "-r",
        "--orientation",
        default="landscape",
        choices=["portrait", "landscape"],
        help="Set the orientation of the PDF (default: %(default)s)",
    )
    timetable.add_argument(
        "-p",
        "--time-size",
        type=int,
        default=60,
        choices=[30, 60],
        help="The time size (default: %(default)s)",
    )
    timetable.add_argument(
        "-s",
        "--semester",
        choices=["S1", "S2", "S3"],
        help="Manually set the semester (default: current)",
    )
    timetable.add_argument(
        "-y",
        "--year",
        choices=["even", "odd"],
        help="Manually set the year (default: current)",
    )
    timetable.add_argument(
        "-i",
        "--inject",
        type=read_json,
        metavar="JSON",
        help="Inject data from a json file",
    )
    timetable.add_argument(
        "-nf",
        "--no-fetch",
        action="store_false",
        dest="fetch",
        help="Don't fetch data from UQ",
    )
    timetable.add_argument(
        "-S",
        "--store",
        action="store_true",
        help="Store the timetable data in a json file",
    )


def setup_exam(sub: argparse._SubParsersAction) -> None:
    desc = "Download Past UQ exams"
    exam = sub.add_parser("exam", aliases=["eg"], description=desc, help=desc)

    exam.add_argument(
        "courses",
        nargs="+",
        help="Course codes to download",
    )
    exam.add_argument(
        "-o",
        "--out",
        type=Path,
        default=Path.cwd(),
        help="Base out directory.",
    )
    exam.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    exam.add_argument(
        "-n",
        "--max",
        type=int,
        default=0,
        help="Max number of exams to download (default: 0 for all)",
    )


def parse_course_grades(arg: str) -> list:
    tokens = arg.split(",")
    if len(tokens) == 0:
        raise argparse.ArgumentTypeError("No course code given")

    try:
        course = {
            "code": tokens[0],
            "marks": list(map(float, tokens[1:])),
        }
    except ValueError:
        raise argparse.ArgumentTypeError("Marks must be floats")

    return course


def setup_grade(sub: argparse._SubParsersAction) -> None:
    desc = (
        "Calculate what grade you will get and "
        "how much more you need to get with the given marks"
    )
    grade = sub.add_parser("grade", aliases=["gr"], description=desc, help=desc)

    grade.add_argument(
        "courses",
        help="Course code followed by marks in order (e.g. csse2310,15,14,13)."
        "If no marks are given will prompt for them",
        nargs="+",
        type=parse_course_grades,
    )
    grade.add_argument(
        "-o",
        "--out",
        type=Path,
        help="Output file",
    )
    grade.add_argument(
        "-s",
        "--sem",
        type=int,
        help="Semester to calculate grade. (Default: current)."
        "To select summer semester input 3",
    )
    grade.add_argument(
        "-y",
        "--year",
        type=int,
        help="Year to calculate grade for (Default: current)",
    )


def setup_argparse() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Collection of tools to scrap UQ.\n"
        "Use 'uqtools <CMD> --help' for more info",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    root.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=5,
        help="Set the timeout for requests (default: 5)",
    )
    root.add_argument(
        "-b",
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Don't use headless mode",
    )
    root.add_argument(
        "-u", "--username", help="UQ username if not storing in .env file"
    )
    root.add_argument(
        "-p", "--password", help="UQ password if not storing in .env file"
    )

    sub = root.add_subparsers(dest="cmd", metavar="CMD", required=False)
    setup_exam(sub)
    setup_timetable(sub)
    Env.setup_args(sub)
    setup_grade(sub)

    return root
