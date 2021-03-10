import requests
import smtplib
from email.message import EmailMessage

#### Variables ####
STOCK_NAME = "SPY"
COMPANY_NAME = "S&P 500 ETF"


#### Email Info ####
# TODO: Update your email, password and recipient
my_email = "INSERT YOUR EMAIL"
# Don't let anyone see your password!
password = "INSERT YOUR PASSWORD"
recipient = "INSERT THE EMAIL YOU'RE SENDING IT TO"

#### News API ####
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API = "INSERT YOUR NEWS API"

news_parameters = {
    "apiKey": NEWS_API,
    "qInTitle": COMPANY_NAME,
}

#### Stocks API ####
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
API_STOCKS = "INSERT YOUR STOCKS API"

stocks_parameters = {
    "function" : "TIME_SERIES_DAILY",
    "symbol" : STOCK_NAME,
    "apikey" : API_STOCKS
}

# Calling the Stock API
response = requests.get(STOCK_ENDPOINT, params = stocks_parameters)
response.raise_for_status()
data = response.json()

#Get yesterday's closing stock price. Hint: You can perform list comprehensions on Python dictionaries. e.g. [new_value for (key, value) in dictionary.items()]
series_of_stocks = data["Time Series (Daily)"]

# Making a dictionary with a month of stock data
stock_dict = {date: stock_info for (date, stock_info) in series_of_stocks.items()}

# Getting yesterday's closing stock price
yesterday_closing_price = list(stock_dict.values())[1]["4. close"]
yesterday_closing_price = float(yesterday_closing_price)

#Get the day before yesterday's closing stock price
day_before_yesterday_closing_price = list(stock_dict.values())[2]["4. close"]
day_before_yesterday_closing_price = float(day_before_yesterday_closing_price)

#Find the positive difference between 1 and 2. e.g. 40 - 20 = -20, but the positive difference is 20. Hint: https://www.w3schools.com/python/ref_func_abs.asp
difference_price = round(yesterday_closing_price - day_before_yesterday_closing_price,1)
print(difference_price)
up_down = None

if difference_price > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

#Work out the percentage difference in price between closing price yesterday and closing price the day before yesterday.
percentage_difference = round((difference_price / day_before_yesterday_closing_price) * 100, 1)

#This variable will help us to see if the action dropped or increased 5%
absolute_percentage_difference = round(abs((difference_price / day_before_yesterday_closing_price) * 100), 1)
print(f"The absolute Difference is {absolute_percentage_difference}")

#if absolute_percentage_difference is greater than 5, send news
if absolute_percentage_difference >= 3:

    # Calling the news API
    news_response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()["articles"]
    first_three_articles = news_data[:3]

    # List comprehension to get the first 3 article's headline and description
    # new_list = [new_item for item in list]
    dict_first_three_articles = {f"{article['title']}":f"{article['description']}" for (article) in first_three_articles}
    #dict_first_three_articles = {(k).encode("utf-8"): (v).encode("utf-8") for (k,v) in dict_first_three_articles.items()}
    url_list = [url["url"] for url in first_three_articles]

    for headline, description in dict_first_three_articles.items():
        print(headline)

    for url in url_list:
        print(url)

    url_count = 0

    # Sending email
    for headline, description in dict_first_three_articles.items():
        subject = f"{STOCK_NAME} stock:{up_down}{percentage_difference}% ,{headline}"
        body = f"{description}\n\nURL to the article: {url_list[url_count]}\n No son enchiladas..."

        # build-up email details using email.message module
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = my_email
        message["To"] = recipient
        message.set_content(body)

        # send the message via smtp using details above
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(my_email, password=password)
            connection.send_message(message)

        url_count += 1

#Optional TODO: Format the message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

