import hashlib
import hmac
from models.binance_exceptions import *
import time
import typing
from urllib.parse import urlencode
import requests
import math

"""
    Binance class takes users public and private keys check if we on spot or future.
"""


class BinanceApi:
    def __init__(self, public_key: str, secret_key: str, testnet: bool):
        # check the future(levearagedx100) account or spot(regular)

        self._base_url = "https://api.binance.com"

        self._public_key = public_key
        self._secret_key = secret_key
        self._headers = {'X-MBX-APIKEY': self._public_key}
        self.contracts = self.get_contracts()
        self.prices = dict()
        self.futures = False
        self.logs = []
        self.symbol = None

        print("Binance Futures Client successfully initialized")

    def _generate_signature(self, data: typing.Dict) -> str:
        return hmac.new(self._secret_key.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest()

    def _make_request(self, method: str, endpoint: str, data):
        if method == "GET":
            try:
                response = requests.get(self._base_url + endpoint, params=data, headers=self._headers)
            except Exception as e:

                print("Connection error while making %s request to %s: %s"%(method, endpoint, e))
                return None
        elif method == "POST":
            try:
                response = requests.post(self._base_url + endpoint, params=data, headers=self._headers)
            except Exception as e:

                print("Connection error while making %s request to %s: %s"%(method, endpoint, e))
                return None
        elif method == "DELETE":
            try:
                response = requests.delete(self._base_url + endpoint, params=data, headers=self._headers)
            except Exception as e:

                print("Connection error while making %s request to %s: %s"%(method, endpoint, e))
                return None
        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            print("Error while making %s request to %s: %s (error code %s)"%(method, endpoint, response.json(), response.status_code))
            return None

    def get_contracts(self):
        exchange_info = self._make_request("GET", "/api/v3/exchangeInfo", dict())
        contracts = dict()
        if exchange_info is not None:
            for contract_data in exchange_info['symbols']:
                contracts[contract_data['symbol']] = contract_data
            return contracts

    def get_balances(self):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)
        print(data)
        balances = dict()  # sapi/v1/margin/isolated/account
        account_data = self._make_request("GET", "/api/v3/account", data)
        print(account_data)
        if account_data is not None:
            for a in account_data['balances']:
                # balances [a ['baseAsset'] ['asset']] = a ['baseAsset']
                if float(a['free']) > 0.0:
                    balances[a['asset']] = (a['free'])
        return balances

    """
        Place an order. Based on the order_type: LIMIT, MARKET, STOP,
        binance future TAKE_PROFIT, LIQUIDATION
        the price and timeInForce arguments are not required
        TESTING ON ETHUSDT
    """
    async def place_order(self, symbol,
                    side: str,
                    order_type: str,
                    quantity: float,
                    price=None,
                    tif=None):
        try:
            data = dict()
            data['symbol'] = symbol
            print(side,order_type,quantity,price,tif)
            data['side'] = side.upper()
            data['quantity'] = quantity
            data['type'] = order_type.upper()
            if price is not None:
                data['price'] = price
            if tif is not None:
                data [ 'timeInForce' ] =  tif
            print(price)
            data['timestamp'] = int(time.time() * 1000)
            data['signature'] = self._generate_signature(data)
            order_status = self._make_request("POST", "/api/v3/order", data)
            if order_status is not None:
                order_status = (order_status, "binance")
            return order_status
        except BinanceOrderException as e:
            print(e)

