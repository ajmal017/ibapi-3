#from ibw.client import IBClient

#REGULAR_ACCOUNT = 'DU1937358'
#REGULAR_USERNAME = 'ajmal483'
#REGULAR_PASSWORD = 'ajmal017'


# Create a new session of the IB Web API.
#ib_client = IBClient(username= REGULAR_USERNAME, account= REGULAR_ACCOUNT)

# create a new session.
#ib_client.create_session()
# grab the account data.
#account_data = ib_client.portfolio_accounts()

# print the data.
#print(account_data)

# Grab historical prices.
#aapl_prices = ib_client.market_data_history(conid=['265598'], period='1d', bar='5min')
from functions.func import IBClient

#callAccount()

ib_client = IBClient()
#ib_client.set_server()
ret = ib_client.is_authenticated()
ib_client.get_account()
ib_client.server_accounts()
print(ret)
quote_fields = [55, 7296, 7295, 86, 70, 71, 84, 31]
aapl_current_prices = ib_client.get_market(conids = ['265598'], since = '0', fields = quote_fields)
print(aapl_current_prices)
ib_client.portfolio_accounts()

from datetime import date
import tornado.escape
import tornado.ioloop
import tornado.web
 
class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        response = { 'version': '1.0.0',
                     'last_build':  date.today().isoformat() }
        self.write(response)
 
class GetAuth(tornado.web.RequestHandler):
    def get(self):
        ib_client = IBClient()
        ret = ib_client.is_authenticated()

        self.write(ret)
class GetAccount(tornado.web.RequestHandler):
    def get(self):
        ib_client = IBClient()
        ret = ib_client.get_account()

        self.write(ret[0])
class GetMarket(tornado.web.RequestHandler):
    def get(self):
        ib_client = IBClient()
        ret = ib_client.get_market(conids = ['265598'], since = '0', fields = quote_fields)

        self.write(ret[0])
class GetPortfolio(tornado.web.RequestHandler):
    def get(self):
        ib_client = IBClient()
        ret = ib_client.portfolio_accounts()

        self.write(ret[0])        

application = tornado.web.Application([
    (r"/getAuth", GetAuth),
    (r"/getAccount", GetAccount),
    (r"/getMarket", GetMarket),
    (r"/getPortfolio", GetPortfolio),
    (r"/version", VersionHandler)
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
