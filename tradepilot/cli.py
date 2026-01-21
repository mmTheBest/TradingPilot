import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("tradepilot")
    sub = parser.add_subparsers(dest="command", required=True)
    sched = sub.add_parser("ingest-scheduler")
    sched.add_argument("--once", action="store_true")
    worker = sub.add_parser("ingest-worker")
    worker.add_argument("data_type")
    worker.add_argument("--once", action="store_true")
    return parser
