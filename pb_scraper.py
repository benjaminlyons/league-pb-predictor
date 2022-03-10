import bs4
import urllib.request

def parse_table_headers(row):
    headers = []

    for th in row.find_all('th'):
        headers.append(th.get_text())

    return headers

def parse_table_data(row):
    row_data = []

    for index, td in enumerate(row.find_all('td')):
        # if it is the first index, then it requires special parsing
        # to get the data we want
        if index == 0:
            row_data.append(td.find('a').get('title').strip())
            continue
        
        row_data.append(td.get_text().strip().replace(", ", ":"))
    
    return row_data


def scrape_event_pb(event):
    url = f'https://lol.fandom.com/wiki/Special:RunQuery/PickBanHistory?PBH%5Bpage%5D={event}&PBH%5Btextonly%5D=Yes&pfRunQueryFormName=PickBanHistory'

    source = urllib.request.urlopen(url)
    soup = bs4.BeautifulSoup(source, 'lxml')

    pb_table = soup.find(id='pbh-table')

    table_data = []
    for index, row in enumerate(pb_table.find_all("tr")):
        # skip first row of table
        if index == 0:
            continue

        # second row contains headers
        if index == 1:
            headers = parse_table_headers(row)
            continue

        # otherwise 
        table_data.append(parse_table_data(row))

    return headers, table_data

def main():
    with open('events.txt', 'r') as f:
        events = [ line.strip() for line in f.readlines() ]

    with open('pb_table.csv', 'w') as f:
        for index, event in enumerate(events):
            print(f"Downloading {event}...", end='')
            headers, data = scrape_event_pb(event)

            if index == 0:
                f.write(','.join(headers) + '\n')

            for row in data:
                f.write(','.join(row) + '\n')

            print("Done!")


if __name__ == "__main__":
    main()
