test_channel = 930473063043178586
submissions_channel = 930586269237530654
leaderboard_channel = 930981438638133269

#all frequencies are in seconds
submissions_frequency = 120 #frequency to scrape the latest submissions page
leaderboard_frequency = (60*60) - 5 #frequency to scrape the CSR leaderboard
#leaderboard_frequency polls every hour
#but waits until midnight UTC (or 24 polls) before updating
#this is to avoid it running immediately on restarts
#we also actually poll *slightly* more than hourly
#otherwise scraping delays could cause a check at 11:59:58 and then a check at 01:00:03

bot_owner_name = "Sellyme"
bot_owner_discriminator = "1963" #these can have leading zeroes, so need to be a string