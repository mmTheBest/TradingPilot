from tradepilot.cli import build_parser


def test_cli_has_ingest_commands():
    parser = build_parser()
    args = parser.parse_args(["ingest-scheduler"])
    assert args.command == "ingest-scheduler"
