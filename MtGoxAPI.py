"""
    Mt. Gox Python API v0.01 by Jonas Rudloff

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import urllib
import urllib2
import json

class ServerError(Exception):

    def __init__(self, ret):
        self.ret = ret

    def __str__(self):
        return "Server error: %s" % self.ret



class UserError(Exception):

    def __init__(self, errmsg):
        self.errmsg = errmsg

    def __str__(self):
        return self.errmsg



class Client:

    def __init__(self, username="", password="", verbose=True):

        self.username = username
        self.password = password
        self.verbose  = verbose
        self.buff     = ""
        self.base_url = "https://mtgox.com"
        self.timeout  = 10


    def perform(self, path, params={}):
        """perform the operation 'path' with params. returns the result"""
        url = "%s/%s" % (self.base_url, path)
        if len(params) > 0:
            post_data = urllib.urlencode(params.items())
        else:
            post_data = None
        req = urllib2.Request(url, post_data, {"User-Agent": "MtGoxAPI"})
        return urllib2.urlopen(url, post_data).read()

    def request(self, path, params={}):
        """perform the request and check for any errors"""
        ret = json.loads(self.perform(path, params))

        if "error" in ret:
            raise UserError(ret["error"])
        else:
            return ret


    # The Public API

    def get_ticker(self):
        """get the ticker"""
        return self.request("code/data/ticker.php")["ticker"]


    def get_depth(self):
        """get the market depth"""
        return self.request("code/data/getDepth.php")

    def get_trades(self):
        """get all 'recent' trades"""
        return self.request("/code/data/getTrades.php")


    # The Private API

    def get_balance(self):
        """get your balances. returns a dict of currency and their balances"""
        params = {"name":self.username, "pass":self.password}
        return self.request("code/getFunds.php", params)
        
    @property
    def usd(self):
        """your USD balance"""
        return float(self.get_balance()["usds"])
    
    @property
    def btc(self):
        """your BTC balance"""
        return float(self.get_balance()["btcs"])

    def get_orders(self):
        """get all your orders. returns a dict of the oids and their specifications"""
        params = {"name":self.username, "pass":self.password}
        ret = self.request("code/getOrders.php", params)
        orders = {}
        for i in ret["orders"]:
            orders[i["oid"]] = i
        return orders


    def sell_btc(self, amount, price):
        """sell some btc"""
        self._notify("Issuing a sell order for %s BTC at price of %s USD" % (str(amount), str(price)))

        #if amount < 1:
        #    self._notify("Minimun amount is 1BTC")
        #    return 0

        params = {
            "name":   self.username,
            "pass":   self.password,
            "amount": str(amount),
            "price":  str(price)
        }

        return self.request("code/sellBTC.php", params)["oid"]


    def buy_btc(self, amount, price):
        """buy some btc"""
        self._notify("Issuing a buy order for %s BTC at a price pf %s USD" % (str(amount), str(price)))

        params = {
            "name":   self.username, 
            "pass":   self.password,
            "amount": str(amount),
            "price":  str(price)
        }

        return self.request("code/buyBTC.php", params)["oid"]


    def _cancel_order(self, oid, typ):
        
        params = {
            "name": self.username, 
            "pass": self.password, 
            "oid":  str(oid), 
            "type": str(typ)
        }
        
        return self.request("code/cancelOrder.php", params)


    def cancel_order(self, oid):
        """cancel the order 'oid'"""
        orders = self.get_orders()
        order = orders[oid]

        return self._cancel_order(order["oid"], order["type"])


    def _notify(self, message):
        """notifys when some thing happens. may be overwritten."""
        if self.verbose:
            print message
