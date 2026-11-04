"""Central configuration: detection thresholds and validation vocabularies.

Thresholds are fixed constants for version 1 (see the assignment brief, slide 14).
"""

# Event types known to the system, with their default severity.
KNOWN_EVENT_TYPES = {
    "HTTP_REQUEST": "LOW",
    "CONNECTION": "LOW",
    "DNS_QUERY": "LOW",
    "AUTH_SUCCESS": "INFO",
    "AUTH_FAILURE": "MEDIUM",
}

VALID_PROTOCOLS = ("TCP", "UDP", "ICMP")
VALID_ACTIONS = ("ALLOW", "BLOCK")
ALERT_STATUSES = ("NEW", "INVESTIGATING", "CLOSED")

# Detection rules. Windows are fixed (aligned) buckets in UTC.
RULES = {
    "PORT_SCAN": {
        "threshold": 20,          # >= 20 distinct destination ports
        "window_seconds": 300,    # same src + dst, 5-minute bucket
        "severity": "HIGH",
    },
    "BRUTE_FORCE": {
        "threshold": 8,           # >= 8 AUTH_FAILURE events
        "window_seconds": 300,    # same src + dst + service port, 5-minute bucket
        "severity": "HIGH",
    },
    "TRAFFIC_FLOOD": {
        "threshold": 150,         # >= 150 events
        "window_seconds": 60,     # same src + dst + dst port, 1-minute bucket
        "severity": "CRITICAL",
    },
}
