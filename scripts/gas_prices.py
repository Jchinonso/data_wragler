import requests
import os
import datetime
import csv
from bs4 import BeautifulSoup


class GasPriceClass:
    BASE_URL = 'https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm'

    def __init__(self):

        self.table_data = None
        self.daily_prices = []
        self.monthly_prices = []

    def loadHtml(self):
        self.get_html()

    def get_html(self):
        """
          retrieve records form web page 
          :return void
        """
        try:
            req = requests.get(self.BASE_URL)
            if req.status_code == 200:
                html = BeautifulSoup(req.text, 'html.parser')
                self.table_data = html
                print('Getting html content...')
            else:
                print('Server error...')
        except:
            print('An error occurred...')

    def get_daily_prices(self):
        """
          get all daily prices 
          :return void
        """
        daily_prices = []
        for row in self.table_data.find_all('tr'):
            all_date = row.find('td', {'class': 'B6'})
            if all_date:
                date = all_date.text.strip()
                daily_prices.append([date, [item.text for item in row.find_all('td', class_='B3')]])
        self.daily_prices = self.assign_price_to_date(daily_prices)

    def get_monthly_prices(self):
        """
          get all monthly prices 
          :return void
        """
        self.get_daily_prices()
        monthly_prices = []
        for data in self.daily_prices:
            first_day_of_month = int(data[0].split('-')[2])
            if(first_day_of_month == 1):
                month = data[0][0: 8]
                monthly_prices.append([month, data[1] ])
        self.monthly_prices = monthly_prices
            
    def create_csv(self, file_name, data):
        """
          create csv file  
          :return void
        """
        if(os.path.exists(file_name)):
            print('File Already Exist')
        with open(file_name, 'w', newline='') as file:
            file.write('DATE, PRICE \n')
            writer = csv.writer(file)
            for item in data: 
                writer.writerow(item)

    def assign_price_to_date(self, data):

        """
          extract each day from date and assign 
          price to each day
          :return array
        """
        date_price_array = []
        for item in data:
            start_date = item[0].replace('- ',' ').replace('-', ' ').split(' ')[0:3]
            format_start_date = datetime.datetime.strptime('-'.join(start_date), '%Y-%b-%d')
            increment_day = 0
            for price in item[1]:
                day = format_start_date + datetime.timedelta(days = increment_day)
                date_price_array.append([day.strftime('%Y-%b-%d'), price])
                increment_day += 1
        return date_price_array



def main():
    g = GasPriceClass()
    g.loadHtml()
    g.get_monthly_prices()
    g.create_csv('csv/daily_prices.csv', g.daily_prices)
    g.create_csv('csv/monthly_prices.csv', g.monthly_prices)


if __name__ == '__main__':
    main()
