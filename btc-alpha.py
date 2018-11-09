import os
import json
import time
import requests
import traceback
from lxml import etree

from tools import my_mq, my_format ,json_download, html_download, my_websocket
from tools import DepthItem ,TickerItem ,TradeItem, Symbols ,SOCK_PROXIES, HEADERS

file_name = os.path.basename(__file__).split('.')[0]
DepthItem = DepthItem + '_' + file_name
TickerItem = TickerItem + '_' + file_name
TradeItem = TradeItem + '_' + file_name
Symbols = Symbols + '_' + file_name

rabbitmq_url = 'amqp://guest:123456@127.0.0.1:5672'



def parse(exchange_id,exchange_name=file_name):

    my_format_obj = my_format()
    symbols_mq = my_mq(Symbols, Symbols, Symbols,rabbitmq_url=rabbitmq_url)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem,rabbitmq_url=rabbitmq_url)


    def get_symbols():
        map_dict = dict()
        url = 'https://btc-alpha.com/exchange/BTC_USD/'
        res = html_download(url,proxies=SOCK_PROXIES)
        xml = etree.HTML(res)
        tr_list = xml.xpath("//table[@id='markets_table']/tbody//tr")
        symbols = []
        for tr in tr_list:
            subject = tr.xpath("./@id")[0].replace('pair_','').replace('_','^').upper()
            symbols.append(subject)
        symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
        symbols_mq.send_message(symbols_message)
        print(symbols_message)
        return map_dict


    def get_tickers():
        url = 'https://btc-alpha.com/exchange/BTC_USD/'
        res = html_download(url,proxies=SOCK_PROXIES)
        xml = etree.HTML(res)
        tr_list = xml.xpath("//table[@id='markets_table']/tbody//tr")
        ts = my_format_obj.get_13_str_time()
        for tr in tr_list:
            price = tr.xpath("./td[3]/text()")[0]
            subject = tr.xpath("./@id")[0].replace('pair_','').replace('_','^').upper()
            # ts = my_format_obj.get_13_str_time(i[])
            unit = my_format_obj.get_unit(price)
            ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
            tickers_mq.send_message(ticker_message)
            print(ticker_message)


    while 1:
        try:
            map_dict = get_symbols()
            while  1:
                try:
                    get_tickers()
                except Exception as e:
                    print('eid:',exchange_id,traceback.print_exc())
                time.sleep(1)

        except Exception as e:
            print('eid:', exchange_id, traceback.print_exc())
        time.sleep(1)


if __name__ == '__main__':
    print(file_name,'\n')

    exchange_id = '113'
    parse(exchange_id)


