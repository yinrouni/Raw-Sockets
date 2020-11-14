import math
import random
import socket
import sys
import time
from struct import *

RESEND_THRESHOLD = 60


# TCP flags
def getTCPFlags(flag):
    tcp_fin = 0
    tcp_syn = 0
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 0
    tcp_urg = 0

    if flag == 'SYN':
        tcp_syn = 1
    elif flag == 'ACK':
        tcp_ack = 1
    elif flag == 'FIN':
        tcp_fin = 1
    elif flag == 'PSH-ACK':
        tcp_psh = 1
        tcp_ack = 1

    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)
    return tcp_flags


# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0

    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
        s = s + w

    s = (s >> 16) + (s & 0xffff)
    s = s + (s >> 16)

    # complement and mask to 4 byte short
    s = ~s & 0xffff

    return s

def setFileName(url):
    filename = ''
    slash_index = url.rfind('/')
    if slash_index == 6 or slash_index == len(url) - 1:
        filename = "index.html"
    else:
        filename = url[slash_index+1:]

    return filename







class RawSocket:

    def __init__(self):
        self.source_ip = ''
        self.dest_ip = ''
        self.source_port = ''
        self.dest_port = ''

        # create a raw socket
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        except socket.error as msg:
            print('Send socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

        try:
            self.rcv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except socket.error as msg:
            print('Receive socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

    # IP header
    def getIPHeader(self):
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 0  # kernel will fill the correct total length
        ip_id = 54321  # Id of this packet
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0  # kernel will fill the correct checksum
        ip_saddr = socket.inet_aton(self.source_ip)  # Spoof the source ip address if you want to
        ip_daddr = socket.inet_aton(self.dest_ip)

        ip_ihl_ver = (ip_ver << 4) + ip_ihl

        ip_header = pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto,
                         ip_check, ip_saddr, ip_daddr)

        return ip_header

    # TCP header
    def getTCPHeader(self, tcp_seq, tcp_ack_seq, user_data, flag):
        # tcp header fields
        tcp_source = self.source_port  # source port
        tcp_dest = self.dest_port  # destination port

        tcp_doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes

        tcp_window = socket.htons(5840)  # maximum allowed window size
        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_check = 0
        tcp_urg_ptr = 0

        # tcp flags
        tcp_flags = getTCPFlags(flag)

        # the ! in the pack format string means network order
        tcp_header = pack('!HHLLBBHHH', tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,
                          tcp_window, tcp_check, tcp_urg_ptr)

        tcp_check = self.checkPseudoHeader(tcp_header, user_data)
        tcp_header = pack('!HHLLBBH', tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,
                          tcp_window) + pack('H', tcp_check) + pack('!H', tcp_urg_ptr)

        return tcp_header

    # pseudo header for checksum
    def checkPseudoHeader(self, tcp_header, user_data):
        source_address = socket.inet_aton(self.source_ip)
        dest_address = socket.inet_aton(self.dest_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header) + len(user_data)

        psh = pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
        psh = psh + tcp_header + user_data

        tcp_check = checksum(psh)

        return tcp_check

    # handshake
    def handshake(self):
        seq_number = random.randint(0, math.pow(2, 31))
        seq_ack_num = 0

        # send first SYN
        ip_header = self.getIPHeader()
        tcp_header = self.getTCPHeader(seq_number, seq_ack_num, '', 'SYN')
        packet = ip_header + tcp_header

        start = time.clock()
        self.socket.sendto(packet, (self.dest_ip, self.dest_port))
        print('sent SYN at ' + str(start))

        # receive SYN_ACK
        # TODO: retry and timeout
        recv_packet = self.rcv_socket.recvfrom(65565)
        print('received SYN-ACK at' + str(time.clock()))
        print(recv_packet)










    #     send ACK

    # connect
