# Author : Jeff Jones
#
# This uses 'plotly' and 'chart studios' to create interactive graphs of the Sentiment analysis
#
import datetime
import re
import pandas as pd
import chart_studio
username = 'need to register with plotly.com'
api_key = 'your api key'

chart_studio.tools.set_credentials_file(username=username, api_key=api_key)
import plotly.express as px
import chart_studio.plotly as py
import chart_studio.tools as tls
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

def Initialize_Setup() :
    global df
    global New_Title
# Import data

    date_time_obj = datetime.now()
    date_str = str(date_time_obj.date())
    date_str = re.sub(r'-', '', date_str)  # remove the dashes
    Reddit_Stat_String_FileName += date_str + '_Reddit_Stats.csv'
    Reddit_Stats_df = pd.read_csv(Reddit_Stat_String_FileName)


    # Extract date from the df
    TimeStamp = Reddit_Stats_df.iloc[2,0]
    date_time_obj = datetime.strptime(TimeStamp, '%d/%m/%Y %H:%M:%S')
    New_Title = "Equity Ticker and Sentiment Review "+str(date_time_obj.date())
    New_Title += "<br>" + "Top 25 Stocks mentioned by the popular sub-reddit WallStreetBets"
    New_Title += "<br>" + "and the associated sentiment scores"
    df = Reddit_Stats_df.head(25)
    return df

def Plot_Results(df) :
#Generate Initial Figure / plot
    Graph_Color = df['Sentiment_Text']
    fig = px.bar(df, x="Symbol", y="Raw_Hits", title=New_Title, color = 'Sentiment_Text')

#Ensure that multiple data sets order their plots the same
    fig.update_xaxes(categoryorder='array', categoryarray= df['Symbol'])

#Add the scatter graph of sentiment in combination with the bar graph
    fig.add_trace(go.Scatter(
    x=df['Symbol'],
    y=df['Sentiment_Degree'],
    mode='markers',
    showlegend=False,
    marker_color = 'black',
    marker_symbol='square-dot',
    name = "Sentiment Score",
    yaxis="y2"
    ))

# Update the second Y axis with appropriate labels, etc.
    fig.update_layout(
    legend_title_side = 'top',
    legend_title_text = "Sentiment Colors",
#    showlegend = False,
    hovermode = 'closest',
    yaxis2=dict(
        title="Sentiment Degree",
        titlefont=dict(
            color="black"
        ),
        tickfont=dict(
            color="black"
        ),
        overlaying="y",
        side="right"
    ))


#When plotting online, the plot and data will be saved to your cloud account.
#There are two methods for plotting online: py.plot() and py.iplot().
#Both options create a unique url for the plot and save it in your Plotly account.
#Use py.plot() to return the unique url and optionally open the url.
#Use py.iplot() when working in a Jupyter Notebook to display the plot in the notebook.
#Plotly allows you to create graphs offline and save them locally.
#There are also two methods for interactive plotting offline: plotly.io.write_html() and plotly.io.show().
#Use plotly.io.write_html() to create and standalone HTML that is saved locally and opened inside your web browser.
#Use plotly.io.show() when working offline in a Jupyter Notebook to display the plot in the notebook.
    py.plot(fig)
    return


# don't run the script if it is just being imported into another script
if __name__ == '__main__':
    frame = Initialize_Setup()
    Plot_Results(frame)

