import os
import json
import logging

from web3.types import TxParams
from eth_typing.encoding import HexStr


from .web3_client import Web3Client
from .web3_config import Web3Config


logger = logging.getLogger("cracmd")


def _getContractAbiFromFile(fileName: str):
    with open(fileName) as file:
        return json.load(file)


class CrabadaClient(Web3Client):
    def __init__(self, config: Web3Config):
        super().__init__(config=config)

        abiDir = os.path.dirname(os.path.realpath(__file__)) + "/abi"
        abi_json = _getContractAbiFromFile(abiDir + "/crabada-abi.json")

        self.contract = self.web3.eth.contract(
            address=self.CONTRACT_ADDRESS, abi=abi_json
        )

    def removeCrabadaFromTeam(self, teamId: int, position: int) -> bool:
        try:
            txParams: TxParams = self.buildContractTransaction(
                self.contract.functions.removeCrabadaFromTeam(teamId, position)
            )
            logger.debug(f"TxParams: {txParams}")

            txHash = self.signAndSendTransaction(txParams)
            logger.info(f"txHash: {txHash}")

            txReceipt = self.getTransactionReceipt(txHash=txHash)
            logger.debug(f"txParams: {txParams}")

            return txReceipt["status"] == 1
        except:
            logger.exception("removeCrabadaFromTeam error!")
            return False
