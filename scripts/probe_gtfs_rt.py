#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime, timezone
from google.transit import gtfs_realtime_pb2

STOP_ID = "81844"
URL = "https://romamobilita.it/sites/default/files/rome_rtgtfs_trip_updates_feed.pb"
OUT = "rt_probe.json"

req = urllib.request.Request(URL, headers={"User-Agent": "bus-dashboard/1.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    data = r.read()

feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(data)

exact = []
contains = []
all_stop_ids = {}
entities = 0
trip_updates = 0
with_route_id = 0
with_trip_id = 0

for ent in feed.entity:
    entities += 1
    if not ent.HasField("trip_update"):
        continue
    trip_updates += 1
    tu = ent.trip_update
    td = tu.trip

    trip_id = td.trip_id if td.HasField("trip_id") else ""
    route_id = td.route_id if td.HasField("route_id") else ""

    if trip_id:
        with_trip_id += 1
    if route_id:
        with_route_id += 1

    for stu in tu.stop_time_update:
        sid = stu.stop_id
        if not sid:
            continue

        all_stop_ids[sid] = all_stop_ids.get(sid, 0) + 1

        arrival = None
        departure = None
        if stu.HasField("arrival") and stu.arrival.HasField("time"):
            arrival = int(stu.arrival.time)
        if stu.HasField("departure") and stu.departure.HasField("time"):
            departure = int(stu.departure.time)

        row = {
            "entity_id": ent.id,
            "trip_id": trip_id,
            "route_id": route_id,
            "stop_id": sid,
            "stop_sequence": int(stu.stop_sequence) if stu.HasField("stop_sequence") else None,
            "arrival": arrival,
            "departure": departure,
        }

        if sid == STOP_ID:
            exact.append(row)
        if STOP_ID in sid and sid != STOP_ID:
            contains.append(row)

prefixes = sorted(
    [{"stop_id": sid, "count": n} for sid, n in all_stop_ids.items()
     if sid.startswith("8184") or "Conca" in sid],
    key=lambda x: x["stop_id"]
)

payload = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "feed_header_timestamp": int(feed.header.timestamp) if feed.header.HasField("timestamp") else None,
    "bytes": len(data),
    "entities": entities,
    "trip_updates": trip_updates,
    "trip_updates_with_trip_id": with_trip_id,
    "trip_updates_with_route_id": with_route_id,
    "exact_stop_81844_count": len(exact),
    "contains_81844_count": len(contains),
    "exact_stop_81844": exact[:100],
    "contains_81844": contains[:100],
    "nearby_stop_ids_8184x": prefixes[:200],
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(json.dumps({
    "trip_updates": trip_updates,
    "with_route_id": with_route_id,
    "exact_81844": len(exact),
    "contains_81844": len(contains),
    "bytes": len(data)
}))
