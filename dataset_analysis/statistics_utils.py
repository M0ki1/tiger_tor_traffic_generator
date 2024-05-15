import joblib

import dataset_statistics


def save_dict_to_file(dictionary, file_path):
    joblib.dump(dictionary, file_path)

    
def load_dict_from_file(file_path):
    return joblib.load(file_path)


def count_requests_received_by_onion(onion_pages):
    import glob
    import os

    # This needs to gather the features straight from the full-onion pcaps
    onion_pcap_paths = list(glob.iglob(os.path.join('/mnt/nas-shared/torpedo/datasets_20220503/dataset_train/experiment_results_filtered/TrafficCapturesOnion', '**/*request_*_hs.pcap'), recursive=True))
    requests_per_os = {}
    reverse_onions = dataset_statistics.create_reverse_mapping(onion_pages)
    
    for onion_url, onion in reverse_onions.items():
        requests_per_os[onion] = 0
        for path in onion_pcap_paths:
            if onion_url in path:
                requests_per_os[onion] += 1
    
    return list(requests_per_os.values())


def process_request(path):
    import query_sumo_dataset
    import process_pcaps

    onion_name = query_sumo_dataset.get_onion_name(path)
    start_time, end_time = process_pcaps.get_captures_start_end_times(path)
    return onion_name, start_time


def requests_evolution_in_time():
    import datetime
    import glob
    import os
    import joblib
    from joblib import Parallel, delayed

    requests_per_os = {}
    requests_in_time = {}

    results_file = 'requests_evolution_in_time.joblib'

    top_path = '/mnt/nas-shared/torpedo/datasets_20220503/dataset_train/experiment_results_filtered/'

    if not os.path.isfile(results_file):
        #dataset = query_sumo_dataset.SumoDataset(top_path)
        onion_pcap_paths = list(glob.iglob(os.path.join(top_path+'TrafficCapturesOnion/', '**/*request_*_hs.pcap'), recursive=True))
        #full_onion_paths = list(glob.iglob(os.path.join(top_path+'TrafficCapturesOnion/', '**/full-onion/*_hs.pcap'), recursive=True))
        #start_time_all, end_time_all = process_pcaps.get_captures_start_end_times(full_onion_paths[0]) # any onion service full capture will do
        #onion_pcap_paths = onion_pcap_paths[:1000]

        #for path in onion_pcap_paths:
            #onion_name = query_sumo_dataset.get_onion_name(path)
            #start_time, end_time = process_pcaps.get_captures_start_end_times(path)

            #if onion_name not in requests_per_os:
            #    requests_per_os[onion_name] = []

            #requests_per_os[onion_name].append(start_time)
        results = Parallel(n_jobs=-1)(delayed(process_request)(path) for path in onion_pcap_paths)

        # Process the results and update requests_per_os dictionary
        requests_per_os = {}
        for onion_name, start_time in results:
            if start_time == -1:
                continue
            if onion_name not in requests_per_os:
                requests_per_os[onion_name] = []
            requests_per_os[onion_name].append(start_time)
        print("requests_per_os", requests_per_os)

        for onion_name in requests_per_os.keys():
            timestamps = [datetime.datetime.fromtimestamp(ts) for ts in requests_per_os[onion_name]]
            print("requests_per_os[onion_name]", requests_per_os[onion_name])
            print("timestamps", timestamps)
            data = pd.DataFrame({'Timestamp': timestamps, 'Requests': np.ones(len(timestamps))})
            data.set_index('Timestamp', inplace=True)
            requests_in_time[onion_name] = data.resample('1T').sum()

        joblib.dump(requests_in_time, results_file)
    
    else:
        requests_in_time = joblib.load(results_file)

    return requests_in_time