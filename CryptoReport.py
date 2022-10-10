import json
import os
import requests
import time
from datetime import datetime

class Requests:
#Creo una classe che va a richiamare i dati forniti da Coinmarketcap

    def __init__(self):
        self.url = ''
        self.params = {}
        self.headers = {}

    def fetch_currencies_data(self):
        response = requests.get(url=self.url, headers=self.headers, params=self.params).json()
        return response['data']
#La funzione fetchCurrenciesData fa partire la richiesta alle API di CoinMarketCap

class Reports(Requests):
#Creo una classe composta da funzioni contenenti i paramtetri di cui ho bisogno

    def __init__(self):
        super(Reports, self).__init__()
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'd7a0d5e2-b3f4-4823-90fc-05c534d3a060',
        }
        self.reports = self.get_reports()


# Funzione che restituisce la criptovaluta con il volume maggiore nelle ultime 24H:
    def highest_currency(self):
        self.params = {
            'start': 1,
            'limit': 1,
            'sort': 'volume_24h',
            'sort_dir': 'desc',
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        return currencies[0]

# Funzione che restituisce le migliori 10 criptovalute per incremento percentuale nelle ultime 24H:
    def  best_currencies(self):
        self.params = {
            'start': 1,
            'limit': 10,
            'sort': 'percent_change_24h',
            'sort_dir': 'desc',
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        return currencies

#Funzione che restituisce le peggiori 10 criptovalute per incremento percentuale nelle ultime 24H:
    def worst_currencies(self):
        self.params = {
            'start': 1,
            'limit': 10,
            'sort': 'percent_change_24h',
            'sort_dir': 'asc',
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        return currencies

#Funzione che restituisce la quantità di denaro necessaria per acquistare una unità di ciascuna delle prime 20 criptovalute:
    def price_20_best_currencies(self):
        amount = 0
        self.params = {
            'start': 1,
            'limit': 20,
            'sort': 'market_cap',
            'sort_dir': 'desc',
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        for currency in currencies:
            amount += currency['quote']['USD']['price']
        return round(amount, 2)

#Funzione che restituisce la somma necessaria per acquistare una unità di tutte le criptovalute il cui volume delle ultime 24 ore è superiore a 76.000.000$
    def price_higher_volume_currencies(self):
        amount = 0
        self.params = {
            'start': 1,
            'limit': 100,
            'volume_24h_min': 76000000,
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        for currency in currencies:
            amount += currency['quote']['USD']['price']
        return round(amount, 2)

    def gain_top_currencies(self):
        initial_amount = 0
        final_amount = 0
        self.params = {
            'start': 1,
            'limit': 20,
            'sort': 'market_cap',
            'sort_dir': 'desc',
            'convert': 'USD'
        }
#Calcolo la percentuale di guadagno o perdita se avessi comprato una unità di ciascuna delle prime 20 criptovalute il giorno prima:
        currencies = self.fetch_currencies_data()
        for currency in currencies:
            old_price = currency['quote']['USD']['price'] / (1 + (currency['quote']['USD']['percent_change_24h'] / 100))
            initial_amount += old_price
            final_amount += currency['quote']['USD']['price']
        gain = round((((final_amount - initial_amount) / initial_amount) * 100), 1)
        return gain

#Creo un dizionario che ci servirà nel ciclo che andrò a creare per stampare i risultati richiesti:
    def get_reports(self):
        reports = {
            'most_traded': self.highest_currency(),
            'best_10': self. best_currencies(),
            'worst_10': self.worst_currencies(),
            'amount_top_20': self.price_20_best_currencies(),
            'amount_by_volumes': self.price_higher_volume_currencies(),
            'gain_top_20': self.gain_top_currencies()
        }

        return reports

#Funzione che crea il file Json nominato con la data in cui stampiamo i risultati:
def make_json(report):
    file_name = time.strftime('Report_%d_%m_%Y.json', time.localtime())
    script_dir = os.path.dirname(os.path.abspath(__file__))
    destination_dir = os.path.join(script_dir, 'report')
    path = os.path.join(destination_dir, file_name)

    try:
        os.mkdir(destination_dir)
    except OSError:
        pass
    with open(path, 'w') as f:
        json.dump(report, f)


def main():
    seconds = 60
    minutes = 60
    hours = 24

#Per ultmo creo un ciclo infinito che stampa i risultati ogni 24 ore:
    while True:
        report = Reports()

        print(f"Daily report of crypto supplied by CoinMarketCap of: {datetime.now()}")
        print("")
        print(f"The cryptocurrency with the highest volume in the last 24 hours is: "
              f"{report.reports['most_traded']['symbol']} "
              f"with a volume of {round(report.reports['most_traded']['quote']['USD']['volume_24h'], 0)}$")
        print("")
        print("Top 10 cryptocurrencies by percentage increase over the last 24 hours are: ")
        for currency in report.reports['best_10']:
            print(currency['symbol'], f"{round(currency['quote']['USD']['percent_change_24h'], 2)}%")
        print("")
        print("Worst 10 cryptocurrencies by percentage increase in the last 24 hours are: ")
        for currency in report.reports['worst_10']:
            print(currency['symbol'], f"{round(currency['quote']['USD']['percent_change_24h'], 2)}%")
        print("")
        print(f"Total price of 20 best currencies of CoinMarketCap ranking: {report.reports['amount_top_20']}$")
        print(f"Total price of currencies that have a daily volume higher than 76M$: "
              f"{report.reports['amount_by_volumes']}$")
        print(f"Percentage change of 20 best currencies of CoinMarketCap ranking: "
              f"{report.reports['gain_top_20']}%")
        print("------------------------------------------------------------")

        make_json(report.reports)
        time.sleep(seconds * minutes * hours)

if __name__ == '__main__':
    main()