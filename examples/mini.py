#!/usr/bin/env python3

from context import icscrack

import argparse
import scapy.all as scpy
import yaml


SERVER_PORT = 5020


def w_printer(automata):
    def doPrinter(seqNb, parsed):
        for automaton in automata:
            if automaton.getName() not in ("hmi", "bottleFactory"):
                continue

            msgL = sum(
                filter(
                    None,
                    map(
                        lambda _: _[1] if _[0] in ("ReadResp", "WriteReq") else [],
                        parsed
                    )
                ), []
            )

            if msgL:
                res = automaton.update(dict(msgL))
                if res is not None:
                    state,varsL = res
                    #varsL = [automaton.getVariableName(var) for var,_ in varsL]
                    print("[{}] [{}] {} {}".format(seqNb, automaton.getName(), state, varsL))

    return doPrinter


def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument(
        "--pcap", "-p",
        help="loads and analyze a pcap file",
        type=str
    )

    argParser.add_argument(
        "--verbose", "-v",
        help="verbose mode",
        action="store_true"
    )

    argParser.add_argument(
        "yaml",
        help="yaml file with automata",
        type=str
    )

    args = argParser.parse_args()
    automata = icscrack.fromYaml(args.yaml)
    printer = w_printer(automata)
    if args.pcap:
        if args.verbose:
            print("[+] Loading pcap {}".format(args.pcap))

        pcap = scpy.rdpcap(args.pcap)
        for pkt in pcap:
            res = icscrack.modbusHandler(SERVER_PORT, printer)(pkt)
            if args.verbose and res:
                print(res)

    else:
        print("[+] Sniffing tcp port {}".format(SERVER_PORT))
        sniffer = scpy.sniff(
            filter="tcp and port {}".format(SERVER_PORT),
            iface="vboxnet2",
            prn=icscrack.modbusHandler(SERVER_PORT, printer)
        )


if __name__ == "__main__":
    main()
