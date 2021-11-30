import scrapy
import os
import pandas as pd
import re
import datetime

class GainersSpider(scrapy.Spider):
    mcm_url = 'https://coinmarketcap.com/gainers-losers/'
    name = 'gainers'
    allowedDomains = ['coinmarketcap.com']
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN":1,
        "DEFAULT_REQUEST_HEADERS":{
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
        },
        "LOG_ENABLED": True,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }
    def start_requests(self):
#         self.initialize_sheets()
        start_urls = [self.mcm_url]
        
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
            
    def parse(self, response):
        df = self.extract_table_values(response)
        self.save_page(df)        
        yield response.follow(self.mcm_url, callback=self.parse)
        
    def save_page(self, dataframe):

        directory = "./data/"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        now_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        outname = now_str + '.csv'
        filename = os.path.join(directory, outname)    

        dataframe.to_csv(filename)

    def extract_table_values(self, response):
        gainers_table = response.xpath('//div[h3/text() = "Top Gainers"]').css('table')
        t_values = gainers_table.css('tbody td p::text, tbody td span::text, tbody td::text').getall()
        t_chunks = list(chunks(t_values, 7))
        df = pd.DataFrame(data=t_chunks)
        df[7] = datetime.datetime.now()
        print(df)
        return df



def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
