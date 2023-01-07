import enum
 
# Bot Conditon Enum
##---------------------------------------
class Status(enum.Enum):
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
    
 
# Value Conditon Enum
##--------------------------------------- 
class ValueConditon(enum.Enum):
    NOT_SELECTED = "---"
    GREATER_THAN = "greater_than"
    LOWER_THAN = "lower_than"
    
    
# Time Frame Enum
##---------------------------------------
class TimeFrame(enum.Enum):
    NOT_SELECTED = "---"
    MINUTE_1M = "1m"
    MINUTE_5M = "5m"
    MINUTE_15M = "15m"
    MINUTE_30M = "30m"
    HOUR_1H = "1h"
    HOUR_2H = "2h"
    HOUR_4H = "4h"
    DAY_1D = "1d"

# Currency Enum 
##---------------------------------------
class Currency(enum.Enum):
    BTC = "BTC"
    ETH = "ETH"
    BNB = "BNB"
   

# Event Type Enum
##---------------------------------------
class EventType(enum.Enum):
    NOT_SELECTED = "---"
    PRICE = "price"
    RSI = "rsi"
    VOLUME = "volume"
    
    
# ACTIONS Enum
##---------------------------------------
# Order Side  
class OrderSide(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

# Order Type Enum 
##---------------------------------------
class OrderType(enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    
