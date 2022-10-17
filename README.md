# NFT Auction Alarm
A friend of mine is really into the NFT space and told me about its potential and how he wants to be part of it, but of course he is also interested in earning money with it. So he told me how he is looking at auctions on [OpenSea](https://opensea.io/) and what are his key points on which he decides to buy a NFT or not. At this time I got more into advanced coding and saw the opportunity to test my skills on webscraping and OOP and to automate a 24/7 auction alarm for my friend.

## Method
Baisically what the Auction Alarm does is that it takes all the auctions that we give the Auction Alarm Container (AAC), it opens the NFT projects websites, scrapes all the informations and decides if an alarm via email is send or not.
The neccessary information of the NFT projects which are going to be scraped are stored in a json-file in a way shown here:

    {  
      "1": {  
        "name": "invisible friends",  
      "url": "https://opensea.io/collection/invisiblefriends",  
      "thresh_time": 9000,  
      "thresh_percentage": 100  
      },  
      "2": {  
        "name": "bored apes",  
      "url": "https://opensea.io/collection/boredapeyachtclub",  
      "thresh_time": 9000,  
      "thresh_percentage": 100  
      }  
    }
So for each element all the informations are gathered and a decision is made, whether to ssend an email or not. If the alarm hits and an email is send the object is put to a list, so the Auction Alarm knows on which NFT object a email was already sent in the next iteration.
To run the bot 24/7 I set up a VM via AWS so none of us had to let their notebook run all the time. On top of that I connected the bot with the Google Drive API to implement a simple interface for my friend to communicate with the auction bot. Therefore a second .json-file is implemeted which is used as an interface in the way that the AAC reads it every iteration and takes its orders. The file looks like this:

    {  
      "continue": 1,  
      "receiver": ["put-your-target-mail-here@mail.com"],  
      "administrator": ["this-is-used-for-debugging@gmail.com"],  
      "hrs_to_reset": 12,  
      "reset_status": 1  
    }
Where continue just tells the AAC to continue and the receiver is the mail to which the AAC sends an alarm. Administrator is just a second email for debug puropose, which gets the alarm and the log of the iteration. hrs_to_reset is used to reset the list of objects for which an alarm was already triggered.

## Tech
In this project the following technologies were used

 - **Webdriver for Google Chrome** - [Link](https://chromedriver.chromium.org/downloads)
 - **selenium** - To automate navigating through the websites
 - **beautiful soup** - for web scraping
 - **gspread** - Google Docs API
 - **smtplib** - To send emails

## Summary
This project was really fun, because I had such a steep learn curve and it felt so good to present the project later to my friend and the moment he wrote me that he got an email from my bot. Sadly just two weeks after he started to use the bot the whole Crypto crashed and the NFT market even more and the whole behaviour of the market changed with it and the bot lost its attraction immediatly. But instead of him becoming a welathy NFT holder I gained knwoledge.
