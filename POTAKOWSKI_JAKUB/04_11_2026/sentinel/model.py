from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from ipaddress import ip_address
import hashlib
import json
import re

CATEGORIES = ('CONNECTION','HTTP_REQUEST','DNS_QUERY','AUTH_SUCCESS','AUTH_FAILURE')
COLUMNS = ('timestamp','sensor_name','src_ip','dst_ip','src_port','dst_port','protocol','event_type','action','bytes','duration_ms')
EPOCH = datetime(1970,1,1,tzinfo=timezone.utc)

def utc(microseconds):
    return (EPOCH+timedelta(microseconds=microseconds)).isoformat(timespec='microseconds').replace('+00:00','Z')

def number(value, port=False):
    if port and value=='':return None
    if not re.fullmatch('[0-9]+',value):raise ValueError('expected unsigned integer')
    result=int(value)
    if result>9223372036854775807:raise ValueError('integer exceeds SQLite range')
    if port and not 1<=result<=65535:raise ValueError('port outside 1..65535')
    return result

@dataclass(frozen=True)
class Event:
    instant:int
    sensor:str
    source:str
    target:str
    sport:int|None
    dport:int|None
    protocol:str
    category:str
    action:str
    octets:int
    elapsed:int

    @classmethod
    def parse(cls,row):
        if None in row or any(row.get(k) is None for k in COLUMNS):raise ValueError('wrong field count')
        if 'T' not in row['timestamp']:raise ValueError('timestamp requires ISO date and time')
        dt=datetime.fromisoformat(row['timestamp'].replace('Z','+00:00'))
        dt=dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
        delta=dt-EPOCH
        instant=(delta.days*86400+delta.seconds)*1000000+delta.microseconds
        if instant<0:raise ValueError('timestamp before 1970 unsupported')
        if not row['sensor_name'].strip():raise ValueError('empty sensor')
        if row['protocol'] not in ('TCP','UDP','ICMP'):raise ValueError('unknown protocol')
        if row['event_type'] not in CATEGORIES:raise ValueError('unknown event type')
        if row['action'] not in ('ALLOW','BLOCK'):raise ValueError('unknown action')
        return cls(instant,row['sensor_name'],str(ip_address(row['src_ip'])),str(ip_address(row['dst_ip'])),
                   number(row['src_port'],True),number(row['dst_port'],True),row['protocol'],row['event_type'],row['action'],number(row['bytes']),number(row['duration_ms']))

    def fingerprint(self):
        return hashlib.sha256(json.dumps(asdict(self),sort_keys=True).encode()).hexdigest()
