import json 


#Binance API Exceptions
#--------------------------
class BinanceAPIException(Exception):
    
    def __init__(self, response, status_code, text):
        self.code = 0
        try:
            json_res = json.loads(text)
        except ValueError:
            self.message = 'Invalid JSON error message from Binance: {}'.format(response.text)
        else:
            self.code = json_res['code']
            self.message = json_res['msg']
        self.status_code = status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'APIError(code=%s): %s' % (self.code, self.message)

#Binance Request Exception
#--------------------------
class BinanceRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'BinanceRequestException: %s' % self.message

#Binance Rate Limit Exception
#--------------------------
class BinanceOrderException(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return 'BinanceOrderException(code=%s): %s' % (self.code, self.message)

#Binance Order Exception
#--------------------------
class BinanceOrderMinAmountException(BinanceOrderException):

    def __init__(self, value):
        message = "Amount must be a multiple of %s" % value
        super().__init__(-1013, message)

#Binance Order Exception
#--------------------------
class BinanceOrderMinPriceException(BinanceOrderException):

    def __init__(self, value):
        message = "Price must be at least %s" % value
        super().__init__(-1013, message)

#Binance Order Exception
#--------------------------
class BinanceOrderMinTotalException(BinanceOrderException):

    def __init__(self, value):
        message = "Total must be at least %s" % value
        super().__init__(-1013, message)

#Binance Order Exception
#--------------------------
class BinanceOrderUnknownSymbolException(BinanceOrderException):

    def __init__(self, value):
        message = "Unknown symbol %s" % value
        super().__init__(-1013, message)

#Binance Order Exception
#--------------------------
class BinanceOrderInactiveSymbolException(BinanceOrderException):

    def __init__(self, value):
        message = "Attempting to trade an inactive symbol %s" % value
        super().__init__(-1013, message)

#Binance websocket exception
#--------------------------
class BinanceWebsocketUnableToConnect(Exception):
    pass

#Custom Exception
#--------------------------
class NotImplementedException(Exception):
    def __init__(self, value):
        message = f'Not implemented: {value}'
        super().__init__(message)


