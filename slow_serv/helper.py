from typing import Dict, List
from urllib import parse


def http_kvarray_to_kvmap(
    array: List[str], hashmap: Dict[str, str], *, seperator: str = "=", encoding_type: str = "UTF-8"
) -> Dict[str, str]:
    """
    decode array with structures like ["k1-v1", "k2-v2", "k3-v3"] to kv-map.
    decode k,v from ASCII form(HTTP encoding) to their original form

    Ref: https://stackoverflow.com/questions/6603928/should-i-url-encode-post-data
    """

    for pair_str in array:
        k, v = pair_str.split(seperator)
        hashmap[parse.unquote(k)] = parse.unquote(v)

    return hashmap
