import pytrends
from pytrends.request import TrendReq
import pandas as pd
import time
import datetime
import random
from flask import Response
import matplotlib.pyplot as plt


def create_figure(kw):
    from_to = "2018-01-01 2021-01-01"
    pytrends = TrendReq(hl='en-US', tz=360)

    pytrends.build_payload([kw], timeframe=from_to)
    trends = pytrends.interest_over_time()

    if all(trends.isPartial == False):
        del trends['isPartial']

    fig = plt.figure(figsize = (9,5))
    dig = fig.add_subplot(1,1,1)

    trends.plot(ax=dig)
    plt.ylabel('Frequency')
    plt.xlabel('Year')

    plt.ylim((0,100))

    plt.legend(loc='lower left')
    plt.style.use('ggplot')
    plt.savefig('static/plot.png')
    

def getTrends(kw):
    pytrend = TrendReq()
    pytrends = TrendReq(hl='es-US', tz=360)

    kw_list = [kw]
    pytrends.build_payload(kw_list, cat=2, timeframe='today 3-y', geo='', gprop='')
    return pytrends.interest_over_time()
