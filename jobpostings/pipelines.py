# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import pandas as pd
import requests
from jobpostings import settings
temp_list = []


class JobpostingsPipeline(object):
    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        temp_list.append(item)
        return item

    def close_spider(self, spider):
        if len(temp_list) > 0:
            df_web = pd.DataFrame(temp_list)
            data_json = df_web.to_json()
            data = {"request": "upsert", "data": data_json}
            res = requests.post(url=settings.PIPELINES_URL, json=data)
            print(f"The response status：{res.status_code}")

