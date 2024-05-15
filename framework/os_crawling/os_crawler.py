# https://deepakbalhara.com/blog/how-to-scrape-dark-web-onion-site-using-python/


# 11 most popular Tor Onion Services: https://www.cyberghostvpn.com/en_US/privacyhub/what-are-onion-sites/
# Hidden Wiki: http://paavlaytlfsqyvkg3yqj7hflfg5jw2jdg2fgkza5ruf6lplwseeqtvyd.onion/
# Torch: http://torchdeedp3i2jigzjdmfpn5ttjhthh5wbmda2rr3jvqjg5p77c54dqd.onion/
# DuckDuckGo: https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/
# The Intercept: https://27m3p2uv7igmj6kvd4ql3cct5h3sdwrsajovkkndeufumzyfhlfev4qd.onion/
# Proton Mail: https://protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion/
# ProPublica: http://p53lf57qovyuvwsc6xnrppyply3vtqm7l6pcobkmyqsiofyeznfu5uqd.onion/
# SecureDrop: http://sdolvtfhatvsysc6l34d65ymdwxcujausv7k5jk4cy5ttzhjoi6fzvyd.onion/
# Webpage Archive: http://archiveiya74codqgiixo33q62qlrqtkgmcitqx5u2oeqnmn5bpcbiyd.onion/
# Dread: http://dreadytofatroptsdj6io7l3xptbet6onoyno2yv7jicoxknyazubrad.onion/
# Hidden Wallet: http://d46a7ehxj6d6f2cf4hi3b424uzywno24c7qtnvdvwsah5qpogewoeqid.onion/
# Deep Web Radio: http://anonyradixhkgh5myfrkarggfnmdzzhhcgoy2v66uf7sml27to5n2tid.onion/
# IncogTube: http://tuberyps2pn6dor6h47brof3w2asmauahhk4ei42krugybzzzo55klad.onion/
# Facebook: https://www.facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion/


from lzma import FORMAT_AUTO
import requests
import random
import subprocess
import sys
import os
import glob
import tqdm
from multiprocessing import Pool
import time


def find_links(content, keyword, onion_urls):
        #takes in content - webpage in string format - then searches it with regex
        import re
        import random #just for generating lists of sites -files easily
        
        regexquery = "\w+\.onion"
        #regexquery is a regex query for finding onion links
        mineddata = re.findall(regexquery, content)
        
        # Remove onion urls already on other files
        mineddata = set(mineddata) - onion_urls

        onion_urls.update(mineddata)
        
        filename = "sites_{}.txt".format(keyword)
        print("Saving to ... ", filename)
        # The dictionary prevents repeated keys on the same file
        mineddata = list(dict.fromkeys(mineddata))
        
        with open(filename,"w+") as _:
            print("")
        for k in mineddata:
            with open(filename,"a") as newfile:
                k  = k + "\n"
                newfile.write(k)
        print("All the files written to a text file : ", filename)


def scrape_ahmia():
    # Use a list of popular onion services and use it as a seed list
    # Use ahmia as a seed list and pass keywords in their search
    # https://ahmia.fi/search/?q=a
    # https://ahmia.fi/search/?q=hello
    # https://ahmia.fi/search/?q=world
    # https://hoxframework.com.hr/?p=473

    keywords = ["credit card", "hacking", "guns", "news", "search", "forum", "wiki", "whistleblower", "mail", "bitcoin", "fraud", "fraud", "market", "drugs", "video"]
    # Avoid repeated onion urls on the multiple files
    onion_urls = set()
    for keyword in keywords:

        if " " in keyword:
            keyword = keyword.replace(" ","+")

        url = "https://ahmia.fi/search/?q={}".format(keyword)
        print("=== URL: {}".format(url))

        #lets set up some fake user agents
        ua_list = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19577"
        ,"Mozilla/5.0 (X11) AppleWebKit/62.41 (KHTML, like Gecko) Edge/17.10859 Safari/452.6", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2656.18 Safari/537.36"
        ,"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36", "Mozilla/5.0 (Linux; U; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13","Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27"
        ,"Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_5_8; zh-cn) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27"]
        ua = random.choice(ua_list)
        headers = {'User-Agent': ua}

        request = requests.get(url, headers=headers) #, verify=False)
        content = request.text

        if request.status_code == 200:
            print("Request went through. Url: {}\n".format(url))
            #print(content)
            find_links(content, keyword, onion_urls)
        else:
            print("Request failed! Url: {}\n".format(url))

    print("Total urls scraped: ", len(onion_urls))


def mirror_os(file):
    log_file = 'mirror_oses_{}.log'.format(os.getpid())
    count_errors = 0
    count_success = 0

    opened_file = open(file, 'r')
    urls = opened_file.readlines()
    existing_urls = set(glob.glob('*.onion'))
    for url in tqdm.tqdm(urls):
        if url in existing_urls:
            count_success += 1
            continue
        print("--- url: ", url)
        try:
            output = subprocess.check_output('torsocks wget -m -k -K -E {}'.format(url), shell=True)
            count_success += 1
        except Exception as err:
            print("Error: ", err)
            count_errors += 1
            continue
        finally:
            with open(log_file, 'w') as f:
                f.write("Success: {}\nError: {}".format(count_success, count_errors))


def mirror_oses():
    # https://pirate.london/how-to-mirror-an-onion-site-for-later-discussion-f0ea102a1dec
    # The switches in question tell wget to mirror, konvert links to local versions, save original non-Konverted files, and adjust Extensions to .html files
    # Could not run this on Mac, only on Linux
    # First run tor process
    # wget -m -k -K -E olivq73nea2cnwdtgrt2urxhw7ub3eigxl2wrca2k3b2davfakai7zqd.onion.to/
    # Method that works: torsocks wget -m -k -K -E olivq73nea2cnwdtgrt2urxhw7ub3eigxl2wrca2k3b2davfakai7zqd.onion/
    # curl --socks5-hostname localhost:9150 olivq73nea2cnwdtgrt2urxhw7ub3eigxl2wrca2k3b2davfakai7zqd.onion
    # curl --socks5-hostname localhost:9151 olivq73nea2cnwdtgrt2urxhw7ub3eigxl2wrca2k3b2davfakai7zqd.onion

    # Iterate through all scrapped links
    files = glob.glob('sites_*.txt')
    p = Pool(10)
    p.map(mirror_os, files)
    p.terminate()
    p.join()
    #for file in tqdm.tqdm(files):


def main():
    scrape_ahmia() # gets the url of multiple onion services
    start = time.time()
    mirror_oses()
    end = time.time()
    print("end - start", end - start)
    # hmuidcgzsjlcsxe6rdluskevjtgynhupixpb7g5czmjpuftlhrl42bid.onion


if __name__ == "__main__":
    main()


# Marketplaces
# DDoS mechanisms
# http://alphabay522szl32u4ci5e3iokdsyth56ei7rwngr2wm7i5jo54j2eid.onion/
# http://alphabay522szl32u4ci5e3iokdsyth56ei7rwngr2wm7i5jo54j2eid.onion/login

# http://bohemiaobko4cecexkj5xmlaove6yn726dstp5wfw4pojjwp6762paqd.onion/

# BBC
# old: bbcnewsd73hkzno2ini43t4gblxvycyac5aw4gnv7t2rccijh7745uqd.onion
# new: bbcweb3hytmzhn5d532owbu6oqadra5z3ar726vq5kgwwn6aucdccrad.onion

# Check onion services that are up
# https://dark.fail/
# https://darknetlive.com/markets/
# https://darknetlive.com/


# Other crawled websites:
## BBC
### For HTTPS, needs to have --no-check-certificate flag
### torsocks wget -m -k -K -E --no-check-certificate https://www.bbcweb3hytmzhn5d532owbu6oqadra5z3ar726vq5kgwwn6aucdccrad.onion

## ASAP Market with DDoS mechanism:  (I think it uses old version dread)
## https://blog.tinned-software.net/download-a-complete-website-using-wget/
### http://asap4u2ihsunfdsumm66pmado3mt3lemdiu3fbx5b7wj5hb3xpgmwkqd.onion/
#### Access through known cookies pre-obtained in the Tor browser
#### https://unix.stackexchange.com/questions/36531/format-of-cookies-when-using-wget
# Go to the network tab of the developer tools and select the request > copy as curl
#### torsocks curl 'http://asap2u4pvplnkzl7ecle45wajojnftja45wvovl3jrvhangeyq67ziid.onion/' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Connection: keep-alive' -H 'Cookie: dcap=988CA7867664613895FD8450AC968BDB5947CA27908E62F181B0B2472E52BF855A0EAE652EF523EFDCCE88483870A52A141B662C5D47A6E1EA1B39F29EA94551A3E357A5A65792F5695892D4AC66697311F1E9324C496E4A053A7C469E562107185C55AF9F5B89C6F9AA649B5122CBD1B8773BA3F079DB0D703AA94DC2467138' -H 'Upgrade-Insecure-Requests: 1' -H 'Sec-Fetch-Dest: document' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Site: none' -H 'Sec-Fetch-User: ?1'
#### torsocks wget -m -k -K -E --execute="robots = off" --header='User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0' --header='Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' --header='Accept-Language: en-US,en;q=0.5' --header='Connection: keep-alive' --header='Cookie: dcap=988CA7867664613895FD8450AC968BDBAF7218A96C63BAF24F78EADD4B357B20D56EEF416166FEA80D9F6DFC213530B7A644F9B56AE48F1726B7FD5AEFD06CAF5ACCC2DE8DE2626F6B4CCEC3854243BF7474A215E548482039797E1588DF056CF3F60A795388614245429A372008A892' --header='Upgrade-Insecure-Requests: 1' --header='Sec-Fetch-Dest: document' --header='Sec-Fetch-Mode: navigate' --header='Sec-Fetch-Site: none' --header='Sec-Fetch-User: ?1' http://asap2u4pvplnkzl7ecle45wajojnftja45wvovl3jrvhangeyq67ziid.onion/

