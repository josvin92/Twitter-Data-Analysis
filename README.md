# Twitter-Sentiment, Hashtag and Source-Analysis

Task 1: Collecting Twitter Data
Collect some Twitter data by using Twitter APIs such as the tweepy search API.
By using the tweepy search API, collect at least 1,000 tweets containing a keyword “donald trump”, and another 1,000 tweets containing “joe biden”. Also, store the collected data in JSON format. 
Add the following conditions when you use the search API:
▪ Tweets should be written in English.
▪ Remove/filter retweets to get more meaningful information if you can get at least 1,000 tweets.

Some other important things to note are:
1. api.search returns a list of dictionary like objects containing a lots of attributes for a tweet such as the tweet itself, when it was created, the name of the user who sent the tweet, how many followers the user has etc. A list of some of the attributes and a brief description can be found in this tutorial.
2. The search parameter q=’\”{}\” -filter:retweets’.format(search_term): This ensures that the tweets returned contain the exact search phrase and that retweets are not returned in the results as it can result in duplicate data.
3. The tweet_mode=extended parameter ensures that we retrieve full text of each tweet not the preview along with a url. Leaving this out gets you a short version of the tweet followed by ellipses (…) and a url to the tweet.
4. tweet_details[‘created’] = tweet.created_at.strftime(“%Y-%m-%d %H:%M:%S”): The object returned when tweet.created_at is retrieved is a datetime object. However since I’m storing my tweets in a json file and since json doesn’t support datetime object, I had to convert it to a text/string format. That is why the .strftime("%Y-%m-%d %H:%M:%S") function is called.

Task 2: Exploratory Analysis
1. Extract the average length of all the tweets of each candidate from the ‘len’ column that we created, using numpy’s mean function.

2. Find the maximum number of likes from the 'likes' column and the maximum number of retweets from the 'RTs' column using numpy's max function and print the tweet, the number of likes for that tweet and the number of characters in that tweet.

3. Time Series Analysis - the number of tweets over time of Donald Trump/Joe Biden
4. Sentiment Analysis - using TextBlob
5. Sentiment Polarity Score over Time – Time Series
6. Number of followers by Source – Pie Chart
7. Top 10 most frequent hashtags from positive tweets – Bar Chart
8. Top 10 most frequent hashtags from negative tweets – Bar Chart
9. Finally, Based on the above analysis, who will be elected in the 2020 presidential election.
