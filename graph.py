from plotly import graph_objects as go
from plotly import subplots as subplt
import numpy as np

def plot_data(df):
  """Plot data for ticker dataframe"""

  # Construct 2x1 Plotly figure
  fig = subplt.make_subplots(rows=2, cols=1)

  # Plot ticker price candles
  fig.append_trace(
    go.Candlestick(
      x=df.index,
      open=df['Open'],
      high=df['High'],
      low=df['Low'],
      close=df['Close'],
      increasing_line_color='#4def00',
      decreasing_line_color='red',
      name='Day Price'
    ), row=1, col=1
  )

  # Plot MACD line
  fig.append_trace(
    go.Scatter(
      x=df.index,
      y=df['MACD'],
      line=dict(color='#4def00', width=2),
      name='MACD',
      legendgroup=2
    ), row=2, col=1
  )

  # Plot signal line
  fig.append_trace(
    go.Scatter(
      x=df.index,
      y=df['Signal'],
      line=dict(color='gray', width=2),
      name='Signal',
      legendgroup=2
    ), row=2, col=1
  )

  # Plot hisogram bars
  fig.append_trace(
    go.Bar(
      x=df.index,
      y=df['Histogram'],
      marker_color=(np.where(df['Histogram'] < 0, 'red', '#4def00')),
      name='Histogram'
    ), row=2, col=1
  )

  # Format figure layout
  layout = go.Layout(
    plot_bgcolor='#efefef',
    font_family='Monospace',
    font_color='#000',
    font_size=20,
    xaxis=dict(rangeslider=dict(visible=False))
  )

  fig.update_layout(layout)
  fig.show()