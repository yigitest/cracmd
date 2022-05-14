from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.contract import Contract, ContractFunction
from web3.types import BlockData, Nonce, TxParams, TxReceipt, TxData
from eth_account.datastructures import SignedTransaction
from eth_typing.encoding import HexStr


from .web3_config import Web3Config


class Web3Client:
    def __init__(self, config: Web3Config):
        self.RPC_URL = config.RPC_URL
        self.USER_ADDRESS = Web3.toChecksumAddress(config.USER_ADDRESS)
        self.CONTRACT_ADDRESS = Web3.toChecksumAddress(config.CONTRACT_ADDRESS)
        self.USER_PRIVATE_KEY = config.USER_PRIVATE_KEY

        self.CHAIN_ID = config.CHAIN_ID
        self.GAS_LIMIT = config.GAS_LIMIT
        self.MAX_PRIORITY_FEE_PER_GAS_IN_GWEI = config.MAX_PRIORITY_FEE_PER_GAS_IN_GWEI

        self.web3 = Web3(Web3.HTTPProvider(self.RPC_URL))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.web3.isConnected():
            raise Exception("Web3 is not connected!")

    def buildContractTransaction(self, contractFunction: ContractFunction) -> TxParams:
        """
        Build a transaction that involves a contract interation.

        Requires passing the contract function as detailed in the docs:
        https://web3py.readthedocs.io/en/stable/web3.eth.account.html#sign-a-contract-transaction
        """
        baseTx = self.buildBaseTransaction()
        return contractFunction.buildTransaction(baseTx)

    def buildBaseTransaction(self) -> TxParams:
        """
        Build a basic EIP-1559 transaction with just nonce, chain ID and gas;
        before invoking this method you need to have specified a chainId and
        called setNodeUri().

        Gas is estimated according to the formula
        maxMaxFeePerGas = 2 * baseFee + maxPriorityFeePerGas.
        """
        tx: TxParams = {
            "type": 0x2,
            "chainId": self.CHAIN_ID,
            "gas": self.GAS_LIMIT,  # type: ignore
            "maxFeePerGas": Web3.toWei(self.estimateMaxFeePerGasInGwei(), "gwei"),
            "maxPriorityFeePerGas": Web3.toWei(
                self.MAX_PRIORITY_FEE_PER_GAS_IN_GWEI, "gwei"
            ),
            "nonce": self.getNonce(),
        }
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

    def estimateMaxFeePerGasInGwei(self):
        """
        Gets the base fee from the latest block and returns a maxFeePerGas
        estimate as 2 * baseFee + maxPriorityFeePerGas, as done in the
        web3 gas_price_strategy middleware (and also here >
        https://ethereum.stackexchange.com/a/113373/89782)
        """
        latest_block = self.web3.eth.get_block("latest")
        baseFeeInWei = latest_block["baseFeePerGas"]  # in wei
        baseFeeInGwei = int(Web3.fromWei(baseFeeInWei, "gwei"))
        return 2 * baseFeeInGwei + self.MAX_PRIORITY_FEE_PER_GAS_IN_GWEI

    def getNonce(self):
        return self.web3.eth.get_transaction_count(self.USER_ADDRESS)

    def getTransactionReceipt(self, txHash: HexStr) -> TxReceipt:
        """
        Given a transaction hash, wait for the blockchain to confirm
        it and return the tx receipt.
        """
        return self.web3.eth.wait_for_transaction_receipt(txHash)
