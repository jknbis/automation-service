import asyncio
from binance import AsyncClient
from models.binance_exceptions import *
from database.automations import *
from indicators.indicators import *
from models.binance_model import BinanceApi
from models.binance_exceptions import *
from models.enums import *
from binance.helpers import round_step_size


def check_condition_event(event_value,condition_check,event_value_is)->bool:
    res=False
    if(event_value_is==ValueConditon.GREATER_THAN.value):
        if(condition_check>event_value):
            res=True
    elif(event_value_is==ValueConditon.LOWER_THAN.value):
        if(condition_check<event_value):
            res=True
    return res

def is_all_events_completed(events_arr):
    temp_event_array=[]
        #check if all the events are finneshed are true
    for event in events_arr:
        temp_event_array.append(event['finished'])

    return all(temp_event_array)

def is_all_actions_completed(actions_arr):
    temp_action_array=[]
        #check if all the events are finneshed are true
    for action in actions_arr:
        temp_action_array.append(action['finished'])
    return all(temp_action_array)

'''
start = time.time()
c=get_user_api_key()
s=get_user_api_secret()
print(c)
print(s)
end = time.time()
print(end - start)  
'''     
#save that action is completed
async def place_order(coin,side,type,amount,limit_amount,amount_unit,exchange_account_id,automation_id,action_id,automation_actions_array)->bool:
    try:
        api_obj=get_user_api_key_secret(exchange_account_id)
        user_public_key=api_obj['api_key']
        user_secret_key=api_obj['api_secret']
        client = await AsyncClient.create(user_public_key, user_secret_key)
        
        #get the asset tick size for this coin
        symbol_info = await client.get_symbol_info(coin+"USDT")
        step_size = 0.00001
        for f in symbol_info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                step_size = float(f['stepSize'])

                break
        #convert to crypto coin price
        last_price= get_last_candle('1T',coin)
        buy_quantity= amount/last_price['close']
       
       
        tick_size = step_size
        buy_quantity = round_step_size(buy_quantity, tick_size)
        #minum quantity of binance
        minumum_quantity = 10/last_price['close']
        
        #minuse the fee
        if(buy_quantity>minumum_quantity):
            #personal binance connector to execte orders
            b=BinanceApi(user_public_key, user_secret_key,False)
            #if market order
            if(type==OrderType.MARKET.value):
                if(side==OrderSide.BUY.value):
                    await b.place_order(coin+"USDT",
                        "BUY",
                        "MARKET",
                        buy_quantity)
                    print("buy market order")
                elif(side==OrderSide.SELL.value):
                    await b.place_order(coin+"USDT",
                        "SELL",
                        "MARKET",
                        buy_quantity)
                    print("sell market order")
            #if limit order        
            if(type==OrderType.LIMIT.value):
                if(side==OrderSide.BUY.value):
                    await b.place_order(coin+"USDT",
                        "BUY",
                        "LIMIT",
                        buy_quantity,limit_amount,'GTC')
                    print("buy limit order")
                    #await client.order_limit_buy(symbol=coin+"USDT",quantity=60,price=float(limit_amount))
                elif(side==OrderSide.SELL.value):
                    await b.place_order(coin+"USDT",
                        "SELL",
                        "LIMIT",
                        buy_quantity,limit_amount,'GTC')
                    print("sell limit order")
                # await client.order_limit_sell(symbol=coin+"USDT",quantity=60,price=float(limit_amount))

        await client.close_connection() 
        #check if order went ok
        save_action(automation_id,action_id,automation_actions_array)
        
        #await client.order_market_sell(symbol=coin+"USDT",quantity=0.039)
    except BinanceAPIException as e:
        print(e.message)
        await client.close_connection() 
        return False
    except Exception as e:
        print(e)
        await client.close_connection() 
        return False
    
    return True


async def check_signal_place_order(event_value,last_candle,event_value_is,automation_id,event_id,automation_events_array,automation_actions_array,exchange_account_id):
    signal=check_condition_event(event_value,last_candle,event_value_is)
    if(signal):
        save_event(automation_id,event_id,automation_events_array)
        is_events_completed= is_all_events_completed(automation_events_array)
                                #save that event is completed
        if(is_events_completed):     
            for a in automation_actions_array:
                #create new event obj
                action_id=a['actionId']
                action_of_coin=a['ofCoin']
                action_amount=a['amount']
                action_amount_unit=a['amountUnit']
                action_order_side=a['orderSide']
                action_order_type=a['orderType']
                action_limit_price=a['limitPrice']
                                        
                await place_order(action_of_coin,
                                action_order_side,
                                action_order_type,
                                action_amount,
                                action_limit_price,
                                action_amount_unit,
                                exchange_account_id,
                                automation_id,action_id,automation_actions_array)

async def main():  

    over = True
    
    while over:
        #retrieve_all_abots
        automations=retrieve_all_automations()

        for automation in automations:
            #variables for bot
            automation_id = automation['_id']
            exchange_account_id=automation['exchangeAccountId']
            automation_events_array=automation['eventsArr']
            automation_actions_array=automation['actionsArr']
            automation_status=automation['status']
            
            #check if all actions are completed
            if(is_all_actions_completed(automation_actions_array)):
                #update status to finished
                update_status(automation_id,Status.FINISHED.value)
            
            #if bot state is completed
            if automation_status!=Status.PAUSED.value and automation_status!=Status.FINISHED.value:
                for event in automation_events_array:  
                #create new event obj
                    event_id=event['eventId'],
                    event_some_coin=event['someCoin'],
                    event_type=event['type'],
                    event_value=event['value'],
                    event_value_is=event['valueIs'],
                    event_in_time_frame=event['inTimeframe'],
                    event_finished=event['finished'],

                    if(event_finished[0]==False):
                        #PRICE CONDITION   
                        if(event_type[0]==EventType.PRICE.value):
                            #price strategy condition
                            last_candle=get_last_candle("1T", event_some_coin[0])
                            #check if conditon met the value
                            last_candle=last_candle['close']
                            #if condition met the requirments lower greater than with last candle cloase
                            await check_signal_place_order(event_value[0],last_candle,event_value_is[0],
                                                           automation_id,event_id[0],automation_events_array,
                                                           automation_actions_array,exchange_account_id)
                            
 
                        #RSI CONDITION             
                        elif(event_type[0]==EventType.RSI.value):
                            user_timeframe=event_in_time_frame[0]
                            user_selected_coin=event_some_coin[0]
                            #get candles
                            candles = get_candles(user_timeframe, user_selected_coin)
                            #convert to dataframe
                            candles_df = pd.DataFrame(
                                candles, 
                                columns=['_id', 'timestamp', 'open', 'high', 'low', 'close', 'volume'])
                            rsi=RSI(candles_df)
                            rsi=rsi.to_dict()
                            #get the last rsi result
                            last_rsi=rsi[len(rsi)-1]
                            #check if conditon met the value
                            #if condition met the requirments lower greater than with last candle cloase
                            await check_signal_place_order(event_value[0],last_rsi,event_value_is[0],
                                                           automation_id,event_id[0],automation_events_array,
                                                           automation_actions_array,exchange_account_id)
                                        
                                        
                            
                                

if __name__ == "__main__":
    print("Service started listening to user events ...") 
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())