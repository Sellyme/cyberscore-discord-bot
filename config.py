test_channel = 930473063043178586
cs_submissions_channel = 930586269237530654 #Cyberscore `#submissions`
cs_mod_channel = 199790440784986122 #Cyberscore `#staff-central`
cs_pokemon_channel = 157232307286048768 #Cyberscore `#pokémon`
ps_submissions_channel = 936392388102991892 #Pokemon Snap `#cyberscore-submissions`
leaderboard_channel = 930981438638133269

ps_server_id = 671836713236299826

#all frequencies are in seconds
submissions_frequency = 120 #frequency to scrape the latest submissions page
leaderboard_frequency = 60*60 #frequency to scrape the CSR leaderboard
timeout = 20 #number of seconds to wait for page load before abandoning an update
#leaderboard_frequency polls every hour
#but waits until midnight UTC (or 24 hours since the last update) before updating

bot_owner_name = "Sellyme"
bot_owner_discriminator = "1963" #these can have leading zeroes, so need to be a string