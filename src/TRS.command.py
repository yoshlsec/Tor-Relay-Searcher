from typing import *
import pycountry
import argparse
import requests
import json
import sys

class searchRelay():
    def __init__(self, 
                flags:                  list  = None,
                country:                str   = "",
                first_seen:             str   = "",
                last_seen:              str   = "",
                version:                str   = "",
                recommended_version:    bool  = None,
                ) -> None:
        
        self.flags = flags if flags is not None else []
        self.country = country
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.version = version
        self.recommended_version = recommended_version
        
        self.relays = json.loads(requests.get('https://onionoo.torproject.org/details').text)["relays"]
    
    def filterFlags(self, flags=None, accurateFlags=None):
        if flags is None:
            flags = self.flags

        filteredFlags = searchRelay().TheFlagSintax(flags)
        if accurateFlags:
            for relay in self.relays:
                try:
                    if filteredFlags == relay["flags"]:
                        yield relay

                except KeyError as ke:
                    print("{} not found".format(ke))
        else:
            for relay in self.relays:
                try:
                    if all(flag in relay["flags"] for flag in filteredFlags):
                        yield relay

                except KeyError as ke:
                    print("{} not found".format(ke))

    @staticmethod # Function to fix and check relay flags
    def TheFlagSintax(flags:Tuple[str]):
        flagsTypes = {
            "authority": "Authority", 
            "badexit": "BadExit",
            "exit": "Exit", 
            "fast": "Fast", 
            "guard": "Guard", 
            "hsdir": "HSDir",
            "middleonly": "MiddleOnly", 
            "noedconsensus": "NoEdConsensus",
            "running": "Running", 
            "stable": "Stable", 
            "stabledesc": "StableDesc",
            "v2dir": "V2Dir",
            "valid": "Valid"
            }

        
        for flag in flags:
            lowerFlag = flag.lower()
            if lowerFlag in flagsTypes:
                yield flagsTypes[lowerFlag]

    def filterCountry(self, country=None):
        if country is None:
            country = self.country

        list_country = {country.alpha_2: country.name for country in pycountry.countries}

        if country.upper() in list_country:
            for relay in self.relays:
                try:
                    if country.lower() == relay["country"]:
                        yield relay

                except KeyError as ke:
                    print("{} not found".format(ke))
        else:
            print("Check the ISO code, '{}' was not found".format(country))     \
                if len(country) == 2                                            \
                else print("The country code needs to be only 2 characters")
        
    def filterVersion(self, version=None):
            if version is None:
                version = self.version

            for relay in self.relays:
                try:
                    if version == relay["version"]: 
                        yield relay
                except KeyError as ke:
                    print("{} not register for this relay.".format(ke))

    def fitlerReVersion(self,recommended_version=None):
        if recommended_version:
            for relay in self.relays:
                if relay["recommended_version"]:
                    yield relay
        else:
            for relay in self.relays:
                if not relay["recommended_version"]:
                    yield relay

    @staticmethod
    def Combiner(
                flags:                  list  = None,
                accurateFlags:          bool  = False,
                country:                str   = "",
                first_seen:             str   = "",
                last_seen:              str   = "",
                version:                str   = "",
                recommended_version:    bool  = None
                ) -> List[dict]:
        
        instance = searchRelay()
        filteredRelays = instance.relays

        if flags:
            filteredRelays = list(instance.filterFlags(flags, accurateFlags))

        if version:
            instance.relays = filteredRelays
            filteredRelays = list(instance.filterVersion(version))
        
            instance.relays = filteredRelays
            filteredRelays = list(instance.fitlerReVersion(recommended_version))

        if country:
            instance.relays = filteredRelays
            filteredRelays = list(instance.filterCountry(country))

        if first_seen:
            instance.relays = filteredRelays
            filteredRelays = list(instance.filterFirstSeen(
                first_seen.get('first_seen', ''),
                first_seen.get('preciseStamp', None),
                first_seen.get('greaterStamp', None),
                first_seen.get('lessStamp', None)
            ))

        if last_seen:
            instance.relays = filteredRelays
            filteredRelays = list(instance.filterLastSeen(
                last_seen.get('last_seen', ''),
                last_seen.get('preciseStamp', None),
                last_seen.get('greaterStamp', None),
                last_seen.get('lessStamp', None)
            ))

        return filteredRelays

parser = argparse.ArgumentParser(description='Tor relay finder by relay characteristics')

parser.add_argument('--flags', '-f', nargs='+', type=str, default="",dest="flagList", required=False, help="Filter by the flags in a relay")
parser.add_argument( '--acurrate-flags','-af', type=bool, default=None, dest="accurateFlag", required=False, help="Enable a precise flag filter for  a relay")
parser.add_argument('--country','-c', type=str, default="", dest="countryFilter", required=False, help="Filter by the country of the relay")
parser.add_argument('--first-seen','-fs', type=str, default="", dest="firstSeenFilter", required=False, help="Filter by first occurrence")
parser.add_argument('--last-seen', '-ls', type=str, default="", required=False, dest="lastSeenFilter", help="Filter by last occurrence")
parser.add_argument('--version', '-v', type=str, default="", required=False, dest="versionFilter", help="Filter by the version of TOR")
parser.add_argument('--recomemded-version', '-rv', type=bool, default=None, required=False, dest="versionRecommended", help="Filter by the recommended version of TOR")

parser.add_argument('--output','-o', type=str, default=None, required=False, dest="outFile", help="Save the output in a file")
parser.add_argument('--detailed',action='store_true', default=None, required=False, dest="detailed", help="Show all details of the nodes filtered. Recommended with --output/-o argument")

args = parser.parse_args()

if "__main__" == __name__:
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    arguments = {
        "flags": args.flagList if args.flagList else None,
        "accurateFlags": args.accurateFlag if args.accurateFlag is not None else None,
        "country": args.countryFilter if args.countryFilter else None,
        "version": args.versionFilter if args.versionFilter else None,
        "recommended_version": args.versionRecommended if args.versionRecommended is not None else None,
        "first_seen": args.firstSeenFilter if args.firstSeenFilter is not None else None,
        "last_seen": args.lastSeenFilter if args.lastSeenFilter is not None else None
    }

    filtered_arguments = {key: value for key, value in arguments.items() if value}

    searchRelays = searchRelay()
    combinedRelays = searchRelays.Combiner(**filtered_arguments)

    process_relay = lambda relay: json.dumps(relay, indent=4) + '\n' if args.detailed else '\n'.join(relay["or_addresses"]) + '\n'

    if args.outFile:
        with open(args.outFile, "w") as of:
            for relay in combinedRelays:
                    of.write(process_relay(relay))
    else:
        for relay in combinedRelays:
            print(process_relay(relay))
