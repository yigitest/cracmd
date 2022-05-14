import argparse
import logging

from .w3.crabada_client import CrabadaClient
from .w3.web3_config import Web3Config

logger = logging.getLogger("cracmd")
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def main():
    parser = argparse.ArgumentParser(
        description="Commandline interface to crabada functions."
    )

    subparsers = parser.add_subparsers(
        help="help for command", dest="command", required=True
    )

    remove_from_team = subparsers.add_parser(
        "remove-from-team", help="remove-from-team help"
    )
    remove_from_team.add_argument("teamId", type=int, help="teamId, positional")
    remove_from_team.add_argument("position", type=int, help="teamId, positional")

    args = parser.parse_args()

    client = CrabadaClient(config=Web3Config())

    if args.command == "remove-from-team":
        result = client.removeCrabadaFromTeam(
            teamId=args.teamId, position=args.position
        )
        logger.info(f"Result: {result}")


main()
