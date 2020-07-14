class Dummy:

    import time

    debugLevel = 0
    enabled = False
    master = None
    msgBuffer = None
    twcID = 1234
    timeLastTx = 0

    def __init__(self, master):
        self.master = master
        try:
            self.debugLevel = master.config["config"]["debugLevel"]
        except KeyError:
            pass

        # Unload if this module is disabled or misconfigured
        if (not self.enabled):
            self.master.releaseModule("lib.TWCManager.Interface","Dummy");
            return None

        # Configure the module
        if "interface" in master.config:
            self.twcID = master.config["interface"]["Dummy"].get("twcID", 1234)

    def close(self):
        # NOOP - No need to close anything
        return 0

    def getBufferLen(self):
        # This function returns the size of the recieve buffer.
        # This is used by read functions to determine if information is waiting
        return len(self.msgBuffer)

    def send(self, msg):
        # NOOP - TBD

        self.master.debugLog(9, "IfaceDummy", "Tx@: " + self.master.hex_str(msg))
        self.timeLastTx = self.time.time()
        return 0

    def read(self, len):
        # Read our buffered messages. We simulate this by making a copy of the
        # current message buffer, clearing the shared message buffer and then
        # returning the copied message to TWCManager. This is what it would look
        # like if we read from a serial interface
        localMsgBuffer = self.msgBuffer
        self.msgBuffer = None
        self.master.debugLog(
            9, "IfaceDummy", "Rx@: " + self.master.hex_str(localMsgBuffer)
        )
        return localMsgBuffer

    def sendInternal(self, msg):
        # The sendInternal function takes a message that we would like to send
        # from the dummy module to the TWCManager, adds the required checksum,
        # updates the internal message buffer with the sent message and then
        # allows this to be polled & read by TWCManager on the next loop iteration

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
        self.master.debugLog(9, "IfaceDummy", "TxInt@: " + self.master.hex_str(msg))

        self.msgBuffer = msg
