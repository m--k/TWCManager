import socket


class TCP:

    import time

    debugLevel = 0
    enabled = False
    master = None
    port = 6000
    server = None
    sock = None
    timeLastTx = 0

    def __init__(self, master):
        self.master = master
        try:
            self.debugLevel = master.config["config"]["debugLevel"]
        except KeyError:
            pass

        # Unload if this module is disabled or misconfigured
        if (not self.enabled):
            self.master.releaseModule("lib.TWCManager.Interface","TCP");
            return None

        # Create TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # If we are configured to listen, open the listening socket
        self.sock.bind(("localhost", self.port))
        self.sock.listen(1)


    def close(self):
        # Close the TCP socket interface
        self.sock.close()

    def getBufferLen(self):
        # This function returns the size of the recieve buffer.
        # This is used by read functions to determine if information is waiting
        return 0

    def read(self, len):
        # Read the specified amount of data from the TCP interface
        return 0

    def send(self, msg):
        # Send msg on the RS485 network. We'll escape bytes with a special meaning,
        # add a CRC byte to the message end, and add a C0 byte to the start and end
        # to mark where it begins and ends.

        msg = bytearray(msg)
        checksum = 0
        for i in range(1, len(msg)):
            checksum += msg[i]

        msg.append(checksum & 0xFF)

        # Escaping special chars:
        # The protocol uses C0 to mark the start and end of the message.  If a C0
        # must appear within the message, it is 'escaped' by replacing it with
        # DB and DC bytes.
        # A DB byte in the message is escaped by replacing it with DB DD.
        #
        # User FuzzyLogic found that this method of escaping and marking the start
        # and end of messages is based on the SLIP protocol discussed here:
        #   https://en.wikipedia.org/wiki/Serial_Line_Internet_Protocol

        i = 0
        while i < len(msg):
            if msg[i] == 0xC0:
                msg[i : i + 1] = b"\xdb\xdc"
                i = i + 1
            elif msg[i] == 0xDB:
                msg[i : i + 1] = b"\xdb\xdd"
                i = i + 1
            i = i + 1

        msg = bytearray(b"\xc0" + msg + b"\xc0")
        self.master.debugLog(9, "IfaceTCP  ", "Tx@: " + self.master.hex_str(msg))

        # self.ser.write(msg)

        self.timeLastTx = self.time.time()
