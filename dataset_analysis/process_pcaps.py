from scapy.all import *
import traceback
import numpy as np


class InvalidPcapException(Exception):
    def __init__(self, path):  
        message = "No data could be read!"         
        super().__init__(f'{message} : {path}')


def skip_packets(dport, sport):
    """Return True or False

    True if this packet should be skipped or False if this packet should be kept
    """

    # Internal communications between client Docker containers to use Tor socket
    if(dport == 9050 or sport == 9050):
        return True

    # Do not target packets produced due to synchronizing REST calls
    if(dport == 5005 or sport == 5005):
        return True

    # skip HTTP packets to manage Google Cloud instances
    if(dport == 80 or sport == 80):
        return True

    # Internal communications between onion Docker containers to host the onion website
    if(dport == 8080 or sport == 8080):
        return True

    return False


def filter_empty_ack(pkt):
    if pkt[TCP].flags & 0x10 and len(pkt[TCP].payload) == 0:
        ip_len = pkt[IP].len
        ip_hdr_len = pkt[IP].ihl * 4
        tcp_hdr_len = pkt[TCP].dataofs * 4
        payload_len = ip_len - ip_hdr_len - tcp_hdr_len
        if payload_len == 0:
            return True
        
    return False


def get_captures_start_end_times(fileName):
    try:
        cap = PcapReader(fileName)
    except Exception as e:
        print("Problem parsing pcap {}".format(fileName))
        print(e)
        return

    absoluteInitialTime = -1
    maxAbsoluteTime = -1

    #Read one by one
    for i, pkt in enumerate(cap):
        ts = np.float64(pkt.time)

        try:
            if pkt.haslayer(TCP):
                dport = pkt[TCP].dport
                sport = pkt[TCP].sport

                if skip_packets(dport, sport):
                    continue

                # Record first absolute time of all packets
                if absoluteInitialTime == -1:
                    absoluteInitialTime = ts
                elif absoluteInitialTime > ts:
                    absoluteInitialTime = ts

                if maxAbsoluteTime < ts:
                    maxAbsoluteTime = ts

        except Exception as e:
            print(e) #Uncomment to check what error is showing up when reading the pcap
            #Skip this corrupted packet
            traceback.print_exc()
            continue

    return absoluteInitialTime, maxAbsoluteTime


def process_packets(path, machine_ip):
    capture = {'first_ts': 0,
            'last_ts': 0,
            'packetSizes': [],
            'packetSizesIn': [],
            'packetSizesOut': [],
            'packetTimesAbs': [],
            'packetTimesInAbs': [],
            'packetTimesOutAbs': [],
            'totalPacketsIn': 0,
            'totalPacketsOut': 0,
            'totalBytes': 0,
            'totalPackets': 0,
            'totalBytesIn': 0,
            'totalBytesOut': 0
            }


    try:
        # The capture file is not entirely loaded into memory at the same time, 
        # only a packet each time, making it more memory efficient
        cap = PcapReader(path)
    except Exception as e:
        print("Problem parsing pcap {}".format(path))
        print(e)
        traceback.print_exc()
        #continue
        raise InvalidPcapException(path)
    
    for i, pkt in enumerate(cap):
        ts = np.float64(pkt.time)
        size = pkt.wirelen

        try:
            # Target TCP communication
            if pkt.haslayer(TCP):
                src_ip_addr_str = pkt[IP].src
                dst_ip_addr_str = pkt[IP].dst
                
                dport = pkt[TCP].dport
                sport = pkt[TCP].sport

                if skip_packets(dport, sport):
                    continue

                # Filter packets with empty TCP ACK payload
                if filter_empty_ack(pkt):
                    continue
                
                # Record initial and last timestamps
                if(capture['first_ts'] == 0):
                    capture['first_ts'] = ts
                if ts < capture['first_ts']:
                    capture['first_ts'] = ts
                if capture['last_ts'] < ts:
                    capture['last_ts'] = ts

                if(machine_ip in dst_ip_addr_str):
                    capture['packetSizesIn'].append(size)
                    capture['packetTimesInAbs'].append(ts)
                    capture['totalPacketsIn'] += 1

                # If machine is sender
                elif(machine_ip in src_ip_addr_str):
                    capture['packetSizesOut'].append(size)
                    capture['packetTimesOutAbs'].append(ts)
                    capture['totalPacketsOut'] += 1
                    

                # Bytes transmitted statistics
                capture['totalBytes'] += pkt.wirelen
                capture['totalPackets'] += 1

                if (machine_ip in src_ip_addr_str):
                    capture['totalBytesOut'] += size
                else:
                    capture['totalBytesIn'] += size

                # Packet Size statistics
                capture['packetSizes'].append(size)

                # Packet Times statistics
                capture['packetTimesAbs'].append(ts)
            
        except Exception as e:
            print("Corrupted packet")
            print(repr(e))
            print(e)
            traceback.print_exc()

    return capture