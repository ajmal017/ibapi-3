
import requests
import urllib3
import certifi
from typing import Union
from typing import List
import json

import urllib
from typing import Dict
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(category=InsecureRequestWarning)


class IBClient():

    def __init__(self) -> None:
        self.account = "DU1937358"
        self.api_version = 'v1/'
        ib_gateway_host = r"https://localhost"
        ib_gateway_port = r"5000"
        self.ib_gateway_path = ib_gateway_host + ":" + ib_gateway_port

    def _headers(self, mode: str = 'json') -> Dict:
        """
                    Returns a dictionary of default HTTP headers for calls to TD Ameritrade API,
                    in the headers we defined the Authorization and access token.
                    NAME: mode
                    DESC: Defines the content-type for the headers dictionary.
                          default is 'json'. Possible values are ['json','form']
                    TYPE: String
                """

        if mode == 'json':
            headers = {'Content-Type': 'application/json'}
        elif mode == 'form':
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        return headers

    def _build_url(self, endpoint: str) -> str:
        """
                    builds a url for a request.
                    NAME: endpoint
                    DESC: The URL that needs conversion to a full endpoint URL.
                    TYPE: String
                    RTYPE: String
                """

        # otherwise build the URL
        return urllib.parse.unquote(
            urllib.parse.urljoin(self.ib_gateway_path, self.api_version) + r'portal/' + endpoint)

    def _make_request(self, endpoint: str, req_type: str, params: Dict = None) -> Dict:
        url = self._build_url(endpoint=endpoint)

        if req_type == 'POST' and params is None:

            response = requests.post(url, headers=self._headers(mode='json'), verify=False)
        elif req_type == 'GET' and params is None:
            response = requests.get(url, headers=self._headers(mode='json'), verify=False)
        elif req_type == 'GET' and params is not None:
            response = requests.get(url, headers=self._headers(mode='json'), params=params, verify=False)
        elif req_type == 'POST' and params is not None:
            headers = self._headers(mode='json')
            response = requests.post(url, headers=headers, json=params, verify=False)
            print(response.text)
            status_code = response.status_code
        #print(status_code)
        return response.json()

    def _prepare_arguments_list(self, parameter_list: List[str]) -> str:
        """
            Some endpoints can take multiple values for a parameter, this
            method takes that list and creates a valid string that can be
            used in an API request. The list can have either one index or
            multiple indexes.
            NAME: parameter_list
            DESC: A list of paramater values assigned to an argument.
            TYPE: List
            EXAMPLE:
            SessionObject.prepare_arguments_list(parameter_list = ['MSFT', 'SQ'])
        """

        # validate it's a list.
        if type(parameter_list) is list:
            # specify the delimiter and join the list.
            delimiter = ','
            parameter_list = delimiter.join(parameter_list)

        return parameter_list

    def is_authenticated(self) -> Dict:
        # define request components
        endpoint = 'iserver/auth/status'
        req_type = 'POST'
        content = self._make_request(endpoint=endpoint, req_type=req_type)

        return content

    def get_account(self) -> Dict:

        endpoint = 'portfolio/accounts'
        req_type = 'GET'
        content = self._make_request(endpoint=endpoint, req_type=req_type)

        return content

    def get_market(self, conids: List[str], since: str, fields: List[str]) -> Dict:

        endpoint = 'iserver/marketdata/snapshot'
        req_type = 'GET'
        conids_joined = self._prepare_arguments_list(parameter_list=conids)
        if fields is not None:
            fields_joined = ",".join(str(n) for n in fields)
        else:
            fields_joined = ""
        # define the parameters
        if since is None:
            params = {
                'conids': conids_joined,
                'fields': fields_joined
            }
        else:
            params = {
                'conids': conids_joined,
                'since': since,
                'fields': fields_joined
            }
        content = self._make_request(endpoint=endpoint, req_type=req_type, params=params)

        return content

    def server_accounts(self):
        """
            Returns a list of accounts the user has trading access to, their
            respective aliases and the currently selected account. Note this
            endpoint must be called before modifying an order or querying
            open orders.
        """

        # define request components
        endpoint = 'iserver/accounts'
        req_type = 'GET'
        content = self._make_request(endpoint=endpoint, req_type=req_type)

        return content

    def set_server(self) -> bool:
        print(self.account)
        server_update_content = self.update_server_account(account_id=self.account, check=False)
        return True

    def update_server_account(self, account_id: str, check: bool = False) -> Dict:
        endpoint = 'iserver/account'
        req_type = 'POST'
        params = {'acctId': account_id}
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)
        return content

        #FUNDAMENTAL DATA ENDPOINTS


    def fundamentals_summary(self, conid: str) -> Dict:
        """Grabs a financial summary of a company.
        Return a financial summary for specific Contract ID. The financial summary
        includes key ratios and descriptive components of the Contract ID.
        Arguments:
        ----        
        conid {str} -- The contract ID.
        Returns:
        ----
        {Dict} -- The response dictionary.
        """

        # define request components
        endpoint = 'iserver/fundamentals/{}/summary'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def fundamentals_financials(self, conid: str, financial_statement: str, period: str = 'annual') -> Dict:
        """
            Return a financial summary for specific Contract ID. The financial summary
            includes key ratios and descriptive components of the Contract ID.
            NAME: conid
            DESC: The contract ID.
            TYPE: String
            NAME: financial_statement
            DESC: The specific financial statement you wish to request for the Contract ID. Possible
                  values are ['balance','cash','income']
            TYPE: String
            NAME: period
            DESC: The specific period you wish to see. Possible values are ['annual','quarter']
            TYPE: String
            RTYPE: Dictionary
        """

        # define the period
        if period == 'annual':
            period = True
        else:
            period = False

        # Build the arguments.
        params = {
            'type':financial_statement,
            'annual':period
        }

        # define request components
        endpoint = 'fundamentals/financials/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content

    def fundamentals_key_ratios(self, conid: str) -> Dict:
        """
            Returns analyst ratings for a specific conid.
            NAME: conid
            DESC: The contract ID.
            TYPE: String
        """

        # Build the arguments.
        params = {
            'widgets':'key_ratios'
        }

        # define request components
        endpoint = 'fundamentals/landing/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content

    def fundamentals_dividends(self, conid: str) -> Dict:
        """
            Returns analyst ratings for a specific conid.
            NAME: conid
            DESC: The contract ID.
            TYPE: String
        """

        # Build the arguments.
        params = {
            'widgets':'dividends'
        }

        # define request components
        endpoint = 'fundamentals/landing/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content

    def fundamentals_esg(self, conid: str) -> Dict:
        """
            Returns analyst ratings for a specific conid.
            NAME: conid
            DESC: The contract ID.
            TYPE: String
        """

        # Build the arguments.
        params = {
            'widgets':'esg'
        }

        # define request components
        endpoint = 'fundamentals/landing/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content

    """
        DATA ENDPOINTS
    """

    def data_news(self, conid: str) -> Dict:
        """
            Return a financial summary for specific Contract ID. The financial summary
            includes key ratios and descriptive components of the Contract ID.
            NAME: conid
            DESC: The contract ID.
            TYPE: String
        """

        # Build the arguments.
        params = {
            'widgets':'news',
            'lang':'en'
        }

        # define request components
        endpoint = 'fundamentals/landing/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content

    def data_ratings(self, conid: str) -> Dict:
        """
            Returns analyst ratings for a specific conid.
            NAME: conid
            DESC: The contract ID.
            TYPE: String
        """

        # Build the arguments.
        params = {
            'widgets':'ratings'
        }

        # define request components
        endpoint = 'fundamentals/landing/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content

    def _data_events(self, conid: str) -> Dict:
        """
            Returns analyst ratings for a specific conid.
            NAME: conid
            DESC: The contract ID.
            TYPE: String
        """

        # Build the arguments.
        params = {
            'widgets':'ratings'
        }

        # define request components
        endpoint = 'fundamentals/landing/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content

    def data_ownership(self, conid: str) -> Dict:
        """
            Returns analyst ratings for a specific conid.
            NAME: conid
            DESC: The contract ID.
            TYPE: String
        """

        # Build the arguments.
        params = {
            'widgets':'ownership'
        }

        # define request components
        endpoint = 'fundamentals/landing/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content

    def data_competitors(self, conid: str) -> Dict:
        """
            Returns analyst ratings for a specific conid.
            NAME: conid
            DESC: The contract ID.
            TYPE: String
        """

        # Build the arguments.
        params = {
            'widgets':'competitors'
        }

        # define request components
        endpoint = 'fundamentals/landing/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content

    def data_analyst_forecast(self, conid: str) -> Dict:
        """
            Returns analyst ratings for a specific conid.
            NAME: conid
            DESC: The contract ID.
            TYPE: String
        """

        # Build the arguments.
        params = {
            'widgets':'analyst_forecast'
        }

        # define request components
        endpoint = 'fundamentals/landing/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content

    def market_data_history(self, conid: str, period: str, bar: str) -> Dict:
        """
            Get history of market Data for the given conid, length of data is controlled by period and 
            bar. e.g. 1y period with bar=1w returns 52 data points.
            NAME: conid
            DESC: The contract ID for a given instrument. If you don't know the contract ID use the
                  `search_by_symbol_or_name` endpoint to retrieve it.
            TYPE: String
            NAME: period
            DESC: Specifies the period of look back. For example 1y means looking back 1 year from today.
                  Possible values are ['1d','1w','1m','1y']
            TYPE: String
            NAME: bar
            DESC: Specifies granularity of data. For example, if bar = '1h' the data will be at an hourly level.
                  Possible values are ['5min','1h','1w']
            TYPE: String
        """

        # define request components
        endpoint = 'iserver/marketdata/history'
        req_type = 'GET'
        params = {
            'conid':conid,
            'period':period,
            'bar':bar
        }
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = params)

        return content


    """
        SERVER ACCOUNTS ENDPOINTS
    """


    def server_account_pnl(self):
        """
            Returns an object containing PnLfor the selected account and its models 
            (if any).
        """

        # define request components
        endpoint = 'iserver/account/pnl/partitioned'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    """
        CONTRACT ENDPOINTS
    """

    def symbol_search(self, symbol: str) -> Dict:
        """
            Performs a symbol search for a given symbol and returns information related to the
            symbol including the contract id.
        """

        # define the request components
        endpoint = 'iserver/secdef/search'
        req_type = 'POST'
        payload = {'symbol':symbol}
        content = self._make_request(endpoint = endpoint, req_type = req_type, params= payload)

        return content

    def contract_details(self, conid: str) -> Dict:
        """
            Get contract details, you can use this to prefill your order before you submit an order.
            NAME: conid
            DESC: The contract ID you wish to get details for.
            TYPE: String
            RTYPE: Dictionary
        """

        # define the request components
        endpoint = '/iserver/contract/{conid}/info'.format(conid = conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def contracts_definitions(self, conids: List[str]) -> Dict:
        """
            Returns a list of security definitions for the given conids.
            NAME: conids
            DESC: A list of contract IDs you wish to get details for.
            TYPE: List<Integer>
            RTYPE: Dictionary
        """

        # define the request components
        endpoint = '/trsrv/secdef'
        req_type = 'POST'
        payload = {
            'conids':conids
            }
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)

        return content

    def futures_search(self, symbols: List[str]) -> Dict:
        """
            Returns a list of non-expired future contracts for given symbol(s).
            NAME: Symbol
            DESC: List of case-sensitive symbols separated by comma.
            TYPE: List<String>
            RTYPE: Dictionary
        """

        # define the request components
        endpoint = '/trsrv/futures'
        req_type = 'GET'
        payload = {'symbols':"{}".format(','.join(symbols))}
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)

        return content        
        
    """
        PORTFOLIO ACCOUNTS ENDPOINTS
    """


    def portfolio_accounts(self):
        """
            In non-tiered account structures, returns a list of accounts for which the 
            user can view position and account information. This endpoint must be called prior 
            to calling other /portfolio endpoints for those accounts. For querying a list of accounts 
            which the user can trade, see /iserver/accounts. For a list of subaccounts in tiered account 
            structures (e.g. financial advisor or ibroker accounts) see /portfolio/subaccounts.
        """

        # define request components
        endpoint = 'portfolio/accounts'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    def portfolio_sub_accounts(self):
        """
            Used in tiered account structures (such as financial advisor and ibroker accounts) to return a 
            list of sub-accounts for which the user can view position and account-related information. This 
            endpoint must be called prior to calling other /portfolio endpoints for those subaccounts. To 
            query a list of accounts the user can trade, see /iserver/accounts.
        """

        # define request components
        endpoint = r'​portfolio/subaccounts'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    def portfolio_account_info(self, account_id: str) -> Dict:
        """
            Used in tiered account structures (such as financial advisor and ibroker accounts) to return a 
            list of sub-accounts for which the user can view position and account-related information. This 
            endpoint must be called prior to calling other /portfolio endpoints for those subaccounts. To 
            query a list of accounts the user can trade, see /iserver/accounts.
            NAME: account_id
            DESC: The account ID you wish to return info for.
            TYPE: String
        """

        # define request components
        endpoint = r'portfolio/{}/meta'.format(account_id)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    def portfolio_account_summary(self, account_id: str) -> Dict:
        """
            Returns information about margin, cash balances and other information 
            related to specified account. See also /portfolio/{accountId}/ledger. 
            /portfolio/accounts or /portfolio/subaccounts must be called 
            prior to this endpoint.
            NAME: account_id
            DESC: The account ID you wish to return info for.
            TYPE: String
        """

        # define request components
        endpoint = r'portfolio/{}/summary'.format(account_id)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    def portfolio_account_ledger(self, account_id: str) -> Dict:
        """
            Information regarding settled cash, cash balances, etc. in the account's 
            base currency and any other cash balances hold in other currencies. /portfolio/accounts 
            or /portfolio/subaccounts must be called prior to this endpoint. The list of supported 
            currencies is available at https://www.interactivebrokers.com/en/index.php?f=3185.
            NAME: account_id
            DESC: The account ID you wish to return info for.
            TYPE: String
        """

        # define request components
        endpoint = r'portfolio/{}/ledger'.format(account_id)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    def portfolio_account_allocation(self, account_id: str) -> Dict:
        """
            Information about the account's portfolio allocation by Asset Class, Industry and 
            Category. /portfolio/accounts or /portfolio/subaccounts must be called prior to 
            this endpoint.
            NAME: account_id
            DESC: The account ID you wish to return info for.
            TYPE: String
        """

        # define request components
        endpoint = r'portfolio/{}/allocation'.format(account_id)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    def portfolio_accounts_allocation(self, account_ids: List[str]) -> Dict:
        """
            Similar to /portfolio/{accountId}/allocation but returns a consolidated view of of all the 
            accounts returned by /portfolio/accounts. /portfolio/accounts or /portfolio/subaccounts must 
            be called prior to this endpoint.
            NAME: account_ids
            DESC: A list of Account IDs you wish to return alloacation info for.
            TYPE: List<String>
        """

        # define request components
        endpoint = r'portfolio/allocation'
        req_type = 'POST'
        payload = account_ids
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)

        return content


    def portfolio_account_positions(self, account_id: str, page_id: int = 0) -> Dict:
        """
            Returns a list of positions for the given account. The endpoint supports paging, 
            page's default size is 30 positions. /portfolio/accounts or /portfolio/subaccounts 
            must be called prior to this endpoint.
            NAME: account_id
            DESC: The account ID you wish to return positions for.
            TYPE: String
            NAME: page_id
            DESC: The page you wish to return if there are more than 1. The
                  default value is `0`.
            TYPE: String
            ADDITIONAL ARGUMENTS NEED TO BE ADDED!!!!!
        """

        # define request components
        endpoint = r'portfolio/{}/positions/{}'.format(account_id, page_id)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    #
    #   RENAME THIS
    #

    def portfolio_account_position(self, account_id: str, conid: str) -> Dict:
        """
            Returns a list of all positions matching the conid. For portfolio models the conid 
            could be in more than one model, returning an array with the name of the model it 
            belongs to. /portfolio/accounts or /portfolio/subaccounts must be called prior to 
            this endpoint.
            NAME: account_id
            DESC: The account ID you wish to return positions for.
            TYPE: String
            NAME: conid
            DESC: The contract ID you wish to find matching positions for.
            TYPE: String
        """

        # define request components
        endpoint = r'portfolio/{}/position/{}'.format(account_id, conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    #
    #   GET MORE DETAILS ON THIS
    #

    def portfolio_positions_invalidate(self, account_id: str) -> Dict:
        """
            Invalidates the backend cache of the Portfolio. ???
            NAME: account_id
            DESC: The account ID you wish to return positions for.
            TYPE: String
        """
        
        # define request components
        endpoint = r'portfolio/{}/positions/invalidate'.format(account_id)
        req_type = 'POST'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    def portfolio_positions(self, conid: str) -> Dict:
        """
            Returns an object of all positions matching the conid for all the selected accounts. 
            For portfolio models the conid could be in more than one model, returning an array 
            with the name of the model it belongs to. /portfolio/accounts or /portfolio/subaccounts 
            must be called prior to this endpoint.
            NAME: conid
            DESC: The contract ID you wish to find matching positions for.
            TYPE: String          
        """

        # define request components
        endpoint = r'portfolio/positions/{}'.format(conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    """
        TRADES ENDPOINTS
    """


    def trades(self):
        """
            Returns a list of trades for the currently selected account for current day and 
            six previous days.
        """

         # define request components
        endpoint = r'iserver/account/trades'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    """
        ORDERS ENDPOINTS
    """


    def get_live_orders(self):
        """
            The end-point is meant to be used in polling mode, e.g. requesting every 
            x seconds. The response will contain two objects, one is notification, the 
            other is orders. Orders is the list of orders (cancelled, filled, submitted) 
            with activity in the current day. Notifications contains information about 
            execute orders as they happen, see status field.
        """

        # define request components
        endpoint = r'iserver/account/orders'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    def place_order(self, account_id: str, order: dict) -> Dict:
        """
            Please note here, sometimes this end-point alone can't make sure you submit the order 
            successfully, you could receive some questions in the response, you have to to answer 
            them in order to submit the order successfully. You can use "/iserver/reply/{replyid}" 
            end-point to answer questions.
            NAME: account_id
            DESC: The account ID you wish to place an order for.
            TYPE: String
            NAME: order
            DESC: Either an IBOrder object or a dictionary with the specified payload.
            TYPE: IBOrder or Dict
        """

        if type(order) is dict:
            order = order
        else:
            order = order.create_order()

        # define request components
        endpoint = r'iserver/account/{}/order'.format(account_id)
        req_type = 'POST'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = order)

        return content


    def place_orders(self, account_id: str, orders: List[Dict]) -> Dict:
        """
            An extension of the `place_order` endpoint but allows for a list of orders. Those orders may be
            either a list of dictionary objects or a list of IBOrder objects.
            NAME: account_id
            DESC: The account ID you wish to place an order for.
            TYPE: String
            NAME: orders
            DESC: Either a list of IBOrder objects or a list of dictionaries with the specified payload.
            TYPE: List<IBOrder Object> or List<Dictionary>
        """

        # EXTENDED THIS
        if type(orders) is list:
            orders = orders
        else:
            orders = orders

        # define request components
        endpoint = r'iserver/account/{}/orders'.format(account_id)
        req_type = 'POST'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = orders)

        return content

    def place_order_scenario(self, account_id: str, order: dict) -> Dict:
        """
            This end-point allows you to preview order without actually submitting the 
            order and you can get commission information in the response.
            NAME: account_id
            DESC: The account ID you wish to place an order for.
            TYPE: String
            NAME: order
            DESC: Either an IBOrder object or a dictionary with the specified payload.
            TYPE: IBOrder or Dict
        """

        if type(order) is dict:
            order = order
        else:
            order = order.create_order()

        # define request components
        endpoint = r'iserver/account/{}/order/whatif'.format(account_id)
        req_type = 'POST'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = order)

        return content


    def modify_order(self, account_id: str, customer_order_id: str, order: dict) -> Dict:
        """
            Modifies an open order. The /iserver/accounts endpoint must first
            be called.
            NAME: account_id
            DESC: The account ID you wish to place an order for.
            TYPE: String
            NAME: customer_order_id
            DESC: The customer order ID for the order you wish to MODIFY.
            TYPE: String
            NAME: order
            DESC: Either an IBOrder object or a dictionary with the specified payload.
            TYPE: IBOrder or Dict
        """

        if type(order) is dict:
            order = order
        else:
            order = order.create_order()

        # define request components
        endpoint = r'iserver/account/{}/order/{}'.format(account_id, customer_order_id)
        req_type = 'POST'
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = order)

        return content


    def delete_order(self, account_id: str, customer_order_id: str) -> Dict:
        """
            Deletes the order specified by the customer order ID.
            NAME: account_id
            DESC: The account ID you wish to place an order for.
            TYPE: String
            NAME: customer_order_id
            DESC: The customer order ID for the order you wish to DELETE.
            TYPE: String
        """
        # define request components
        endpoint = r'iserver/account/{}/order/{}'.format(account_id, customer_order_id)
        req_type = 'DELETE'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content


    """
        ORDERS ENDPOINTS
    """


    def get_scanners(self):
        """
            Returns an object contains four lists contain all parameters for scanners.
            RTYPE Dictionary
        """
        # define request components
        endpoint = r'iserver/scanner/params'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def run_scanner(self, instrument: str, scanner_type: str, location: str, size: str = '25', filters: List[dict] = None) -> Dict:
        """
            Run a scanner to get a list of contracts.
            NAME: instrument
            DESC: The type of financial instrument you want to scan for.
            TYPE: String
            NAME: scanner_type
            DESC: The Type of scanner you wish to run, defined by the scanner code.
            TYPE: String
            NAME: location
            DESC: The geographic location you wish to run the scan. For example (STK.US.MAJOR)
            TYPE: String
            NAME: size
            DESC: The number of results to return back. Defaults to 25.
            TYPE: String
            NAME: filters
            DESC: A list of dictionaries where the key is the filter you wish to set and the value is the value you want set
                  for that filter.
            TYPE: List<Dictionaries>
            RTYPE Dictionary
        """

        # define request components
        endpoint = r'iserver/scanner/run'
        req_type = 'POST'
        payload = {
            "instrument": instrument,
            "type": scanner_type,
            "filter":filters,
            "location": location,
            "size": size
        }
        print(payload)

        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)

        return content

    def customer_info(self):
        """
            Returns Applicant Id with all owner related entities     
            RTYPE Dictionary
        """

        # define request components
        endpoint = r'ibcust/entity/info'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def get_unread_messages(self):
        """
            Returns the unread messages associated with the account.
            RTYPE Dictionary
        """

        # define request components
        endpoint = r'fyi/unreadnumber'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def get_subscriptions(self):
        """
            Return the current choices of subscriptions, we can toggle the option.
            RTYPE Dictionary
        """

        # define request components
        endpoint = r'fyi/settings'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def change_subscriptions_status(self, type_code: str, enable: bool = True) -> Dict:
        """
            Turns the subscription on or off.
            NAME: type_code
            DESC: The subscription code you wish to change the status for.
            TYPE: String
            NAME: enable
            DESC: True if you want the subscription turned on, False if you want it turned of.
            TYPE: Boolean
            RTYPE Dictionary
        """

        # define request components
        endpoint = r'fyi/settings/{}'
        req_type = 'POST'
        payload = {'enable': enable}
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)

        return content

    def subscriptions_disclaimer(self, type_code: str) -> Dict:
        """
            Returns the disclaimer for the specified subscription.
            NAME: type_code
            DESC: The subscription code you wish to change the status for.
            TYPE: String
            RTYPE Dictionary
        """

        # define request components
        endpoint = r'fyi/disclaimer/{}'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def mark_subscriptions_disclaimer(self, type_code: str) -> Dict:
        """
            Sets the specified disclaimer to read.
            NAME: type_code
            DESC: The subscription code you wish to change the status for.
            TYPE: String
            RTYPE Dictionary
        """

        # define request components
        endpoint = r'fyi/disclaimer/{}'
        req_type = 'PUT'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def subscriptions_delivery_options(self):
        """
            Options for sending fyis to email and other devices.
            RTYPE Dictionary
        """

        # define request components
        endpoint = r'fyi/deliveryoptions'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def mutual_funds_portfolios_and_fees(self, conid: str) -> Dict:
        """
            Grab the Fees and objectives for a specified mutual fund.
            NAME: conid
            DESC: The Contract ID for the mutual fund.
            TYPE: String
            RTYPE Dictionary
        """

        # define request components
        endpoint = r'fundamentals/mf_profile_and_fees/{mutual_fund_id}'.format(mutual_fund_id = conid)
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def mutual_funds_performance(self, conid: str, risk_period: str, yield_period: str, statistic_period: str) -> Dict:
        """
            Grab the Lip Rating for a specified mutual fund.
            NAME: conid
            DESC: The Contract ID for the mutual fund.
            TYPE: String
            NAME: yield_period
            DESC: The Period threshold for yield information
                  possible values: ['6M', '1Y', '3Y', '5Y', '10Y']
            TYPE: String
            NAME: risk_period
            DESC: The Period threshold for risk information
                  possible values: ['6M', '1Y', '3Y', '5Y', '10Y']
            TYPE: String
            NAME: statistic_period
            DESC: The Period threshold for statistic information
                  possible values: ['6M', '1Y', '3Y', '5Y', '10Y']
            TYPE: String
            RTYPE Dictionary
        """

        # define request components
        endpoint = r'fundamentals/mf_performance/{mutual_fund_id}'.format(mutual_fund_id = conid)
        req_type = 'GET'
        payload = {
            'risk_period':None,
            'yield_period':None,
            'statistic_period':None
        }
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)

        return content
