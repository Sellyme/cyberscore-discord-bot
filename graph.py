import os
import cmfn

def generate_lead_progression(board, sort="plat"):  # WIP
    p = "D:/Programming/Cyberscore/Discord bot/leaderboards/archive/" + board + "/"
    leads = []
    for filename in os.listdir(p):
        if not validate_board_sort(board, filename, sort):
            continue

        with open(p + filename, "r+") as f:
            data = cmfn.load_leaderboard(f)
            # todo - restructure load_leaderboard output so this doesn't have to iterate over everything
            # ideally we have some kind of indexing by position
            lead = 0
            for username in data:
                user_entry = data[username]
                if user_entry['pos'] == 1:
                    lead += user_entry['score']
                elif user_entry['pos'] == 2:
                    lead -= user_entry['score']

            dt = cmfn.convert_timestamp_to_excel(filename)

            # below line won't work on boards with custom sort params
            leads.append({"dt": dt, "diff": lead})
    return leads

def generate_top_n(n, board, sort="plat"):  # WIP
    # sort is for medal/trophy boards
    # gold/silver/bronze sorts are kept in the same folder
    # so we need to specify which to use
    # TODO - actually look into if trophy sort is working correctly?

    p = "D:/Programming/Cyberscore/Discord bot/leaderboards/archive/" + board + "/"
    lb_entries = {}
    users = set()

    for filename in os.listdir(p):
        if not validate_board_sort(board, filename, sort):
            continue

        with open(p + filename, "r+") as f:
            data = cmfn.load_leaderboard(f, True)
            dt = cmfn.convert_timestamp_to_excel(filename)
            lb_entry = {}
            for pos in range(1, n + 1):
                row = data[pos]
                users.add(row['name'])
                lb_entry[row['name']] = row['score']
            lb_entries[dt] = lb_entry

    output = ""

    # print header row
    output += "Timestamp"
    for user in users:
        output += "\t" + user
    output += "\n"
    # and print data
    for update in lb_entries:
        output += update
        entry = lb_entries[update]
        for user in users:
            if user not in entry:
                output += "\t"
            else:
                output += "\t" + str(entry[user])
        output += "\n"

    return output

def validate_board_sort(board, filename, sort):
    # returns True if a board filename matches the request sort, False otherwise
    board = board.lower()
    if board == "medals" or board == "trophy":
        if sort:
            if sort not in filename:
                # and if we've set a different sort, discard any not containing that
                return False
        else:
            if filename.count("_") > 1:
                # if there's a suffix indicating board size_type, it's not plat
                return False
    return True

#actual graphing happens below
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#import numpy as np #not used yet but probably should be for multi-user graphs

from datetime import datetime

matplotlib.use("TkAgg") #this fixes rendering in PyCharm

def build_user_scores(user, board, sort_type = None):
    p = "D:/Programming/Cyberscore/Discord bot/leaderboards/archive/" + board + "/"
    timestamps = []
    scores = []
    for filename in os.listdir(p):
        #todo - this isn't working?
        if not validate_board_sort(board, filename, sort_type):
            continue

        with open(p + filename, "r+") as f:
            data = cmfn.load_leaderboard(f)
            # todo - restructure load_leaderboard output so this doesn't have to iterate over everything
            # ideally we have some kind of indexing by position
            score = 0
            for username in data:
                if username.lower() != user.lower():
                    continue

                user_entry = data[username]
                score = user_entry['score']

            #todo - replace this with less gross direct conversion
            dt = datetime.strptime(cmfn.convert_timestamp_to_excel(filename), "%Y-%m-%d %H:%M:%S")

            timestamps.append(dt)
            scores.append(score)
    return {'x_values': timestamps, 'y_values': scores}

def build_lead_differences(board, sort_type = "plat"):
    #for graphs, we want every series to be in its own array, as well as the matching array of points on the x-axis
    data = generate_lead_progression(board, sort_type)
    x_values = []
    y_values = []
    for item in data:
        #convert datetime string to a datetime object
        x_datetime = datetime.strptime(item['dt'], "%Y-%m-%d %H:%M:%S")
        x_values.append(x_datetime)
        y_values.append(item['diff'])

    return {'x_values': x_values, 'y_values': y_values}

def generate_lead_diff_graph(board, sort_type = None):
    #takes in some parameters for what board/sort to render a graph for
    #then creates the graph and saves it to /graphs/
    #returning the filename (*without* "/graphs/") of the saved file
    sb_names = cmfn.get_scoreboard_names(board, sort_type)
    graph_data = build_lead_differences(sb_names['file_name'], sb_names['sort_type'])

    fig, ax = plt.subplots()
    ax.plot(graph_data['x_values'], graph_data['y_values'])

    #format axes
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.gcf().autofmt_xdate() #rotates date labels diagonally
    ax.set_ylim(bottom=0)

    #titles and labels
    graph_title = "Lead progression — " + sb_names['display_name']
    if sort_type:
        graph_title += " ("+sb_names['sort_type'].title()+")"
        #we want just e.g., "Gold" instead of "Gold Medals for the header
        #since the "Medals" part of it is fairly obvious from "Medal Table"
        #the award_name ("Gold Medals") is displayed in y-axis label
    ax.set_title(graph_title)
    ax.set_xlabel("Date")
    ax.set_ylabel(sb_names['award_name'])

    #save to image and get the filename we saved it to
    graph_name = save_graph_to_image(board, sb_names['sort_type'])
    return graph_name

def generate_user_graph(user, board, sort_type = None):
    sb_names = cmfn.get_scoreboard_names(board, sort_type)
    graph_data = build_user_scores(user, sb_names['file_name'], sb_names['sort_type'])

    fig, ax = plt.subplots()
    ax.plot(graph_data['x_values'], graph_data['y_values'])

    #format axes
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.gcf().autofmt_xdate() #rotates date labels diagonally
    ax.set_ylim(bottom=0)

    #titles and labels
    graph_title = user + " — " + sb_names['display_name']
    if sort_type:
        graph_title += " ("+sb_names['sort_type']+")"
    ax.set_title(graph_title)
    ax.set_xlabel("Date")
    ax.set_ylabel(sb_names['award_name'])
    #force y-axis to start at 0

    #save to image and get the filename we saved it to
    graph_name = save_graph_to_image(board, sb_names['sort_type'])
    return graph_name

def save_graph_to_image(board, sort_type):
    #generate filename
    curr_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    graph_name = board #this is an ephemereal file so no need to use user-friendly names
    if sort_type:
        graph_name += "_"+sort_type
    graph_name += "_"+curr_time + ".png"
    #save image, bbox_inches=tight removes whitespace on outer edges
    plt.savefig('graphs/'+graph_name, bbox_inches="tight")

    return graph_name