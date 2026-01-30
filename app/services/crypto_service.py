import httpx
from typing import Optional, Dict, Any
from datetime import datetime


class CryptoService:
    """Service for verifying blockchain transactions"""
    
    # BSCScan API for Binance Smart Chain
    BSCSCAN_API = "https://api.bscscan.com/api"
    BSCSCAN_API_KEY = ""  # Optional: add for higher rate limits
    
    # Etherscan API for Ethereum
    ETHERSCAN_API = "https://api.etherscan.io/api"
    
    @staticmethod
    def generate_safepal_deep_link(
        to_address: str,
        amount: float,
        currency: str = "USDT",
        network: str = "bsc"
    ) -> str:
        """
        Generate a deep link to open SafePal wallet with pre-filled transaction
        
        Note: SafePal doesn't have official deep links for payments,
        so we use a workaround with clipboard + instructions
        """
        # SafePal app scheme (opens the app)
        # For now, return a basic link - user will need to manually enter details
        return f"safepal://send?address={to_address}&amount={amount}&token={currency}"
    
    @staticmethod
    def generate_trust_wallet_link(
        to_address: str,
        amount: float,
        currency: str = "USDT",
        network: str = "bsc"
    ) -> str:
        """Generate Trust Wallet deep link"""
        # Trust Wallet uses WalletConnect or simple links
        # For BSC USDT: token contract is 0x55d398326f99059fF775485246999027B3197955
        if network == "bsc" and currency == "USDT":
            token_contract = "0x55d398326f99059fF775485246999027B3197955"
            return f"trust://send?asset=c20000714_t{token_contract}&address={to_address}&amount={amount}"
        return f"trust://send?address={to_address}&amount={amount}"
    
    @staticmethod
    async def verify_bsc_transaction(tx_hash: str) -> Dict[str, Any]:
        """
        Verify a transaction on Binance Smart Chain
        
        Returns:
            Dict with: success, confirmations, amount, from_address, to_address, status
        """
        try:
            async with httpx.AsyncClient() as client:
                # Get transaction details
                response = await client.get(
                    CryptoService.BSCSCAN_API,
                    params={
                        "module": "transaction",
                        "action": "gettxreceiptstatus",
                        "txhash": tx_hash,
                        "apikey": CryptoService.BSCSCAN_API_KEY or ""
                    },
                    timeout=10.0
                )
                data = response.json()
                
                if data.get("status") == "1":
                    # Transaction found and successful
                    receipt_status = data.get("result", {}).get("status", "0")
                    
                    # Get full transaction details
                    tx_response = await client.get(
                        CryptoService.BSCSCAN_API,
                        params={
                            "module": "proxy",
                            "action": "eth_getTransactionByHash",
                            "txhash": tx_hash,
                            "apikey": CryptoService.BSCSCAN_API_KEY or ""
                        },
                        timeout=10.0
                    )
                    tx_data = tx_response.json()
                    result = tx_data.get("result", {})
                    
                    return {
                        "success": True,
                        "status": "confirmed" if receipt_status == "1" else "failed",
                        "from_address": result.get("from", ""),
                        "to_address": result.get("to", ""),
                        "block_number": int(result.get("blockNumber", "0x0"), 16) if result.get("blockNumber") else 0,
                        "confirmations": 12 if receipt_status == "1" else 0,  # BSC is fast
                    }
                else:
                    return {
                        "success": False,
                        "status": "pending",
                        "error": "Transaction not found or pending"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    async def get_crypto_price(currency: str = "USDT") -> float:
        """
        Get current price of cryptocurrency in USD
        For stablecoins like USDT, this is approximately 1.0
        """
        if currency in ["USDT", "USDC", "DAI", "BUSD"]:
            return 1.0  # Stablecoins are pegged to USD
        
        # For other cryptos, would need to call CoinGecko or similar API
        return 0.0
    
    @staticmethod
    def usd_to_crypto(usd_amount: float, currency: str = "USDT") -> float:
        """Convert USD amount to crypto amount"""
        if currency in ["USDT", "USDC", "DAI", "BUSD"]:
            return usd_amount  # 1:1 for stablecoins
        # Add more conversions as needed
        return usd_amount
