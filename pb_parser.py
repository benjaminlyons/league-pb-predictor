import pandas as pd

def analyze_pb_row(row, champion_stats):
    ban_headers = ["BB1", "RB1", "BB2", "RB2", "BB3", "RB3", "RB4", "BB4", "RB5", "BB5"]
    pick_headers = ["BP1", "RP1-2", "BP2-3", "RP3", "RP4", "BP4-5", "RP5"]

    blue_wins = True if row['Winner'] == 1 else False

    for ban in ban_headers:
        champ = row[ban]

        if not champ in champion_stats:
            champion_stats[champ] = {"bans": 0, "picks": 0, "wins": 0, "games": 0}
        
        champion_stats[champ]["bans"] += 1

    for pick in pick_headers:
        # determine if the team that  made this pick won the game
        blue_pick = True if "B" in pick else False
        winning_pick = (blue_pick and blue_wins) or (not blue_pick and not blue_wins)

        champ1 = row[pick]

        # if their are two picks at once bc of snake draft
        if "-" in pick: 
            champ1 = row[pick].split(':')[0]
            champ2 = row[pick].split(':')[1]

            if not champ2 in champion_stats:
                champion_stats[champ2] = {"bans": 0, "picks": 0, "wins": 0, "games": 0}

            champion_stats[champ2]["picks"] += 1
            champion_stats[champ2]["games"] += 1
            champion_stats[champ2]['wins'] += int(winning_pick)


        if not champ1 in champion_stats:
            champion_stats[champ1] = {"bans": 0, "picks": 0, "wins": 0, "games": 0}

        champion_stats[champ1]["picks"] += 1
        champion_stats[champ1]["games"] += 1
        champion_stats[champ1]["wins"] += int(winning_pick)

def generate_champion_stats(df):
    champion_stats = {}
    total_games = len(df)

    for index, row in df.iterrows():
        analyze_pb_row(row, champion_stats)

    # compute the rate stats
    for champ in champion_stats:
        champion_stats[champ]["pick_rate"] = champion_stats[champ]["picks"] / total_games
        champion_stats[champ]["ban_rate"] = champion_stats[champ]["bans"] / total_games

        if champion_stats[champ]["games"]:
            champion_stats[champ]["win_rate"] = champion_stats[champ]["wins"] / champion_stats[champ]["games"]

    print(champion_stats["Rakan"])

    return champion_stats


def main():
    df = pd.read_csv("pb_table.csv")

    generate_champion_stats(df)

if __name__ == "__main__":
    main()
