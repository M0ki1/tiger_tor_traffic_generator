import os
from bs4 import BeautifulSoup
import ssdeep
import shutil



def get_only_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    return [tag.name for tag in soup.find_all()]


def search_files(base_dir):
    """Recursively search for files with a given file extension in a root directory"""
    file_list = []
    for dirpath, dirnames, filenames in os.walk(base_dir):
        for filename in filenames:
            #if filename.endswith(file_ext):
            file_list.append(os.path.join(dirpath, filename))
    return file_list


# First, it gathers the combination of all the simple files in the main website's directory
# Then, it computes the fuzzy hash of all the files combined
# Then, it compares the fuzzy hash of all the onion sites with each other, and the ones with similarity higher than 90 are considered mirrors
def deduplicate_pages(base_dir, results_dir):
    known_htmls = {}

    for onion_dir in os.listdir(base_dir):
        #print("= onion_dir: {}".format(onion_dir))
        if '.DS_Store' in onion_dir:
            continue


        files = search_files(base_dir+onion_dir)
        files_combined_str = ''
        for file in files:
            with open(file, 'r', encoding = "ISO-8859-1") as f:
                files_combined_str += f.read()
        known_htmls[onion_dir] = ssdeep.hash(files_combined_str)

    #print("known_htmls: {}".format(known_htmls))
    unique_htmls = known_htmls.copy()
    
    for onion_dir1, hash1 in known_htmls.items():
        for onion_dir2, hash2 in known_htmls.items():
            #if (onion_dir1 == 'royalthrgnah65g556h7nmmawqyu5ulrtju7i7pskma35lj2ky6w2iyd.onion' and onion_dir2 == 'royalfoupfrbh3npfuqsbm6ienpdwd2j6dfqijrnkeqzdnby52bldgqd.onion') or (onion_dir1 == 'royalfoupfrbh3npfuqsbm6ienpdwd2j6dfqijrnkeqzdnby52bldgqd.onion' and onion_dir2 == 'royalthrgnah65g556h7nmmawqyu5ulrtju7i7pskma35lj2ky6w2iyd.onion'):
            #    print("******** DIRS REPEATED!")
            #else:
            #    continue
            if onion_dir1 == onion_dir2:
                continue
            try:
                similarity_score = ssdeep.compare(hash1, hash2)
                print("similarity_score: {}".format(similarity_score))
            except Exception as e:
                print("Error in {} and {}".format(onion_dir1, onion_dir2))
                continue
            if similarity_score > 10:
                print("Similar files found: {} and {}".format(onion_dir1, onion_dir2))
                if onion_dir2 in unique_htmls:
                    unique_htmls.pop(onion_dir2)
            else:
                print("Pages are not duplicates: {} and {}".format(onion_dir1, onion_dir2))
                #os.system()

    for onion_dir in unique_htmls.keys():
        shutil.copytree(base_dir+onion_dir, results_dir+onion_dir, dirs_exist_ok=True)
    


# TODO: test with new onion sites crawled
def main():
    base_dir = 'onion_pages_2023/'
    results_dir = 'onion_pages_2023_deduped/'
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)

    deduplicate_pages(base_dir, results_dir)


if __name__ == "__main__":
    main()


