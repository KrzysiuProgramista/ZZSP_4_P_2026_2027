# Entity relationship diagram

```mermaid
erDiagram
    sensors ||--o{ network_events : observes
    event_types ||--o{ network_events : classifies
    ip_addresses ||--o{ network_events : source
    ip_addresses ||--o{ network_events : destination
    ip_addresses ||--o{ alerts : source
    ip_addresses ||--o{ alerts : target
    alerts ||--o{ alert_events : includes
    network_events ||--o{ alert_events : evidence_for

    sensors {
        int sensor_id PK
        text name UK
        text location
    }
    ip_addresses {
        int ip_id PK
        text address UK
        bool is_private
    }
    event_types {
        int event_type_id PK
        text code UK
        text default_severity
    }
    network_events {
        int event_id PK
        text event_hash UK
        int sensor_id FK
        int event_type_id FK
        int src_ip_id FK
        int dst_ip_id FK
        text event_time
        int src_port
        int dst_port
        text protocol
        text action
        int bytes
        int duration_ms
    }
    alerts {
        int alert_id PK
        text rule_code
        int source_ip_id FK
        int target_ip_id FK
        int dst_port
        text window_start
        text window_end
        int event_count
        int metric_count
        text severity
        text status
    }
    alert_events {
        int alert_id PK, FK
        int event_id PK, FK
    }
    import_rejections {
        int rejection_id PK
        text filename
        int line_number
        text reason
        text raw_row
    }
```

The seven tables include six related domain tables plus a standalone import audit table. The `alert_events` junction records exactly which event IDs support each alert. `alerts` uniqueness is `(rule_code, source_ip_id, target_ip_id, COALESCE(dst_port,-1), window_start, window_end)`.
