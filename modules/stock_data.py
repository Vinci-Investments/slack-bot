# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 20:24:00 2018

@author: Maxence
"""

import requests 
import pandas as pd
import numpy as np

from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go


lines_api_key = [line.rstrip('\n') for line in open('alpha_vantage.key')]
API_KEY = lines_api_key[0]

lines_plotly_key = [line.rstrip('\n') for line in open('plotly.key')]
PLOTLY_USER = lines_plotly_key[0]
PLOTLY_PASSWORD = lines_plotly_key[1]


TIME_INTERVALS = {'Intraday' : 'TIME_SERIES_INTRADAY', 'Daily' :'TIME_SERIES_DAILY', 
                  'Weekly' : 'TIME_SERIES_WEEKLY', 'Monthly' : 'TIME_SERIES_MONTHLY'}


def get_stock(symbol, interval):
    
    """
    Returns a pandas DataFrame with (Open, High, Low, Close, Volume) columns
    for the specific symbol and specific time_interval.
    Returns None if an exception occurs.
    """
    
    try:
        
        time_interval = TIME_INTERVALS[interval]
        
        if(time_interval == TIME_INTERVALS['Intraday']):
            json_data = requests.request('GET', 'https://www.alphavantage.co'+
                        '/query?function=TIME_SERIES_INTRADAY&symbol='+symbol+
                        '&interval=1min&apikey='+API_KEY).json()
            data_frame = pd.DataFrame.from_records(json_data['Time Series (1min)'])
        
        else:
            json_data = requests.request('GET', 'https://www.alphavantage.co'+
                        '/query?function='+time_interval+'&symbol='+symbol+
                        '&apikey='+API_KEY).json()
            
            data_key = ''
            
            if(time_interval == TIME_INTERVALS['Daily']):
                data_key = 'Time Series (Daily)'
            elif(time_interval == TIME_INTERVALS['Weekly']):
                data_key = 'Weekly Time Series'
            else:
                data_key = 'Monthly Time Series'
            
            data_frame = pd.DataFrame.from_records(json_data[data_key])
            
        data_frame = data_frame.transpose()
        data_frame.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return data_frame
    
    except:
        print("Error while loading data")
        return None



def create_plotting(symbol, interval):
    
    py.sign_in(PLOTLY_USER, PLOTLY_PASSWORD)
    
    df = get_stock(symbol, interval)
    
    if(df is None):
        
        return ("Error", None)
    
    else:
        
        df = df.astype(float)
        
        High = max(df['High'])
        Low = min(df['Low'])
        data_mean = np.round(df['Close'].mean(),2)
        data_std = np.round(df['Close'].std(), 4)
        
        return_object = {'high' : High, 'low': Low, 'mean' : data_mean, 'std' : data_std}
        
        trace_stock = go.Ohlc(x=df.index,
                        open=df.Open,
                        high=df.High,
                        low=df.Low,
                        close=df.Close)
        
        trace_volume = go.Scatter(
            x=df.index.values,
            y=df['Volume'],
            line = dict(
                color = ('rgb(22, 96, 167)'),
                width = 4)
        )
        
        stock_label = symbol + ' ' + interval + ' interval graph' 
        
        
        fig = tools.make_subplots(rows=4, cols=1, specs=[[{'rowspan' : 3}], [None], [None], [{}]],
                                  shared_xaxes=True, shared_yaxes=True,
                                  vertical_spacing=0.12, 
                                  subplot_titles=(stock_label, '', '', 'Trading volume'))
        
        fig.append_trace(trace_stock, 1, 1)
        fig.append_trace(trace_volume, 4, 1)
        
        fig['layout'].update(xaxis = dict(rangeslider = dict(visible = False)), showlegend=False)
        path = 'data/plotting/'+symbol+'_graph.png'
        py.image.save_as(fig, filename=path)
        return (symbol+'_graph.png', return_object)



        