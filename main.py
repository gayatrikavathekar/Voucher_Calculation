import logging
import datetime
from pandas import read_parquet
import pandas as pd
from collections import Counter
from flask import request
import json
from flask import Flask

def getSegment(data_response):
    country = data_response['country_code']
    customer_segment = data_response['segment_name']
    # calculate the segment using customer data to find out to which segment the customer belong
    if customer_segment == 'recency_segment':
        recency_segment = ''
        date_time_obj = datetime.datetime.strptime(data_response['last_order_ts'], '%Y-%m-%d %H:%M:%S')
        segment = (pd.to_datetime('today').date() - date_time_obj.date()).days
        # check the segment bucket
        print("returning recency segment: ", segment)
        if segment in range (30,60):
            recency_segment = "30-60"
        elif segment in range (61,90):
            recency_segment = "61-90"
        elif segment in range (91,120):
            recency_segment = "91-120"
        elif segment in range (121,180):
            recency_segment = "121-180"
        elif segment >= 181:
            recency_segment = "180+"
        return recency_segment,country,customer_segment

    elif customer_segment == 'frequent_segment':
        frequent_segment = ''
        segment = data_response['total_orders']
        # check the segment bucket
        print("returning frequency segment: ", segment)
        if segment in range(0,4):
            frequent_segment = "0-4"
        elif segment in range(5,13):
            frequent_segment = "5-13"
        if segment in range(14,37):
            frequent_segment = "14-37"
        return frequent_segment,country,customer_segment


def dataPreparation(country):
    # import the data
    df = read_parquet("data.parquet.gzip")

    # check if na values are present. replace if necessary
    df.voucher_amount = df.voucher_amount.fillna(0)
    df.total_orders = df.total_orders.replace('', 0)

    # change the datatypes of columns
    df['timestamp'] = pd.to_datetime(df.timestamp).dt.tz_convert(None)
    df['last_order_ts'] = pd.to_datetime(df.last_order_ts).dt.tz_convert(None)
    df['first_order_ts'] = pd.to_datetime(df.first_order_ts).dt.tz_convert(None)

    # filter the data on the basis of the country : Peru
    df = df[df['country_code'] == country]

    # calculate the recency considering the last date of purchase and current date
    df['current_date'] = pd.to_datetime('today')
    df['recency'] = (df['current_date'] - df['last_order_ts']).dt.days

    # create recency segments
    df.loc[df['recency'].any() >= 30 & df['recency'].any() <= 60, 'recency_segment'] = "30-60"
    df.loc[df['recency'].any() >= 61 & df['recency'].any() <= 90, 'recency_segment'] = "61-90"
    df.loc[df['recency'].any() >= 91 & df['recency'].any() <= 120, 'recency_segment'] = "91-120"
    df.loc[df['recency'].any() >= 121 & df['recency'].any() <= 180, 'recency_segment'] = "121-180"
    df.loc[df['recency'] >= 181, 'recency_segment'] = "180+"

    # create frequency segments
    df.loc[df['total_orders'].any() >= 0 & df['total_orders'].any() <= 4, 'frequency_segment'] = "0-4"
    df.loc[df['total_orders'].any() >= 5 & df['total_orders'].any() <= 13, 'frequency_segment'] = "5-13"
    df.loc[df['total_orders'].any() >= 14 & df['total_orders'].any() <= 37, 'frequency_segment'] = "14-37"
    return df


def calculateVoucherAmount(df,segment,customer_segment):
    # filter the dataframe as per the segment name
    df = df[df[customer_segment] == segment]
    # get the most used voucher for the segment
    c = Counter(df['voucher_amount'])
    return c.most_common(1)[0][0]




app = Flask(__name__)
@app.route("/customerData")
def getData():
    try:
        customer_id = request.args['customer_id']
        country_code = request.args['country_code']
        last_order_ts = request.args['last_order_ts']
        first_order_ts = request.args['first_order_ts']
        total_orders = request.args['total_orders']
        segment_name = request.args['segment_name']

        customer_data = {"customer_id": customer_id, "country_code": country_code, "last_order_ts": last_order_ts,
                "first_order_ts": first_order_ts,
                "total_orders": total_orders,
                "segment_name": segment_name
                }
        logging.info(customer_data)
        data_response = customer_data

        # get the segment
        segment, country, customer_segment = getSegment(data_response)
        
        # get the cleaned dataframe
        df = dataPreparation(country)

        # calculate the voucher
        voucher_amount = calculateVoucherAmount(df, segment, customer_segment)

        data = {'voucher_amount': voucher_amount}
        logging.info(data)
        return json.dumps(data)
    except Exception as e:
        logging.error(e)
        return 'internal error'


if __name__ == '__main__':
    app.run(debug=True)

