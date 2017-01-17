#!/usr/bin/env python3

from context import icscrack

import argparse
import scapy.all as scpy
import yaml

SERVER_PORT = 5020


def parseYaml(path):
    with open(path, "r") as handle:
        yamlObj = yaml.load(handle.read())
        servers = yamlObj["topology"]["servers"]

        res = []
        for name, attributes in servers.items():
            res.append(icscrack.Automaton.fromYaml(attributes["behavior"]))

        return res


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
    automata = parseYaml(args.yaml)
    if args.pcap:
        if args.verbose:
            print("[+] Loading pcap {}".format(args.pcap))

        pcap = scpy.rdpcap(args.pcap)
        for pkt in pcap:
            res = icscrack.modbusCallback(SERVER_PORT, automata)(pkt)
            if args.verbose and res:
                print(res)

    else:
        print("[+] Sniffing tcp port {}".format(SERVER_PORT))
        sniffer = scpy.sniff(
            filter="tcp and port {}".format(SERVER_PORT),
            iface="vboxnet2",
            prn=icscrack.modbusCallback(SERVER_PORT, automata)
        )


if __name__ == "__main__":
    main()
