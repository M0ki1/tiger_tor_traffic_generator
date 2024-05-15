alexa_file_name = 'alexa_top_50_2022.txt'
tranco_file_name = 'tranco_top_websites.csv'

alexa_file = open(alexa_file_name, 'r')
tranco_file = open(tranco_file_name, 'r')

alexa_contents = alexa_file.readlines()
tranco_contents = tranco_file.readlines()

OVERLAP = 250

alexa_websites = []
tranco_websites = []

for website in alexa_contents:
    alexa_websites.append(website)

for i, line in enumerate(tranco_contents):
    if i >= OVERLAP:
        break
    tranco_websites.append(line.split(',')[-1])

print(tranco_websites)

count_common_websites = 0
for site in alexa_websites:
    if site in tranco_websites:
        count_common_websites += 1


print("count_common_websites", count_common_websites)