
import praw
import pandas as pd
import os
import re
from datetime import datetime

NasDaq = './NASDAQ_Symbols.csv'
Nyse = './NYSE_Symbols.csv'
Amex = './AMEX_Symbols.csv'
ProcessedPosts = './Reddit_Posts.txt'
Posts_Output = open(ProcessedPosts, "w")

dfs = []

dfs.append(pd.read_csv(NasDaq))
dfs.append(pd.read_csv(Nyse))
dfs.append(pd.read_csv(Amex))

frame = pd.concat(dfs)

frame['Counter'] = 0


# function to clean the text from other references that start with @, #, url's
def cleanTxt(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)  # remove @mentions
    text = re.sub(r'#', '', text)  # removing anything with a '#'
    text = re.sub(r'https?:\/\/\S+', '', text)  # remove the hyper links

    return text

# function to search reddit posts for symbols and to count the occurrences
def Symbol_Lookup(title, body):
    RowSymbol = 0

    HitorMiss = False
    post_title = cleanTxt(title)
    post_body = cleanTxt(body)

    # Special conditions to avoid false positives
    # Don't process posts which are all upper case as can easily
    # have uppercase symbol strings embedded unintentionally
    if (post_title.isupper()):
        return HitorMiss
    if (post_body.isupper()):
        return HitorMiss

    for EachSymbol in frame["Symbol"]:
        if ((post_title.startswith(EachSymbol + " "))
                or (post_title.endswith(" " + EachSymbol))
                or (post_title.find(" " + EachSymbol + " ") != -1)):
            # print("We have a hit in title ", post.title, EachSymbol)
            frame.iloc[RowSymbol, 11] += 1
            HitorMiss = True
        # If not found in titles, check the body of the submission
        elif ((post_body.endswith(" " + EachSymbol))
              or (post_body.find(" " + EachSymbol + " ") != -1)
              or (post_body.startswith(EachSymbol + " "))):
            # print("We have a hit in post body ", EachSymbol)
            frame.iloc[RowSymbol, 11] += 1
            HitorMiss = True
        RowSymbol += 1

    return HitorMiss

# Use the PRAW library connect to reddit with a registered API.
# The ID's are provided when you fill out their form to register your app
reddit = praw.Reddit(client_id='Uk8bEsY94zqc-A', client_secret='rUztaipnKZjq8bn0t77Wofq3HC7LbA',
                     user_agent='Equity_Scanner')

# This retrieves 1000 posts and allows access to all the comments.
# The limit is 1000
Top100Posts = reddit.subreddit('WallStreetBets').hot(limit=100)

Post_Counter = 0
for post in Top100Posts:
    print(Post_Counter)

    comment_counter = post.num_comments
    RowSymbol = 0
    Post_Counter += 1

    Posts_Output.write("%s\n" % post.title.encode('utf-8'))
    Posts_Output.write("%s\n" % post.selftext.encode('utf-8'))

    Symbol_Lookup(post.title, post.selftext)
    Posts_Output.write("Number of comments is : %d \n" % comment_counter)

    if comment_counter > 0:
        for comment in post.comments.list():
            if isinstance(comment, praw.models.reddit.more.MoreComments):
                comment_text = " "
                continue
            else:
                temp_string = str(comment.body)
                Posts_Output.write("%s \n" % temp_string.encode('utf-8'))
                comment_text = cleanTxt(comment.body)
            Symbol_Lookup(comment_text, " ")

RowSymbol=0
frame.sort_values('Counter',ascending=False,inplace=True)
for EachSymbol in frame["Symbol"] :
    if frame.iloc[RowSymbol,11] > 0 :
        temp_string = str(frame.iloc[RowSymbol,0] + ", " + str(frame.iloc[RowSymbol,1]) + ", " + str(frame.iloc[RowSymbol,11]))
        print(temp_string)
        Posts_Output.write("%s \n" % temp_string)
    RowSymbol += 1

Posts_Output.close()