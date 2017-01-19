""" MODBUS backend SACADE tool API. """

##  @file   modbus.py
#   @brief  MODBUS backend SACADE tool API.
#   @author Maxime Puys
#   @date   2016-11-19
#   MODBUS backend SACADE tool API.
#
#   Copyright (c) 2016 University Grenoble Alpes
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#   IN THE SOFTWARE.


import scapy.all as scpy


READ_QUEUE = {
    "Coil": [],
    "DiscreteInput": [],
    "HoldingRegister": [],
    "InputRegister": []
}

WRITE_QUEUE = {
    "Coil": [],
    "DiscreteInput": [],
    "HoldingRegister": [],
    "InputRegister": []
}


def modbusHandler(serverPort, callback):
    def handler(pkt):
        if scpy.TCP in pkt and scpy.Raw in pkt:
            modbusPkt = pkt[scpy.Raw].load
            seqNb = int.from_bytes(modbusPkt[0:2], byteorder="big")
            fnCode = modbusPkt[7]
            payload = modbusPkt[8:]

            parsed = []

            if pkt[scpy.TCP].dport == serverPort:
                parsed = handleRequest(fnCode, payload)
            elif pkt[scpy.TCP].sport == serverPort:
                parsed = handleResponse(fnCode, payload)
            else:
                return

            callback(seqNb, parsed)

    return handler


##  Handles a MODBUS request of multiple coils reading (fn code 1).
#   Stores each requested address into `READ_QUEUE`.
#   @param  payload Request payloads containing:
#                       * `fisrt`: Address of first coil to read (2 bytes)
#                       * `nbAddr`: Number of coils to read (2 bytes)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here ReadReq)
#               * Type of the data (here Coil)
#               * Address requested.
def handleReqReadMultCO(payload):
    """ Handles a MODBUS request of multiple coils reading (fn code 1). """
    first = int.from_bytes(payload[:2], byteorder="big")
    nbAddr = int.from_bytes(payload[2:4], byteorder="big")
    addresses = range(first, first+nbAddr)

    READ_QUEUE["Coil"] += addresses
    return [("ReadReq", [("Coil", addr) for addr in addresses])]


##  Handles a MODBUS response of multiple coils reading (fn code 1).
#   Pops from `READ_QUEUE` for each responded value.
#   @param  payload Response payloads containing:
#                       * Number of bytes of coil values to follow (1 byte)
#                       * Coil values (8 coils per byte)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here ReadResp)
#               * Type of the data (here Coil)
#               * Address requested.
#               * Value returned.
def handleRespReadMultCO(payload):
    """ Handles a MODBUS response of multiple coils reading (fn code 1). """
    bits = int.from_bytes(payload[1:], byteorder="big")
    tmp = []
    res = [("ReadResp", tmp)]
    while True:
        try:
            req = READ_QUEUE["Coil"].pop(0)
            bit = bits & 0x1
            bits >>= 1
            tmp += [(("Coil", req), bit)]
        except IndexError:
            break

    return res


##  Handles a MODBUS request of multiple discrete inputs reading (fn code 2).
#   Stores each requested address into `READ_QUEUE`.
#   @param  payload Request payloads containing:
#                       * `fisrt`: Address of first discrete input to read (2 bytes)
#                       * `nbAddr`: Number of discrete inputs to read (2 bytes)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here ReadReq)
#               * Type of the data (here DiscreteInput)
#               * Address requested.
def handleReqReadMultDI(payload):
    """ Handles a MODBUS request of multiple discrete inputs reading (fn code 2). """
    first = int.from_bytes(payload[:2], byteorder="big")
    nbAddr = int.from_bytes(payload[2:4], byteorder="big")
    addresses = range(first, first+nbAddr)

    READ_QUEUE["DiscreteInput"] += addresses
    return [("ReadReq", [("DiscreteInput", addr) for addr in addresses])]


##  Handles a MODBUS response of multiple discrete inputs reading (fn code 2).
#   Pops from `READ_QUEUE` for each responded value.
#   @param  payload Response payloads containing:
#                       * Number of bytes of discrete input values to follow (1 byte)
#                       * Discrete input values (8 discrete inputs per byte)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here ReadResp)
#               * Type of the data (here DiscreteInput)
#               * Address requested.
#               * Value returned.
def handleRespReadMultDI(payload):
    """ Handles a MODBUS response of multiple discrete inputs reading (fn code 2). """
    bits = int.from_bytes(payload[1:], byteorder="big")
    tmp = []
    res = [("ReadResp", tmp)]
    while True:
        try:
            req = READ_QUEUE["DiscreteInput"].pop(0)
            bit = bits & 0x1
            bits >>= 1
            tmp += [(("DiscreteInput", req), bit)]
        except IndexError:
            break

    return res


##  Handles a MODBUS request of multiple holding registers reading (fn code 3).
#   Stores each requested address into `READ_QUEUE`.
#   @param  payload Request payloads containing:
#                       * `fisrt`: Address of first holding register to read (2 bytes)
#                       * `nbAddr`: Number of holding registers to read (2 bytes)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here ReadReq)
#               * Type of the data (here HoldingRegister)
#               * Address requested.
def handleReqReadMultHR(payload):
    """ Handles a MODBUS request of multiple holding registers reading (fn code 3). """
    first = int.from_bytes(payload[:2], byteorder="big")
    nbAddr = int.from_bytes(payload[2:4], byteorder="big")
    addresses = range(first, first+nbAddr)

    READ_QUEUE["HoldingRegister"] += addresses
    return [("ReadReq", [("HoldingRegister", addr) for addr in addresses])]


##  Handles a MODBUS response of multiple holding registers reading (fn code 3).
#   Pops from `READ_QUEUE` for each responded value.
#   @param  payload Response payloads containing:
#                       * Number of bytes of holding register values to follow (1 byte)
#                       * Holding registers values (2 bytes each)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here ReadResp)
#               * Type of the data (here HoldingRegister)
#               * Address requested.
#               * Value returned.
def handleRespReadMultHR(payload):
    """ Handles a MODBUS response of multiple holding registers reading (fn code 3). """
    values = payload[1:]
    tmp = []
    res = [("ReadResp", tmp)]
    while True:
        try:
            req = READ_QUEUE["HoldingRegister"].pop(0)
            value = int.from_bytes(values[:2], byteorder="big")
            values = values[2:]
            tmp += [(("HoldingRegister", req), value)]
        except IndexError:
            break

    return res


##  Handles a MODBUS request of multiple input registers reading (fn code 4).
#   Stores each requested address into `READ_QUEUE`.
#   @param  payload Request payloads containing:
#                       * `fisrt`: Address of first input register to read (2 bytes)
#                       * `nbAddr`: Number of input registers to read (2 bytes)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here ReadReq)
#               * Type of the data (here InputRegister)
#               * Address requested.
def handleReqReadMultIR(payload):
    """ Handles a MODBUS request of multiple input registers reading (fn code 4). """
    first = int.from_bytes(payload[:2], byteorder="big")
    nbAddr = int.from_bytes(payload[2:4], byteorder="big")
    addresses = range(first, first+nbAddr)

    READ_QUEUE["InputRegister"] += addresses
    return [("ReadReq", [("InputRegister", addr) for addr in addresses])]


##  Handles a MODBUS response of multiple input registers reading (fn code 4).
#   Pops from `READ_QUEUE` for each responded value.
#   @param  payload Response payloads containing:
#                       * Number of bytes of input register values to follow (1 byte)
#                       * Input registers values (2 bytes each)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here ReadResp)
#               * Type of the data (here InputRegister)
#               * Address requested.
#               * Value returned.
def handleRespReadMultIR(payload):
    """ Handles a MODBUS response of multiple input registers reading (fn code 4). """
    values = payload[1:]
    tmp = []
    res = [("ReadResp", tmp)]
    while True:
        try:
            req = READ_QUEUE["InputRegister"].pop(0)
            value = int.from_bytes(values[:2], byteorder="big")
            values = values[2:]
            tmp += [(("InputRegister", req), value)]
        except IndexError:
            break

    return res


##  Handles a MODBUS request of single coil writing (fn code 5).
#   Stores each requested address and value into `WRITE_QUEUE`.
#   @param  payload Request payload containing:
#                       * `addr`: Address of coil to write (2 bytes)
#                       * `value`: Value to write into `addr` (2 bytes, normaly 0x0000 or 0xff00)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here WriteReq)
#               * Type of the data (here Coil)
#               * Address requested.
#               * Value to write.
def handleReqWriteSingCO(payload):
    """ Handles a MODBUS request of single coil writing (fn code 5). """
    addr = int.from_bytes(payload[:2], byteorder="big")
    value = int.from_bytes(payload[2:4], byteorder="big")
    res = (addr, value)

    WRITE_QUEUE["Coil"] += [res]
    return [("WriteReq", [("Coil", res)])]


##  Handles a MODBUS response of single coil writing (fn code 5).
#   Pops from `WRITE_QUEUE` for each responded value.
#   @param  payload Response payload containing:
#                       * `addr`: Address of coil to write (2 bytes)
#                       * `value`: Value written `addr` (2 bytes, normaly 0x0000 or 0xff00)
#   @return A tuples containing:
#               * Type of the request (here WriteResp)
#               * Type of the data (here Coil)
#               * Address requested.
#               * Value written.
def handleRespWriteSingCO(payload):
    """ Handles a MODBUS response of single coil writing (fn code 5). """
    addr = int.from_bytes(payload[:2], byteorder="big")
    value = int.from_bytes(payload[2:4], byteorder="big")
    res = (addr, value)

    WRITE_QUEUE["Coil"].pop(0)
    return [("WriteResp", [("Coil", res)])]


##  Handles a MODBUS request of multiple coils writing (fn code 15).
#   Stores each requested address and value into `WRITE_QUEUE`.
#   @param  payload Request payloads containing:
#                       * `addr`: Address of the first coil to write (2 bytes)
#                       * `nbAddr`: Number of coils to force/write (2 bytes)
#                       * `nbBytes`: Number of bytes of coil values to follow (1 byte)
#                       * `bits`: Coil values (8 coils per byte)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here WriteReq)
#               * Type of the data (here Coil)
#               * Address requested.
#               * Value to write.
def handleReqWriteMultCO(payload):
    """ Handles a MODBUS request of multiple coils writing (fn code 15). """
    first = int.from_bytes(payload[:2], byteorder="big")
    nbAddr = int.from_bytes(payload[2:4], byteorder="big")
    bits = int.from_bytes(payload[5:], byteorder="big")

    res = []
    for addr in range(first, first+nbAddr):
        bit = 0x0000 if bits & 0x1 == 0 else 0xFF00
        bits >>= 1
        res += [(addr, bit)]

    WRITE_QUEUE["Coil"] += res
    return [("WriteReq", [(("Coil", addr), bit) for addr,bit in res])]


##  Handles a MODBUS response of multiple coils writing (fn code 15).
#   Stores each requested address and value into `WRITE_QUEUE`.
#   @param  payload Request payloads containing:
#                       * `addr`: Address of the first coil to write (2 bytes)
#                       * `nbAddr`: Number of coils to force/write (2 bytes)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here WriteResp)
#               * Type of the data (here Coil)
#               * Address requested.
def handleRespWriteMultCO(payload):
    """ Handles a MODBUS response of multiple coils writing (fn code 15). """
    first = int.from_bytes(payload[:2], byteorder="big")
    nbAddr = int.from_bytes(payload[2:4], byteorder="big")

    addresses = range(first, first+nbAddr)
    for _ in addresses:
        WRITE_QUEUE["Coil"].pop(0)

    return [("WriteResp", [("Coil", addr) for addr in addresses])]


##  Handles a MODBUS request of single holding register writing (fn code 6).
#   Stores each requested address and value into `WRITE_QUEUE`.
#   @param  payload Request payload containing:
#                       * `addr`: Address of holding register to write (2 bytes)
#                       * `value`: Value to write into `addr` (2 bytes)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here WriteReq)
#               * Type of the data (here HoldingRegister)
#               * Address requested.
#               * Value to write.
def handleReqWriteSingHR(payload):
    """ Handles a MODBUS request of single holding register writing (fn code 6). """
    addr = int.from_bytes(payload[:2], byteorder="big")
    value = int.from_bytes(payload[2:4], byteorder="big")

    WRITE_QUEUE["HoldingRegister"] += [(addr, value)]
    return [("WriteReq", [(("HoldingRegister", addr), value)])]


##  Handles a MODBUS response of single holding register writing (fn code 6).
#   Pops from `WRITE_QUEUE` for each responded value.
#   @param  payload Response payload containing:
#                       * `addr`: Address of holding register to write (2 bytes)
#                       * `value`: Value written `addr` (2 bytes)
#   @return A tuples containing:
#               * Type of the request (here WriteResp)
#               * Type of the data (here HoldingRegister)
#               * Address requested.
#               * Value written.
def handleRespWriteSingHR(payload):
    """ Handles a MODBUS response of single holding register writing (fn code 6). """
    addr = int.from_bytes(payload[:2], byteorder="big")
    value = int.from_bytes(payload[2:4], byteorder="big")

    WRITE_QUEUE["HoldingRegister"].pop(0)
    return [("WriteResp", [(("HoldingRegister", addr), value)])]


##  Handles a MODBUS request of multiple holding registers writing (fn code 16).
#   Stores each requested address and value into `WRITE_QUEUE`.
#   @param  payload Request payloads containing:
#                       * `addr`: Address of the first holding register to write (2 bytes)
#                       * `nbAddr`: Number of holding registers to force/write (2 bytes)
#                       * `nbBytes`: Number of bytes of holding register values to follow (1 byte)
#                       * `values`: Holding register values (2 bytes each)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here WriteReq)
#               * Type of the data (here HoldingRegister)
#               * Address requested.
#               * Value to write.
def handleReqWriteMultHR(payload):
    """ Handles a MODBUS request of multiple holding registers writing (fn code 16). """
    first = int.from_bytes(payload[:2], byteorder="big")
    nbAddr = int.from_bytes(payload[2:4], byteorder="big")
    values = payload[5:]

    res = []
    for addr in range(first, first+nbAddr):
        value = int.from_bytes(values[:2], byteorder="big")
        values = values[2:]
        res += [(addr, value)]

    WRITE_QUEUE["HoldingRegister"] += res
    return [("WriteReq", [(("HoldingRegister", addr), value) for addr,value in res])]


##  Handles a MODBUS response of multiple holding registers writing (fn code 16).
#   Stores each requested address and value into `WRITE_QUEUE`.
#   @param  payload Request payloads containing:
#                       * `addr`: Address of the first holding register to write (2 bytes)
#                       * `nbAddr`: Number of holding registers to force/write (2 bytes)
#   @return A list of `nbAddr` tuples containing:
#               * Type of the request (here WriteResp)
#               * Type of the data (here HoldingRegister)
#               * Address requested.
def handleRespWriteMultHR(payload):
    """ Handles a MODBUS response of multiple holding registers writing (fn code 16). """
    first = int.from_bytes(payload[:2], byteorder="big")
    nbAddr = int.from_bytes(payload[2:4], byteorder="big")

    addresses = range(first, first+nbAddr)
    for _ in addresses:
        WRITE_QUEUE["HoldingRegister"].pop(0)

    return [("WriteResp", [("HoldingRegister", addr) for addr in addresses])]


##  Handles a MODBUS request.
#   @param  fnCode  MODBUS function code.
#   @param  payload Request payload.
#   @return A list of parsed requests as tuples.
def handleRequest(fnCode, payload):
    """ Handles a MODBUS request. """
    if fnCode == 1:
        return handleReqReadMultCO(payload)
    elif fnCode == 2:
        return handleReqReadMultDI(payload)
    elif fnCode == 3:
        return handleReqReadMultHR(payload)
    elif fnCode == 4:
        return handleReqReadMultIR(payload)
    elif fnCode == 5:
        return handleReqWriteSingCO(payload)
    elif fnCode == 6:
        return handleReqWriteSingHR(payload)
    elif fnCode == 15:
        return handleReqWriteMultCO(payload)
    elif fnCode == 16:
        return handleReqWriteMultHR(payload)
    else:
        pass


##  Handles a MODBUS response.
#   @param  fnCode  MODBUS function code.
#   @param  payload Response payload.
#   @return A list of parsed response as tuples.
def handleResponse(fnCode, payload):
    """ Handles a MODBUS response. """
    if fnCode == 1:
        return handleRespReadMultCO(payload)
    elif fnCode == 2:
        return handleRespReadMultDI(payload)
    elif fnCode == 3:
        return handleRespReadMultHR(payload)
    elif fnCode == 4:
        return handleRespReadMultIR(payload)
    elif fnCode == 5:
        return handleRespWriteSingCO(payload)
    elif fnCode == 6:
        return handleRespWriteSingHR(payload)
    elif fnCode == 15:
        return handleRespWriteMultCO(payload)
    elif fnCode == 16:
        return handleRespWriteMultHR(payload)
    else:
        pass
