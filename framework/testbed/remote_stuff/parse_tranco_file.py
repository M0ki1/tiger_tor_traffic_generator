def parse_tranco_pages():
    tranco_pages = []
    tranco_pages_file_name = 'tranco_top_websites.csv'
    with open(tranco_pages_file_name, 'r') as f:
        for line in f:
            tranco_pages.append(line.split(',')[1][:-1]) # [-1] removes the /n at the end
    return tranco_pages

tranco_pages = parse_tranco_pages()
print(tranco_pages)