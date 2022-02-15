import pandas as pd
import matplotlib.pyplot as plt

# find all pairs of unique champions between these two sequences
# each pair is in alphabetical order
def generate_pairs(sequence1, sequence2):
    pairs = []
    for champ1 in sequence1:
        for champ2 in sequence2:
            if champ1 < champ2:
                pairs.append((champ1, champ2))
            elif champ2 < champ1:
                pairs.append((champ2, champ1))
    return pairs

def find_common_pairs(drafts):
    def compute_freqs(pairs, freqs):
        for pair in pairs:
            if not pair in freqs:
                freqs[pair] = 0
            freqs[pair] += 1

    synergies = {}
    counters = {}
    for draft in drafts:
        blue_picks = draft["blue_pick_sequence"]
        red_picks = draft["red_pick_sequence"]

        blue_pairs = generate_pairs(blue_picks, blue_picks)
        red_pairs = generate_pairs(red_picks, red_picks)

        counter_pairs = generate_pairs(blue_picks, red_picks)

        compute_freqs(blue_pairs, synergies)
        compute_freqs(red_pairs, synergies)
        compute_freqs(counter_pairs, counters)

    return synergies, counters

def update_bans(champ, champion_stats, team_stats, team):
    if not champ in champion_stats:
        champion_stats[champ] = {"bans": 0, "picks": 0, "wins": 0}

    champion_stats[champ]["bans"] += 1

    if not champ in team_stats[team]:
        team_stats[team][champ] = {"bans": 0, "picks": 0, "wins": 0}

    team_stats[team][champ]["bans"] += 1

def update_picks(champ, champion_stats, team_stats, team, winning_pick):
    if not champ in champion_stats:
        champion_stats[champ] = {"bans": 0, "picks": 0, "wins": 0}

    champion_stats[champ]["picks"] += 1
    champion_stats[champ]["wins"] += int(winning_pick)

    if not champ in team_stats[team]:
        team_stats[team][champ] = {"bans": 0, "picks": 0, "wins": 0}

    team_stats[team][champ]["picks"] += 1
    team_stats[team][champ]["wins"] += int(winning_pick)

# parses the row and puts the relevant data into champion_stats and drafts
def analyze_pb_row(row, champion_stats, drafts, team_stats):
    ban_headers = ["BB1", "RB1", "BB2", "RB2", "BB3", "RB3", "RB4", "BB4", "RB5", "BB5"]
    pick_headers = ["BP1", "RP1-2", "BP2-3", "RP3", "RP4", "BP4-5", "RP5"]

    red_ban_sequence = []
    blue_ban_sequence  = []
    red_pick_sequence = []
    blue_pick_sequence = []

    blue_wins = True if row['Winner'] == 1 else False
    
    blue_team = row["Blue"]
    red_team = row["Red"]

    if not blue_team in team_stats:
        team_stats[blue_team] = {"games": 0, "wins": 0}

    if not red_team in team_stats:
        team_stats[red_team] = {"games": 0, "wins": 0}

    team_stats[blue_team]["games"] += 1
    team_stats[red_team]["games"] += 1

    if blue_wins:
        team_stats[blue_team]["wins"] += 1
    else:
        team_stats[red_team]["wins"] += 1

    for ban in ban_headers:
        blue_ban = False if "R" in ban else True
        champ = row[ban]

        if champ == "MISSING DATA" or champ == "None":
            continue

        if blue_ban:
            update_bans(champ, champion_stats, team_stats, blue_team)
            blue_ban_sequence.append(champ)
        else:
            update_bans(champ, champion_stats, team_stats, red_team)
            red_ban_sequence.append(champ)

    for pick in pick_headers:

        # determine if the team that  made this pick won the game
        blue_pick = True if "B" in pick else False
        winning_pick = (blue_pick and blue_wins) or (not blue_pick and not blue_wins)

        champ1 = row[pick]

        if champ1 == "MISSING DATA" or champ1 == "None":
            continue

        # if their are two picks at once bc of snake draft
        if "-" in pick: 
            champ1 = row[pick].split(':')[0]
            champ2 = row[pick].split(':')[1]

            if blue_pick:
                update_picks(champ2, champion_stats, team_stats, blue_team, winning_pick)
                blue_pick_sequence.append(champ2)
            else:
                update_picks(champ2, champion_stats, team_stats, red_team, winning_pick)
                red_pick_sequence.append(champ2)

        if blue_pick:
            update_picks(champ1, champion_stats, team_stats, blue_team, winning_pick)
            blue_pick_sequence.append(champ1)
        else:
            update_picks(champ1, champion_stats, team_stats, red_team, winning_pick)
            red_pick_sequence.append(champ1)

    drafts.append({"blue_pick_sequence": blue_pick_sequence, "red_pick_sequence": red_pick_sequence, "blue_ban_sequence": blue_ban_sequence, "red_ban_sequence": red_ban_sequence})

def generate_pb_stats(df):
    champion_stats = {}
    team_stats = {}
    drafts = []
    total_games = len(df)

    for index, row in df.iterrows():
        analyze_pb_row(row, champion_stats, drafts, team_stats)

    # compute the rate stats
    for champ in champion_stats:
        champion_stats[champ]["pick_rate"] = champion_stats[champ]["picks"] / total_games
        champion_stats[champ]["ban_rate"] = champion_stats[champ]["bans"] / total_games

        if champion_stats[champ]["picks"]:
            champion_stats[champ]["win_rate"] = champion_stats[champ]["wins"] / champion_stats[champ]["picks"]

        for team in team_stats:
            if not champ in team_stats[team]:
                continue

            team_stats[team][champ]["pick_rate"] = team_stats[team][champ]["picks"] / team_stats[team]["games"]
            team_stats[team][champ]["ban_rate"] = team_stats[team][champ]["bans"] / team_stats[team]["games"]

            if team_stats[team][champ]["picks"]:
                team_stats[team][champ]["win_rate"] = team_stats[team][champ]["wins"] / team_stats[team][champ]["picks"]

    return champion_stats, drafts, team_stats

def summarize_pb_stats(champion_stats, drafts):
    print("------ Pick/Ban Stats ------")
    print("Top 3 most picked:")
    for index, champ in enumerate(sorted(champion_stats.items(), key = lambda champ: champ[1]["pick_rate"], reverse=True)):
        if index >= 3:
            break
        print(f"\t{index}. {champ[0]}: {champ[1]}")

    print()
    print("Top 3 most banned:")
    for index, champ in enumerate(sorted(champion_stats.items(), key = lambda champ: champ[1]["ban_rate"], reverse=True)):
        if index >= 3:
            break
        print(f"\t{index}. {champ[0]}: {champ[1]}")

    print()
    print("Top 3 highest presence:")
    for index, champ in enumerate(sorted(champion_stats.items(), key = lambda champ: champ[1]["ban_rate"] + champ[1]["pick_rate"], reverse=True)):
        if index >= 3:
            break
        print(f"\t{index}. {champ[0]}: {champ[1]}")
    print()
    print(f"Total champions picked: {len(champion_stats.keys())}")
    print()
    print("Top 5 most common synergies:")
    synergies, counters = find_common_pairs(drafts)
    for index, pair in enumerate(sorted(synergies.items(), key=lambda p: p[1], reverse=True)):
        if index >= 5:
            break
        print(f"\t{index}. {pair[0][0]} + {pair[0][1]}: {pair[1]}")
    print()
    print("Top 5 most common counters:")
    for index, pair in enumerate(sorted(counters.items(), key=lambda p: p[1], reverse=True)):
        if index >= 5:
            break
        print(f"\t{index}. {pair[0][0]} + {pair[0][1]}: {pair[1]}")
    

def generate_pb_histograms(champion_stats, drafts):
    total_games = len(drafts)
    pick_rates = [ champion_stats[champ]["pick_rate"] for champ in champion_stats ]
    ban_rates = [ champion_stats[champ]["ban_rate"] for champ in champion_stats ]
    win_rates = [ champion_stats[champ]["win_rate"] for champ in champion_stats if "win_rate" in champion_stats[champ] ]
    presence_rates  = [ champion_stats[champ]["pick_rate"] + champion_stats[champ]["ban_rate"] for champ in champion_stats ]

    n_bins = 20
    fig, axs = plt.subplots(2, 2, tight_layout=True, figsize=(10,10))
    axs[0][0].set_title("Pick Rate Distribution")
    axs[0][1].set_title("Ban Rate Distribution")
    axs[1][0].set_title("Win Rate Distribution")
    axs[1][1].set_title("Presence Rate Distribution")
    axs[0][0].hist(pick_rates, bins=n_bins)
    axs[0][1].hist(ban_rates, bins=n_bins)
    axs[1][0].hist(win_rates, bins=n_bins)
    axs[1][1].hist(presence_rates, bins=n_bins)

    plt.savefig("pb_histograms.jpg")

    synergies, counters = find_common_pairs(drafts)
    synergy_freqs = [ freq  for pair, freq in synergies.items()  if freq > 50] 
    counter_freqs = [ freq for pair, freq in counters.items() if freq > 50]
    fig, axs = plt.subplots(1,2, tight_layout=True, figsize=(10,5))
    axs[0].set_title("Frequency of Synergies")
    axs[0].hist(synergy_freqs, bins=n_bins, density=True)
    axs[1].set_title("Frequency of Counters")
    axs[1].hist(counter_freqs, bins=n_bins, density=True)

    plt.savefig("pairings_histograms.jpg")

def main():
    df = pd.read_csv("pb_table.csv")

    champion_stats, drafts, team_stats = generate_pb_stats(df)
    summarize_pb_stats(champion_stats, drafts)
    generate_pb_histograms(champion_stats, drafts)
    
    print(team_stats["Fnatic"]["Twisted Fate"])

if __name__ == "__main__":
    main()
