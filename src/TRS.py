from typing import *
import pycountry
import requests
import json

class searchRelayTimestamp():
    def __init__(self) -> None:
        self.relays = json.loads(requests.get('https://onionoo.torproject.org/details').text)["relays"]

    def filterFirstSeen(self, first_seen:str,
                        preciseStamp:bool=None,
                        greaterStamp:bool=None,
                        lessStamp:bool=None
                        ):
        
        for relay in self.relays:
            if preciseStamp:
                if relay["first_seen"] == first_seen:
                    yield (relay)
            elif greaterStamp:
                if relay["first_seen"] >= first_seen:
                    yield (relay)
            elif lessStamp:
                if relay["first_seen"] <= first_seen:
                    yield (relay)

    def filterLastSeen(self, last_seen:str,
                        preciseStamp:bool=None,
                        greaterStamp:bool=None,
                        lessStamp:bool=None
                        ):
        
        for relay in self.relays:
            if preciseStamp:
                if relay["last_seen"] == last_seen:
                    yield (relay)
            elif greaterStamp:
                if relay["last_seen"] >= last_seen:
                    yield (relay)
            elif lessStamp:
                if relay["last_seen"] <= last_seen:
                    yield (relay)

class searchRelay(searchRelayTimestamp):
    def __init__(self, 
                flags:                  list  = None,
                country:                str   = "",
                first_seen:             str   = "",
                last_seen:              str   = "",
                version:                str   = "",
                recommended_version:    bool  = False,
                guard_pob:              float = 0.0,
                middle_pob:             float = 0.0,
                exit_pob:               float = 0.0
                ) -> None:
        
        self.flags = flags if flags is not None else []
        self.country = country
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.version = version
        self.recommended_version = recommended_version
        self.guard_pob = guard_pob
        self.middle_pob = middle_pob
        self.exit_pob = exit_pob

        self.relays = json.loads(requests.get('https://onionoo.torproject.org/details').text)["relays"]

        # If you want try with your own file relays

        #self.relays = open("relay.json","r")
        #self.relays = json.loads(self.relays.read())["relays"]

    
    def filterFlags(self, flags=None, accurateFlags=True):
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
    def TheFlagSintax(flags:Tuple[str]) -> str:
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

        filteredFlags = []
        for flag in flags:
            lowerFlag = flag.lower()
            if lowerFlag in flagsTypes:
                filteredFlags.append(flagsTypes[lowerFlag])
        
        return filteredFlags

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
                    print("{} not found".format(ke))

    def fitlerReVersion(self,recommended_version=True):
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
                accurateFlags:          bool  = True,
                country:                str   = "",
                first_seen:             str   = "",
                last_seen:              str   = "",
                version:                str   = "",
                recommended_version:    bool  = False
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

if "__main__" == __name__:
    searchRelays = searchRelay()
    combinedRelays=searchRelays.Combiner(
        flags=["Fast","Running"],
        accurateFlags=False,
        country="fr",
        version="0.4.8.11",
        recommended_version=True,
        )
    
    for result in combinedRelays:
        print(result)
