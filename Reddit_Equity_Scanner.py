# Author : Jeff Jones
# Please note that a user must register their own Reddit application to obtain a client Id and
# a key string (called a 'secret') to initialize the API.  You can't just run this code without taking these steps.
# see lines 108-111

import praw
import pandas as pd
import os
import re
from datetime import datetime

from textblob import TextBlob

from wordcloud import WordCloud

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

def Initialize_Setup() :
    NasDaq = './NASDAQ_Symbols.csv'
    Nyse = './NYSE_Symbols.csv'
    Amex = './AMEX_Symbols.csv'
    ProcessedPosts = './Reddit_Posts.txt'

    date_time_obj = datetime.now()
    date_str = str(date_time_obj.date())
    date_str = re.sub(r'-', '', date_str)  # remove the dashes
    Reddit_Stats = './' + date_str + '_Reddit_Stats.csv'
    global Posts_Output, Stats_Output
    Posts_Output = open(ProcessedPosts, "w")
    Stats_Output = open(Reddit_Stats, "w")

    dfs = []

    dfs.append(pd.read_csv(NasDaq))
    dfs.append(pd.read_csv(Nyse))
    dfs.append(pd.read_csv(Amex))

    # dataframe to maintain statistics for each symbol
    global frame
    frame = pd.concat(dfs)

    # adds a column Counter to track the number of occurrences of each ticker in the reddit posts
    frame['Counter'] = 0


    #add a set of text variables to append all titles and comments for a symbol
    frame['Commentary'] = ' '

    #add a variable to store the polarity and subjectivity score for a symbol
    frame['Polarity'] = 0
    frame['Subjectivity'] = 0

    frame['ResultingSentiment'] = " "

    frame['Recent_Price_Change'] = 0.0
    return frame


def Sentiment_Text_Score(polarity):
    if polarity == 0:
        return "Neutral"
    elif polarity < 0:
        return "Negative"
    elif polarity > 0 and polarity < .27 :
        return "Positive"
    else :
        return "Very_Positive"


# function to clean the text from other references that start with @, #, url's
def cleanTxt(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)  # remove @mentions
    text = re.sub(r'#', '', text)  # removing anything with a '#'
    text = re.sub(r'https?:\/\/\S+', '', text)  # remove the hyper links

    return text

# function to search reddit posts for symbols and to count the occurrences
def Symbol_Lookup(incoming_text):
    RowSymbol = 0

    HitorMiss = False
    post_text = cleanTxt(incoming_text)

    # Posts which are all upper case result in false positives
    if post_text.isupper() :
        return HitorMiss

    for EachSymbol in frame["Symbol"]:
        if ((post_text.startswith(EachSymbol + " "))
                or (post_text.endswith(" " + EachSymbol))
                or (post_text.find(" " + EachSymbol + " ") != -1)):
            # print("We have a hit ", post_text, EachSymbol)
            # accumulate all the text with hits into the dataframe
            frame.iloc[RowSymbol, 12] += post_text
            frame.iloc[RowSymbol, 11] += 1
            HitorMiss = True
        RowSymbol += 1

    return HitorMiss



def Process_Reddit_Posts() :
    # Use the PRAW library connect to reddit with a registered API.
    # The ID's are provided when you fill out their form to register your app
    reddit = praw.Reddit(client_id='need a client ID', client_secret='need to obtain via registration',
                     user_agent='create your own apps name')

    # This retrieves 100 posts and allows access to all the comments.
    # The limit is 100
    Top1000Posts = reddit.subreddit('WallStreetBets').hot(limit=10)

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    Posts_Output.write("Starting Reddit WallStreetBets Scanning : %s\n" % dt_string)

    Post_Counter = 0
    for post in Top1000Posts:
        print(Post_Counter)

        comment_counter = post.num_comments
        RowSymbol = 0
        Post_Counter += 1

        Posts_Output.write("%s\n" % post.title.encode('utf-8'))
        Posts_Output.write("%s\n" % post.selftext.encode('utf-8'))

        titleHit = Symbol_Lookup(post.title)
        selftextHit = Symbol_Lookup(post.selftext)

        Posts_Output.write("Number of comments is : %d \n" % comment_counter)

        CommentHit = False
        if comment_counter > 0:
            for comment in post.comments.list():
                if isinstance(comment, praw.models.reddit.more.MoreComments):
                    comment_text = " "
                    continue
                else:
                    temp_string = str(comment.body)
                    Posts_Output.write("%s \n" % temp_string.encode('utf-8'))
                    comment_text = cleanTxt(comment.body)
                    CommentHit = Symbol_Lookup(comment_text)

        if (titleHit or selftextHit or CommentHit):
            temp_string = str("One or more hits in post " + str(Post_Counter))
            Posts_Output.write("%s \n" % temp_string)

    # develop the subjectivity and polarity of the text for each set of posts that had a symbol found
    # Polarity can range from -1 to 1, with -1, positive values indicating positive sentiment and negative values indicating negative sentiment
    # Subjectivity can range from 0 to 1, with 0 being factual information with values ranging close to 1 being subjective
    RowSymbol = 0

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    frame.sort_values('Counter', ascending=False, inplace=True)
    temp_string = "Date_Time," + "Symbol," + "Company_Name," + "Raw_Hits," + "Sentiment_Degree," + "Sentiment_Text," + "Hits"
    print(temp_string)
    Stats_Output.write("%s \n" % temp_string)
    for EachSymbol in frame["Symbol"]:
        if frame.iloc[RowSymbol, 11] > 0:
            frame.iloc[RowSymbol, 13] = TextBlob(frame.iloc[RowSymbol, 12]).sentiment.polarity
            frame.iloc[RowSymbol, 14] = TextBlob(frame.iloc[RowSymbol, 12]).sentiment.subjectivity
            frame.iloc[RowSymbol, 15] = Sentiment_Text_Score(frame.iloc[RowSymbol, 13])
            temp_string = str(
                dt_string + "," + frame.iloc[RowSymbol, 0] + ", " + str(frame.iloc[RowSymbol, 1]) + ", " + str(
                frame.iloc[RowSymbol, 11]) + ", " + str(frame.iloc[RowSymbol, 13]) + ", " + str(
                frame.iloc[RowSymbol, 15]))
            print(temp_string)
            Stats_Output.write("%s \n" % temp_string)
        RowSymbol += 1

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    Posts_Output.write("Completed Reddit WallStreetBets Scanning : %s\n" % dt_string)

    Stats_Output.close()
    Posts_Output.close()
    return

# don't run the script if it is just being imported into another script
if __name__ == '__main__':
    frame = Initialize_Setup()
    Process_Reddit_Posts()
