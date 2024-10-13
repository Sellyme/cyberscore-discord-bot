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
            diff = data[1]['score'] - data[2]['score']
            dt = cmfn.convert_timestamp_to_excel(filename)

            # below line won't work on boards with custom sort params
            leads.append({"dt": dt, "diff": diff})
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
    if board == "medals" or board == "trophy":
        if sort == "plat":
            if filename.count("_") > 1:
                # if there's a suffix indicating board size_type, it's not plat
                return False
        else:
            if sort not in filename:
                # and if we've set a different sort, discard any not containing that
                return False
    return True