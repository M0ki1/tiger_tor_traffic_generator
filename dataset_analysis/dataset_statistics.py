import matplotlib.pyplot as plt
import glob
import pickle
import numpy as np
import os
import joblib
from joblib import Parallel, delayed
import datetime

import process_pcaps
import query_sumo_dataset
import statistics_utils


def create_reverse_mapping(dictionary):
    return {value.split("/")[-2]: key for key, value in dictionary.items()}


onion_pages = {
    'o1': 'http://localhost/onionRealPages2022/b4bbcjkuimxggedoqahicvimcw7xutwmp4omh2lz7cskuaaxoxog6cad/',
    'o32': 'http://localhost/onionRealPages2022/hackerr6x5joaf2quyop3g3q3jyuqbpkoydtta5a53lhx25k43e6uiad/',
    'o31': 'http://localhost/onionRealPages2022/fxrx6qvrri4ldt7dhytdvkuakai75bpdlxlmner6zrlkq34rpcqpyqyd/',
   'o30': 'http://localhost/onionRealPages2022/liibeu7vlwaumwrstixzcpkqucdfln5m4sn5buciwkgbn6aet2xokzyd/',
    'o2': 'http://localhost/onionRealPages2022/biden6qccqo5iqzvnjgpivp3owp2v5xodgwenqdh5wsq7zzfhnvodjqd/',
    'o29': 'http://localhost/onionRealPages2022/f5a4wxs3e3hsuajufy4sa52jj2vb3khctzrwaka5tanew4uvh3lsrhid/',
    'o28': 'http://localhost/onionRealPages2022/epxfqkb7kyuenlbsitgaj5zht4y33uqj4ftswmhrdwx3b252xj3ajpad/',
    'o27': 'http://localhost/onionRealPages2022/duvlyvpbhwl37a2hisxrr4o2sceq2uygfmhpz3wcidf5xz5yjvxvgjid/',
   'o3': 'http://localhost/onionRealPages2022/bizz4kwy566gxae32fkjybarded4caeqatyj4jvoxpkrx3wrzrq77yad/',
   'o26': 'http://localhost/onionRealPages2022/dse6rlfwpgdohd33ulg623rpzy3zv5y5whfw23jznd3xu4o47vy6xmqd/',
    'o25': 'http://localhost/onionRealPages2022/l5jcgrava4h2joxfcnyas7qvkqjdzeywnsqntrmwqpfq7u4rz2iwjzyd/',
    'o24': 'http://localhost/onionRealPages2022/dbayuapytcowfz2nnfik3jayno4njibl45t77r3eartihtq6igtaqtqd/',
    'o4': 'http://localhost/onionRealPages2022/calcu2cjww3qkdlzllf35qsbstk4umxxi76lnttc3o63bd2gbcidqyqd/',
    'o23': 'http://localhost/onionRealPages2022/coinpigv67cccbkeoddtthduoy65uwtc7rs3pvwtln2xefcrnkhf3sad/',
    'o22': 'http://localhost/onionRealPages2022/dcrdata5oppwcotlxkrlsp6afncnxvw54sw6jqftc4bjytm4rn27j3ad/',
    'o21': 'http://localhost/onionRealPages2022/darkfox7kukhe3b2ufsvuknskyhzdjc7a724mh4zrkipeg7pkaikm6yd/',
    'o5': 'http://localhost/onionRealPages2022/mixtumjzn2tsiusfkdhutntamspsg43kgt764qbdaxjebce4h6fcfiad/',
    'o20': 'http://localhost/onionRealPages2022/mp3fpv6xbrwka4skqliiifoizghfbjy5uyu77wwnfruwub5s4hly2oid/',
    'o19': 'http://localhost/onionRealPages2022/mvj5hwvun4dalhggvh6p5gnclggywrxeflrfaxcpzxo7efseikjj6wid/',
    'o18': 'http://localhost/onionRealPages2022/naturelwg7o3bhnhwcmn6svzoekxkl3pv365krgmdpckonf5xvarlkid/',
    'o6': 'http://localhost/onionRealPages2022/nq4zyac4ukl4tykmidbzgdlvaboqeqsemkp4t35bzvjeve6zm2lqcjid/',
    'o17': 'http://localhost/onionRealPages2022/ofrx66cgm4vzzl4y6brb26anu7uaf5ul4coudu65mpnu44rmfae3fgyd/',
    'o16': 'http://localhost/onionRealPages2022/ojqllc2vr6nttoddzx3yf34qonoqs5qks6jewnfuv256jzfkj724isqd/',
    'o15': 'http://localhost/onionRealPages2022/okj2scf6yptajq2slvahni4u5jrattnr4u4mukokl3d7wq7erygn6bad/',
    'o7': 'http://localhost/onionRealPages2022/orc52yt3qnatcmwwbiht4n6qvbxdeapzzvp6xaiwnuta2c2lqn4afdad/',
    'o14': 'http://localhost/onionRealPages2022/p3s3h32smv45dsvgl63tmsyhl2etq6yuemsmwsjn6z4wjrsltfapihid/',
    'o13': 'http://localhost/onionRealPages2022/p7gettng6fudmj4gowkl6pnsvbqw3mo44pzwjyxaqo5hjpnonf457qad/',
    'o12': 'http://localhost/onionRealPages2022/pharmacy42hblqssvwizqvrwmy7oec5sfgjtr7hy6dup3t2lf2xzitqd/',
    'o8': 'http://localhost/onionRealPages2022/piratec4cdgbjqzny6sykeqeylarm67teyhroxez3y5fmszrr5lmbgad/',
    'o11': 'http://localhost/onionRealPages2022/psyshopshweetovp4em654waimmcjsf7eqifwe2d4qhnluk2b24r6dqd/',
    'o10': 'http://localhost/onionRealPages2022/pvhwsb7a3d2oq73xtr3pzvmrruvswyqgkyahcb7dmbbfftr4qtsmvjid/',
    'o9': 'http://localhost/onionRealPages2022/r7lscyg5lncab4gm77ldshetqoutj3btq53aw44ixnz3iinc3oaz7qqd/' 
}

reverse_onions = create_reverse_mapping(onion_pages)

machine_ips = {
    'o1': '172.120.',
    'o32': '172.120.',
    'o31': '172.120.',
   'o30': '172.120.',
    'o2': '172.121.',
    'o29': '172.121.',
    'o28': '172.121.',
    'o27': '172.121.',
   'o3': '172.122.',
   'o26': '172.122.',
    'o25': '172.122.',
    'o24': '172.122.',
    'o4': '172.123.',
    'o23': '172.123.',
    'o22': '172.123.',
    'o21': '172.123.',
    'o5': '172.124.',
    'o20': '172.124.',
    'o19': '172.124.',
    'o18': '172.124.',
    'o6': '172.125.',
    'o17': '172.125.',
    'o16': '172.125.',
    'o15': '172.125.',
    'o7': '172.126.',
    'o14': '172.126.',
    'o13': '172.126.',
    'o12': '172.126.',
    'o8': '172.127.',
    'o11': '172.127.',
    'o10': '172.127.',
    'o9': '172.127.',
    'client-train-1-client1': '172.120.',
    'client-train-1-client2': '172.120.',
    'client-train-1-client3': '172.120.',
    'client-train-1-client4': '172.120.',
    'client-train-2-client1': '172.121.',
    'client-train-2-client2': '172.121.',
    'client-train-2-client3': '172.121.',
    'client-train-2-client4': '172.121.',
    'client-train-3-client1': '172.122.',
    'client-train-3-client2': '172.122.',
    'client-train-3-client3': '172.122.',
    'client-train-3-client4': '172.122.',
    'client-train-4-client1': '172.123.',
    'client-train-4-client2': '172.123.',
    'client-train-4-client3': '172.123.',
    'client-train-4-client4': '172.123.',
    'client-train-5-client1': '172.124.',
    'client-train-5-client2': '172.124.',
    'client-train-5-client3': '172.124.',
    'client-train-5-client4': '172.124.',
    'client-train-6-client1': '172.125.',
    'client-train-6-client2': '172.125.',
    'client-train-6-client3': '172.125.',
    'client-train-6-client4': '172.125.',
    'client-train-7-client1': '172.126.',
    'client-train-7-client2': '172.126.',
    'client-train-7-client3': '172.126.',
    'client-train-7-client4': '172.126.',
    'client-train-8-client1': '172.127.',
    'client-train-8-client2': '172.127.',
    'client-train-8-client3': '172.127.',
    'client-train-8-client4': '172.127.',
    'client-train-9-client1': '172.128.',
    'client-train-9-client2': '172.128.',
    'client-train-9-client3': '172.128.',
    'client-train-9-client4': '172.128.',
    'client-train-10-client1': '172.129.',
    'client-train-10-client2': '172.129.',
    'client-train-10-client3': '172.129.',
    'client-train-10-client4': '172.129.'
    }


onion_path_to_name = {
    'o1': 'os1-os-train-1',
    'o32': 'os2-os-train-1',
    'o31': 'os3-os-train-1',
    'o30': 'os4-os-train-1',
    'o2': 'os1-os-train-2',
    'o29': 'os2-os-train-2',
    'o28': 'os3-os-train-2',
    'o27': 'os4-os-train-2',
    'o3': 'os1-os-train-3',
    'o26': 'os2-os-train-3',
    'o25': 'os3-os-train-3',
    'o24': 'os4-os-train-3',
    'o4': 'os1-os-train-4',
    'o23': 'os2-os-train-4',
    'o22': 'os3-os-train-4',
    'o21': 'os4-os-train-4',
    'o5': 'os1-os-train-5',
    'o20': 'os2-os-train-5',
    'o19': 'os3-os-train-5',
    'o18': 'os4-os-train-5',
    'o6': 'os1-os-train-6',
    'o17': 'os2-os-train-6',
    'o16': 'os3-os-train-6',
    'o15': 'os4-os-train-6',
    'o7': 'os1-os-train-7',
    'o14': 'os2-os-train-7',
    'o13': 'os3-os-train-7',
    'o12': 'os4-os-train-7',
    'o8': 'os1-os-train-8',
    'o11': 'os2-os-train-8',
    'o10': 'os3-os-train-8',
    'o9': 'os4-os-train-8'
}


# Taken from: https://stackoverflow.com/questions/69520456/how-can-i-plot-a-cdf-in-matplotlib-without-binning-my-data
def ecdf4plot(seq, assumeSorted = False):
    """
    In:
    seq - sorted-able object containing values
    assumeSorted - specifies whether seq is sorted or not
    Out:
    0. values of support at both points of jump discontinuities
    1. values of ECDF at both points of jump discontinuities
       ECDF's true value at a jump discontinuity is the higher one    """
    if len(seq) == 0:
        return [], []
    if not assumeSorted:
        seq = sorted(seq)
    prev = seq[0]
    n = len(seq)
    support = [prev]
    ECDF = [0.]
    for i in range(1, n):
        seqi = seq[i]
        if seqi != prev:
            preP = i/n
            support.append(prev)
            ECDF.append(preP)
            support.append(seqi)
            ECDF.append(preP)
            prev = seqi
    support.append(prev)
    ECDF.append(1.)
    return support, ECDF


def get_session_durations(top_path, dataset_name):
    print(f"Getting session durations for {dataset_name} ...")
    results_file = f'session_durations_{dataset_name}.joblib'
    if not os.path.isfile(results_file):
    
        client_file_paths = list(glob.iglob(os.path.join(top_path+'/client', '**/folderDict.pickle'), recursive=True))

        session_durations = []

        for test_idx, client_file_path in enumerate(client_file_paths):
            clientFolderDict = pickle.load(open(client_file_path, 'rb'))
            allAbsTimes = clientFolderDict['clientFlow']['timesOutAbs'] + clientFolderDict['clientFlow']['timesInAbs']
            absoluteInitialTime = min(allAbsTimes)
            maxAbsoluteTime = max(allAbsTimes)
            session_duration = maxAbsoluteTime - absoluteInitialTime
            session_durations.append(session_duration)

        session_durations_minutes = []
        for duration in session_durations:
            session_durations_minutes.append(duration / 60)

        joblib.dump(session_durations_minutes, results_file)

    else:
        session_durations_minutes = joblib.load(results_file)

    return session_durations_minutes


def get_requests_per_session(data_folder, dataset_pcap_name, dataset_name):
    print(f"Getting requests per session for {dataset_pcap_name} ...")
    results_file = f'requests_per_session_{dataset_name}.joblib'
    print("--- results_file", results_file)
    if not os.path.isfile(results_file):
        requests_per_session = []
        dataset = query_sumo_dataset.SumoDataset(data_folder)
        requests_per_session_per_dataset = {}
        topPath = f"/mnt/nas-shared/torpedo/extracted_features_{dataset_name}"
        print("--- topPath", topPath)
        client_file_paths = list(glob.iglob(os.path.join(topPath+'/client', '**/folderDict.pickle'), recursive=True))
        for test_idx, client_file_path in enumerate(client_file_paths):
            clientFolderDict = pickle.load(open(client_file_path, 'rb'))
            session_id = query_sumo_dataset.get_session_id_from_path(clientFolderDict['clientSessionId'])
            client_name = query_sumo_dataset.get_client_name(session_id)
            requests_per_session_per_dataset[session_id] = dataset.get_client_session_nb_requests(client_name, session_id)
        requests_per_session += list(requests_per_session_per_dataset.values())
    
        joblib.dump(requests_per_session, results_file)

    else:
        requests_per_session = joblib.load(results_file)

    return requests_per_session


def get_running_average(start_time, times, bytes):
    times_in_minutes = (np.array(times) - start_time) / 60.0
    bytes_per_minute = np.diff([0] + bytes)  # Calculate the bytes transmitted per minute
    average_bytes_per_minute = bytes_per_minute / np.diff([0] + times) * 60.0
    
    return times_in_minutes, average_bytes_per_minute


def process_full_pcaps(onion_pcap_path):
    onion_url = onion_pcap_path.split("/")[-1].split("_session")[0].split('_')[-1]
    onion = reverse_onions[onion_url]

    capture = process_pcaps.process_packets(onion_pcap_path, machine_ips[onion])
    
    return onion, capture['first_ts'], capture['last_ts'], capture['packetTimesInAbs'], capture['packetTimesOutAbs'], capture['packetSizesIn'], capture['packetSizesOut']


def process_pcap_features_running_average(onion_pcap_path):
    onion, start_time, end_time, packetTimesInAbs, packetTimesOutAbs, packetSizesIn, packetSizesOut = process_full_pcaps(onion_pcap_path)

    time_in_minutes_in, average_bytes_per_minute_in = get_running_average(start_time, packetTimesInAbs, packetSizesIn)
    time_in_minutes_out, average_bytes_per_minute_out = get_running_average(start_time, packetTimesOutAbs, packetSizesOut)

    return onion, time_in_minutes_in, time_in_minutes_out, average_bytes_per_minute_in, average_bytes_per_minute_out


def process_pcap_features_onion(onion_pcap_path):
    onion, start_time, end_time, packetTimesInAbs, packetTimesOutAbs, packetSizesIn, packetSizesOut = process_full_pcaps(onion_pcap_path)

    return onion, packetSizesIn, packetSizesOut


def process_pcap_features_client(client_pcap_path):
    client = client_pcap_path.split('/')[-1].split('_')[0]
    capture = process_pcaps.process_packets(client_pcap_path, machine_ips[client])

    return client_pcap_path, capture['packetSizesIn'], capture['packetSizesOut']


def get_average_bytes_transmitted_per_os(top_path):
    print("Getting average bytes transmitted per os ...")
    results_file = 'avg_bytes_transmitted_per_os.joblib'
    if not os.path.isfile(results_file):
        # This needs to gather the features straight from the full-onion pcaps
        onion_pcap_paths = list(glob.iglob(os.path.join(top_path+'/TrafficCapturesOnion', '**/full-onion/*_hs.pcap'), recursive=True))

        onion_labels = []
        times_in = []
        times_out = []
        running_avg_in = []
        running_avg_out = []

        """
        for test_idx, onion_pcap_path in enumerate(onion_pcap_paths):
            onion, start_time, end_time, packetTimesInAbs, packetTimesOutAbs, packetSizesIn, packetSizesOut = process_full_pcaps(onion_pcap_path)

            onion_labels.append(onion)

            time_in_minutes_in, average_bytes_per_minute_in = get_running_average(start_time, packetTimesInAbs, packetSizesIn)
            time_in_minutes_out, average_bytes_per_minute_out = get_running_average(start_time, packetTimesOutAbs, packetSizesOut)

            times_in.append(time_in_minutes_in)
            times_out.append(time_in_minutes_out)

            running_avg_in.append(average_bytes_per_minute_in)
            running_avg_out.append(average_bytes_per_minute_out)

        results = {'onion_labels': onion_labels, 'times_in': times_in, 'times_out': times_out, 'running_avg_in': running_avg_in, 'running_avg_out': running_avg_out}
        
        """

        parallel_results = Parallel(n_jobs=-1)(delayed(process_pcap_features_running_average)(path) for path in onion_pcap_paths)

        # Unpack the results
        onion_labels, times_in, times_out, running_avg_in, running_avg_out = zip(*parallel_results)
        results = {
            'onion_labels': onion_labels,
            'times_in': times_in,
            'times_out': times_out,
            'running_avg_in': running_avg_in,
            'running_avg_out': running_avg_out
        }

        joblib.dump(results, results_file)

    else:
        results = joblib.load(results_file)

        
    return results['onion_labels'], results['times_in'], results['times_out'], results['running_avg_in'], results['running_avg_out']


def get_bytes_transmitted_per_os(top_path):
    print("Getting bytes transmitted per os ...")
    results_file = 'bytes_transmitted_per_os.joblib'
    if not os.path.isfile(results_file):
        onion_pcap_paths = list(glob.iglob(os.path.join(top_path+'/TrafficCapturesOnion', '**/*request_*_hs.pcap'), recursive=True))
        parallel_results = Parallel(n_jobs=-1)(delayed(process_pcap_features_onion)(path) for path in onion_pcap_paths)
        # Unpack the results
        onion_labels, sizes_in, sizes_out = zip(*parallel_results)
        results = {}
        for onion_label, s_in, s_out in zip(onion_labels, sizes_in, sizes_out):
            if onion_label not in results:
                results[onion_label] = {'in': [], 'out': []}
            results[onion_label]['in'].append(sum(s_in))
            results[onion_label]['out'].append(sum(s_out))

        joblib.dump(results, results_file)

    else:
        results = joblib.load(results_file)

    times_in_to_plot = []
    times_out_to_plot = []
    for tses in results.values():
        times_in_to_plot.append(tses['in'])
        times_out_to_plot.append(tses['out'])

    return results.keys(), times_in_to_plot, times_out_to_plot


def get_bytes_transmitted_per_client(top_path):
    print("Getting bytes transmitted per client ...")
    results_file = 'bytes_transmitted_per_client.joblib'
    if not os.path.isfile(results_file):
        client_pcap_paths = list(glob.iglob(os.path.join(top_path+'/TrafficCapturesClient', '**/*request_*_client.pcap'), recursive=True))
        parallel_results = Parallel(n_jobs=-1)(delayed(process_pcap_features_client)(path) for path in client_pcap_paths)
        # Unpack the results
        client_paths, sizes_in, sizes_out = zip(*parallel_results)
        results = {'sizes_in_onion': [],
                   'sizes_in_clear': [],
                   'sizes_out_onion': [],
                   'sizes_out_clear': []}

        for client_path, s_in, s_out in zip(client_paths, sizes_in, sizes_out):
            if 'alexa' in client_path:
                results['sizes_in_clear'].append(sum(s_in))
                results['sizes_out_clear'].append(sum(s_out))
            else:
                results['sizes_in_onion'].append(sum(s_in))
                results['sizes_out_onion'].append(sum(s_out))

        joblib.dump(results, results_file)

    else:
        results = joblib.load(results_file)

    return results['sizes_in_onion'], results['sizes_in_clear'], results['sizes_out_onion'], results['sizes_out_clear']


def remove_outliers(vector):
    z_scores = np.abs((vector - np.mean(vector)) / np.std(vector))
    threshold_z = 3
    outliers = np.where(z_scores > threshold_z)
    threshold_percentile = 99
    max_threshold = np.percentile(vector, threshold_percentile)
    outliers = np.where(vector > max_threshold)
    filtered_data = [value for i, value in enumerate(vector) if i not in outliers[0]]

    return filtered_data 


def divide_list_elements(lst, divisor):
    for i in range(len(lst)):
        lst[i] /= divisor

    return lst


def is_list_of_lists(element):
    return isinstance(element, list) and all(isinstance(sublist, list) for sublist in element)


def bytes_to_mbytes_lst(lst):
    if is_list_of_lists(lst):
        for inner_lst in lst:
            inner_lst = divide_list_elements(inner_lst, (1024 * 1024))
        return lst
    else:
        return divide_list_elements(lst, (1024 * 1024))
    

def bytes_to_kbytes_lst(lst):
    if is_list_of_lists(lst):
        for inner_lst in lst:
            inner_lst = divide_list_elements(inner_lst, 1024)
        return lst
    else:
        return divide_list_elements(lst, 1024)


def plot_session_statistics():
    #import random

    plt.rcParams["figure.figsize"] = (16,12)
    tick_labels_font_size = 40
    axis_labels_font_size = 46
    legend_font_size = 40
    
    
    #fig, axs = plt.subplots(
    #                    nrows=2, 
    #                    ncols=3)

    
    pcaps = ["test", "train", "validate"]
    datasets = ["OSTest", "OSTrain", "OSValidate"]
    labels = ["dataset1", "dataset2", "dataset3"]
    colors = ['pink', 'lightblue', 'lightgreen']
    #colors = ['pink', 'lightblue', 'orange']

    results_file = 'onion_page_statistics.joblib'
    results = statistics_utils.load_dict_from_file(results_file)
    onions = list(onion_pages.keys())

    results_dir = "results/"
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)


    # ---- 1. Plot session durations CDF for 3 different datasets
    #session_durations_minutes = []
    #for dataset_name, color, label in zip(datasets, colors, labels):
    _, ax1 = plt.subplots()
    dataset = datasets[1]
    pcap = pcaps[1]
    pcaps_path = f"/mnt/nas-shared/torpedo/datasets_20220503/dataset_{pcap}/experiment_results_filtered"
    top_path = f"/mnt/nas-shared/torpedo/extracted_features_{dataset}"
    #session_durations_minutes += [get_session_durations(top_path, dataset_name)]

    x, y = ecdf4plot(get_session_durations(top_path, dataset))
    #axs[0, 0].plot(x, y, color=color, label=label, linewidth=4)
    ax1.plot(x, y, color='tab:blue', label='Session duration (min)', linewidth=4)

    x, y = ecdf4plot(get_requests_per_session(pcaps_path, pcap, dataset))
    ax1.plot(x, y, color='tab:orange', label='# requests per session', linewidth=4)
    
    
    #bplot = axs[0, 0].boxplot(session_durations_minutes,
    #                vert=True,
    #                patch_artist=True,
    #                labels=labels)
    #axs[0, 0].set_ylabel("Session duration (minutes)", fontsize=axis_labels_font_size)
    ax1.set_ylabel("CDF", fontsize=axis_labels_font_size)
    #axs[0, 0].set_xlabel("Session duration (minutes)", fontsize=axis_labels_font_size)
    ax1.set_xlim(0, 21)
    ax1.legend(loc="lower right", fontsize=legend_font_size)
    # fill with colors
    #for patch, color in zip(bplot['boxes'], colors):
    #    patch.set_facecolor(color)
    ax1.tick_params(axis='both', labelsize=tick_labels_font_size)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{results_dir}plot1.pdf")
    plt.savefig(f"{results_dir}plot1.png")


    """
    # ---- 2. Plot number of requests per session CDF for 3 different datasets
    #session_requests = []
    for dataset_pcap_name, dataset_name, color, label in zip(pcaps, datasets, colors, labels):
        pcaps_path = f"/mnt/nas-shared/torpedo/datasets_20220503/dataset_{dataset_pcap_name}/experiment_results_filtered"
        print("pcaps_path", pcaps_path)
        #session_requests += [get_requests_per_session(pcaps_path, dataset_pcap_name, dataset_name)]

        x, y = ecdf4plot(get_requests_per_session(pcaps_path, dataset_pcap_name, dataset_name))
        axs[0, 1].plot(x, y, color=color, label=label, linewidth=4)
    
    #bplot = axs[0, 1].boxplot(session_requests,
    #                vert=True,
    #                patch_artist=True,
    #                labels=labels)

    axs[0, 1].set_ylabel("CDF", fontsize=axis_labels_font_size)  
    axs[0, 1].set_xlabel("# requests per session", fontsize=axis_labels_font_size)  
    axs[0, 1].set_xlim(0, 21)
   # axs[0, 1].set_ylabel("# requests per session", fontsize=axis_labels_font_size)
    axs[0, 1].legend(loc="lower right")
    # fill with colors
    #for patch, color in zip(bplot['boxes'], colors):
    #    patch.set_facecolor(color)
    """

    
    # ---- 2.
    _, ax2 = plt.subplots()
    onion_labels = onions
    received_requests = statistics_utils.count_requests_received_by_onion(onion_pages)
    # Sort the labels and values together based on the values array
    sorted_pairs = sorted(zip(onion_labels, received_requests), key=lambda x: x[1], reverse=True)
    # Extract the sorted labels and values separately
    onion_labels, received_requests = zip(*sorted_pairs)
    print("--- onion_labels", onion_labels)
    onion_indexes = np.arange(0, len(onions))
    print("--- onion_indexes", onion_indexes)
    ax2.bar(onion_indexes, received_requests)
    ax2.set_xlim(-0.5, max(onion_indexes) + 0.5)
    #axs[1, 1].set_xticklabels(onion_labels)
    ax2.set_xticks(onion_indexes, onion_labels)
    ax2.set_xlabel("Onion service", fontsize=axis_labels_font_size)
    ax2.set_ylabel("# client requests received", fontsize=axis_labels_font_size)
    ax2.tick_params(axis='x', rotation=90)
    ax2.tick_params(axis='both', labelsize=tick_labels_font_size)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{results_dir}plot2.pdf")
    plt.savefig(f"{results_dir}plot2.png")


    # ---- 3. Plot average bytes in per time window per onion service for a single dataset
    _, ax3 = plt.subplots()
    pcaps_path = f"/mnt/nas-shared/torpedo/datasets_20220503/dataset_train/experiment_results_filtered/"
    #onion_labels, times_in, times_out, running_avg_in, running_avg_out = get_average_bytes_transmitted_per_os(pcaps_path)
    onion_labels, sizes_in, sizes_out = get_bytes_transmitted_per_os(pcaps_path)
    #for times_in, avg_in in zip(times_in, running_avg_in):
    #    axs[0, 2].plot(times_in, avg_in)
    bplot1 = ax3.boxplot(bytes_to_kbytes_lst(sizes_in),
                    vert=True,
                    patch_artist=True,
                    labels=onions)
    #axs[0, 2].set_ylabel("Average bytes in", fontsize=axis_labels_font_size)
    #axs[0, 2].set_xlabel("Time (minutes)", fontsize=axis_labels_font_size)
    #axs[0, 2].set_ylabel("Bytes received per request", fontsize=axis_labels_font_size)
    ax3.set_ylabel("Kbs received per request", fontsize=axis_labels_font_size)
    ax3.set_xlabel("Onion service", fontsize=axis_labels_font_size)
    ax3.tick_params(axis='x', rotation=90)
    ax3.tick_params(axis='both', labelsize=tick_labels_font_size)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{results_dir}plot3.pdf")
    plt.savefig(f"{results_dir}plot3.png")


    # ---- 4. Plot average bytes out per time window per onion service for a single dataset
    #for times_out, avg_out in zip(times_out, running_avg_out):
    #    axs[1, 0].plot(times_out, avg_out)
    #axs[1, 0].set_ylabel("Average bytes out", fontsize=axis_labels_font_size)
    #axs[1, 0].set_xlabel("Time (minutes)", fontsize=axis_labels_font_size)
    _, ax4 = plt.subplots()
    bplot2 = ax4.boxplot(bytes_to_kbytes_lst(sizes_out),
                    vert=True,
                    patch_artist=True,
                    labels=onions)
    ax4.set_ylabel("Kbs sent per request", fontsize=axis_labels_font_size)
    ax4.set_xlabel("Onion service", fontsize=axis_labels_font_size)
    ax4.tick_params(axis='x', rotation=90)
    ax4.tick_params(axis='both', labelsize=tick_labels_font_size)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{results_dir}plot4.pdf")
    plt.savefig(f"{results_dir}plot4.png")

    """
    # ---- 5. 
    datasets2 = ["OSTrain", "small_OSTrain", "dataset_client1_is_attacker"]
    for dataset_name, color, label in zip(datasets2, colors, labels):
        print("PLOT 5")
        top_path = f"/mnt/nas-shared/torpedo/extracted_features_{dataset_name}"
        #session_durations_minutes += [get_session_durations(top_path, dataset_name)]

        x, y = ecdf4plot(get_session_durations(top_path, dataset_name))
        axs[1, 1].plot(x, y, color=color, label=label, linewidth=4)

    axs[1, 1].set_ylabel("CDF", fontsize=axis_labels_font_size)
    axs[1, 1].set_xlabel("Session duration (minutes)\n(datasets with different characteristics)", fontsize=axis_labels_font_size)
    axs[1, 1].set_xlim(0, 21)
    axs[1, 1].legend(loc="lower right", fontsize=legend_font_size)
    """

    """
    # ---- 6. 
    pcaps2 = [f"/mnt/nas-shared/torpedo/datasets_20220503/dataset_train/experiment_results_filtered/", f"/mnt/nas-shared/torpedo/datasets_20230521/OSTrain/experiment_results/", f"/mnt/nas-shared/torpedo/datasets_20220516/dataset_client1_is_attacker/experiment_results/"]
    for dataset_pcap_name, dataset_name, color, label in zip(pcaps2, datasets2, colors, labels):
        print("PLOT 6")
        pcaps_path = dataset_pcap_name
        print("pcaps_path",pcaps_path)

        x, y = ecdf4plot(get_requests_per_session(pcaps_path, dataset_pcap_name, dataset_name))
        axs[1, 2].plot(x, y, color=color, label=label, linewidth=4)


    axs[1, 2].set_ylabel("CDF", fontsize=axis_labels_font_size)  
    axs[1, 2].set_xlabel("# requests per session\n(datasets with different characteristics)", fontsize=axis_labels_font_size)  
    axs[1, 2].set_xlim(0, 21)
    axs[1, 2].legend(loc="lower right")
    """


    # ---- 5. Boxplot bytes sent and received per request by all clientes, comparing between onion services and clearnet sites
    _, ax5 = plt.subplots()
    client_labels = ['Received\nwith onion\nservices', 'Received\nwith clearnet\nservices', 'Sent\nwith onion\nservices', 'Sent\nwith clearnet\nservices']
    pcaps_path = f"/mnt/nas-shared/torpedo/datasets_20220503/dataset_train/experiment_results_filtered/"
    sizes_in_os, sizes_in_clear, sizes_out_os, sizes_out_clear = get_bytes_transmitted_per_client(pcaps_path)
    #for times_in, avg_in in zip(times_in, running_avg_in):
    #    axs[0, 2].plot(times_in, avg_in)
    print("sizes_in_os", sizes_in_os[0: 10])
    print("bytes_to_kbytes_lst(sizes_in_os)", bytes_to_kbytes_lst(sizes_in_os)[0: 10])
    print("bytes_to_kbytes_lst(sizes_in_clear)", bytes_to_kbytes_lst(sizes_in_clear)[0: 10])
    print("bytes_to_kbytes_lst(sizes_out_os)", bytes_to_kbytes_lst(sizes_out_os)[0: 10])
    print("bytes_to_kbytes_lst(sizes_out_clear)", bytes_to_kbytes_lst(sizes_out_clear)[0: 10])
    bplot1 = ax5.boxplot([bytes_to_kbytes_lst(sizes_in_os), bytes_to_kbytes_lst(sizes_in_clear), bytes_to_kbytes_lst(sizes_out_os), bytes_to_kbytes_lst(sizes_out_clear)],
                    vert=True,
                    patch_artist=True,
                    labels=client_labels)
    #axs[0, 2].set_ylabel("Average bytes in", fontsize=axis_labels_font_size)
    #axs[0, 2].set_xlabel("Time (minutes)", fontsize=axis_labels_font_size)
    ax5.set_ylabel("Kbs per request", fontsize=axis_labels_font_size)
    #axs[0, 2].set_xlabel("Onion service", fontsize=axis_labels_font_size)
    ax5.set_ylim(0, 11)
    ax5.tick_params(axis='both', labelsize=tick_labels_font_size)
    ax5.spines['top'].set_visible(False)
    ax5.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{results_dir}plot5.pdf")
    plt.savefig(f"{results_dir}plot5.png")
    



    # ---- 6.
    received_requests_in_time = statistics_utils.requests_evolution_in_time()

    start_time = received_requests_in_time[onion_path_to_name[onions[0]]].index[60]  # Replace with your desired start time
    #end_time = start_time + datetime.timedelta(hours=1)  # Set the end time as 1 hour from the start
    end_time = start_time + datetime.timedelta(hours=2)
    # Filter the DataFrame within the specified time range
    desired_time_range_data = {}
    for onion_name, data in received_requests_in_time.items():
        data_in_time_range = data.loc[start_time:end_time]
        data_in_time_range.index = data_in_time_range.index.strftime('%H:%M')
        desired_time_range_data[onion_name] = data_in_time_range
    
    _, ax6 = plt.subplots()
    #axs[1, 2].plot(received_requests_in_time[onion_path_to_name[onions[0]]].index, received_requests_in_time[onion_path_to_name[onions[0]]]['Requests'], label=onions[0])
    
    onions_to_plot = ['o1', 'o2', 'o3', 'o31', 'o25', 'o26']
    colors_to_plot = ['tab:blue', 'tab:pink', 'tab:purple', 'tab:orange', 'tab:green', 'tab:red']
    for onion, color in zip(onions_to_plot, colors_to_plot):
        ax6.plot(desired_time_range_data[onion_path_to_name[onion]].index, desired_time_range_data[onion_path_to_name[onion]]['Requests'], label=onion, color=color, linewidth=4)
    #minutes_labels = np.arange(0, len(received_requests_in_time[onion_path_to_name[onions[0]]].index), 10)
    #axs[1, 2].set_xticks(received_requests_in_time[onion_path_to_name[onions[0]]].index, minutes_labels)
    #axs[1, 2].set_xticks(minutes_labels, minutes_labels)
    x_ticks = data_in_time_range.index[::10]  # Display every 10th label (adjust as needed)
    ax6.set_xticks(x_ticks)
    ax6.set_xlabel("Windows of 1 min for a range of 2 hours", fontsize=axis_labels_font_size)
    ax6.set_ylabel("# client requests received", fontsize=axis_labels_font_size)
    ax6.legend(fontsize=legend_font_size, ncols=6, columnspacing=0.8, borderpad=0.1, handlelength=1, handletextpad=0.3)
    ax6.tick_params(axis='x', rotation=90)
    ax6.tick_params(axis='both', labelsize=tick_labels_font_size)
    ax6.spines['top'].set_visible(False)
    ax6.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{results_dir}plot6.pdf")
    plt.savefig(f"{results_dir}plot6.png")


    
    #for i, ax1 in enumerate(axs):
    #    for j, ax2 in enumerate(ax1):
            
            #if i == 1 and j > 0:
            #    continue
            #ax2.tick_params(axis='x', rotation=90)
    
    

    #plt.subplots_adjust(wspace=0.2, hspace=0.37)
    
    
    #plt.savefig(f"{results_dir}dataset_statistics.pdf")
    #plt.savefig(f"{results_dir}dataset_statistics.png")
    

def main():
    plot_session_statistics()


if __name__ == "__main__":
    main()