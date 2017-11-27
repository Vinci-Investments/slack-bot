# Slack bot

This is a slack bot which send every days on the general channel a summary of key financial datas such as indices, commodities or forex, plus top news from Bloomberg.

## Prerequisites

In order to make proper requests to Slack services we need the [slackclient](https://github.com/slackapi/python-slackclient) and [requests](https://github.com/requests/requests) librairies. We then need the [emoji](https://github.com/carpedm20/emoji/) librairy in order to bring reactions in slack messages. Finally, we need the [weather-api](https://github.com/AnthonyBloomer/weather-api) librairy in order to get the weather datas.

```
pip install slackclient
pip install requests
pip install emoji
pip install weather-api
```

## Setting up the bot

In order to use bot in your Slack workspace, you need to [create one](https://api.slack.com/bot-users), note its private token and to invite it in the channel you want it to interract with (type ```invite @name_of_your_bot name_of_the_channel ``` in the channel to invite the bot).
For security reasons, we cant put bot token or id on github (please not that if you post a Slack bot token on github, Slack will disactivate the bot). To bypass this, you will need to create several .key file that will be located in the exact same repository that the slack.py file. First of all you will need to create a file named bot.key which contains in the first line the name of your bot and in the second line its id (short sequence of numbers and/or letters). You will then need to create a slack.key file which contains the private token of your bot.
Last step, in order to get top news from Bloomberg, we are using the [news-api](https://newsapi.org/) webservices. You will then need to create a token on their web page and to put it in a file named news.key.

## Gallery
