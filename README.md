# Launch program requires root privileges on the operating system
    make
    ./rawhttpget <URL>



IP header
0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |Version|  IHL  |Type of Service|          Total Length         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |         Identification        |Flags|      Fragment Offset    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Time to Live |    Protocol   |         Header Checksum       |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                       Source Address                          |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Destination Address                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Options                    |    Padding    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# IP features implemented:
connect(): we implemented this function to set up the correct IP and port of the remote server
createIPHeader(): we implemented this function to generated an IP header by setting up essential fields in the header,
                  and setting correct checksum in packet.
                  
unpackIP(): we implement this function to unpacks the incoming IP packet and validating the checksums the incoming packet.
            and it also check the validity of IP headers from the remote server.

TCP header
 0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |          Source Port          |       Destination Port        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                        Sequence Number                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Acknowledgment Number                      |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Data |           |U|A|P|R|S|F|                               |
   | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
   |       |           |G|K|H|T|N|N|                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |           Checksum            |         Urgent Pointer        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Options                    |    Padding    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                             data                              |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# TCP features implemented:
createTCPPacket(): we implemented this function to generated an TCP header by setting up essential fields in the header,
                   and Generate pseudo header using 0 as checksum,then replace the checksum calculated by it and repack the returned 
                   TCP header.

unpackTCP(): we implement this function to unpacks the incoming TCP packet and validating the checksums the incoming packet.
             and it also check the validity of TCP headers from the remote server.
             
handshake(): we implemented this function to set up the connect by handshaking. Start with sending a SYN to server. Unpack and
             validate the incoming SYN-ACK packet. Send a ACK for it. Handshake done.

send():      we implemented this function to send request after handshake.Unpack and validate the incoming ACK packet. 
             If it fails validation,resend the request.
             
rev_ack():   we implement this function to Handle the incoming ACK for PSH-ACK when sending http request, and FIN when client wants
             to end the connection.If there's valid ACK within 1 min, assume the sent packet is lost and retransmit. If it does not
             receive any data for 3 min, client start to tear down the connection. And we set the cong cwnd in this function.

recv():      we implement this function to Receive the response of the request. Keep receiving ACK with content from server, 
             and send back ACK for each of them. If there's valid ACK within 1 min, assume the sent packet is lost and retransmit.
             If it does not receive any data for 3 min, client start to tear down the connection. When receiving a packet marked FIN,
             reply to the request from server to end the connection.
             
disconnect() and reply_disconnect(): handle the connection teardown

 
# process of handle sequence and acknowledgement numbers
packet = IP header + TCP header + data

Handshake
        client ---------------------- server
        ----------- SYN seq = x ----------->
        <--SYN, ACK seq = y, ack = x + 1 --
        --- ACK seq = x + 1, ack = y + 1 ---
http request
        - PSH-ACK seq = x + 1, ack = y + 1, len = z ->
        <----- ACK seq = y + 1, ack = x + 1 + z ------
        <- ACK seq = y + 1, ack = x + 1 + z, len = k -
        --- ACK seq = x + 1 + z, ack = y + 1 + k ---->
                            ...
reply to disconnect
        <-- PSH,FIN,ACK seq = m, ack = n, len = k --
        ---- FIN, ACK seq = n, ack = m + k + 1 ---->
         <---- ACK seq = m + k + 1, ack = n + 1 ----
disconnect
        -------- FIN seq = m, ack = n -------->
        <----- ACK seq = k , ack = m + 1 ------
        <---- FIN-ACK seq = w, ack = m + 1 ----
        ---- ACK seq = m + 1 , ack = w + 1 ---->
