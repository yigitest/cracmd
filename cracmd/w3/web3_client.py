from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.contract import ContractFunction
from web3.types import TxParams, TxReceipt, Wei
from eth_account.datastructures import SignedTransaction
from eth_typing.encoding import HexStr
from eth_typing import Address
from web3.gas_strategies import rpc

from .web3_config import Web3Config


class Web3Client:
    def __init__(self, config: Web3Config):
        self.RPC_URL = config.RPC_URL
        self.USER_ADDRESS = Web3.toChecksumAddress(config.USER_ADDRESS)
        self.CONTRACT_ADDRESS = Web3.toChecksumAddress(config.CONTRACT_ADDRESS)
        self.USER_PRIVATE_KEY = config.USER_PRIVATE_KEY

        self.CHAIN_ID = config.CHAIN_ID

        self.web3 = Web3(Web3.HTTPProvider(self.RPC_URL))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.web3.isConnected():
            raise Exception("Web3 is not connected!")

    def buildTransactionWithValue(self, to: Address, valueInEth: float) -> TxParams:
        valueInWei = self.web3.toWei(valueInEth, "ether")
        return self.buildTransactionWithValueInWei(to, valueInWei)

    def buildTransactionWithValueInWei(self, to: Address, valueInWei: Wei) -> TxParams:
        tx = self.buildBaseTransaction()
        to = Web3.toChecksumAddress(to)
        extraParams: TxParams = {
            "to": to,
            "value": valueInWei,
            "gas": self.estimateGasForTransfer(to, valueInWei),  # type: ignore
        }
        return tx | extraParams

    def estimateGasForTransfer(self, to: Address, valueInWei: Wei) -> int:
        """
        Return the gas that would be required to send some ETH
        (expressed in Wei) to an address
        """
        return self.web3.eth.estimate_gas(
            {
                "from": self.USER_ADDRESS,
                "to": to,
                "value": valueInWei,
            }
        )

    def buildContractTransaction(self, contractFunction: ContractFunction) -> TxParams:
        baseTx = self.buildBaseTransaction()
        return contractFunction.buildTransaction(baseTx)

    def buildBaseTransaction(self) -> TxParams:
        tx: TxParams = {
            "type": 1,
            "chainId": self.CHAIN_ID,
            "from": self.USER_ADDRESS,
        }
        self.web3.eth.set_gas_price_strategy(rpc.rpc_gas_price_strategy)
        tx["gasPrice"] = self.web3.eth.generate_gas_price()
        tx["nonce"] = self.getNonce()
        return tx

    def signTransaction(self, tx: TxParams) -> SignedTransaction:
        return self.web3.eth.account.sign_transaction(tx, self.USER_PRIVATE_KEY)

    def sendSignedTransaction(self, signedTx: SignedTransaction) -> HexStr:
        """
        Send a signed transaction and return the tx hash
        """
        tx_hash = self.web3.eth.send_raw_transaction(signedTx.rawTransaction)
        return self.web3.toHex(tx_hash)

    def signAndSendTransaction(self, tx: TxParams) -> HexStr:
        """
        Sign a transaction and send it
        """
        signedTx = self.signTransaction(tx)
        return self.sendSignedTransaction(signedTx)

    def getNonce(self):
        return self.web3.eth.get_transaction_count(self.USER_ADDRESS)

    def getTransactionReceipt(self, txHash: HexStr) -> TxReceipt:
        """
        Given a transaction hash, wait for the blockchain to confirm
        it and return the tx receipt.
        """
        return self.web3.eth.wait_for_transaction_receipt(txHash)
