#!/usr/bin/env python3
import csv
import io
import json
import urllib.request
import zipfile
from datetime import datetime, timezone

STOP_ID = "81844"
GTFS_URL = "https://romamobilita.it/sites/default/files/rome_static_gtfs.zip"
OUTPUT = "gtfs_trip_map.json"

def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": "bus-dashboard/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()

def read_csv(zf, name):
    with zf.open(name) as raw:
        text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        yield from csv.DictReader(text)

def main():
    data = download(GTFS_URL)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        trip_ids = set()
        for row in read_csv(zf, "stop_times.txt"):
            if row.get("stop_id", "").strip() == STOP_ID:
                tid = row.get("trip_id", "").strip()
                if tid:
                    trip_ids.add(tid)

        trip_to_route = {}
        route_ids = set()
        for row in read_csv(zf, "trips.txt"):
            tid = row.get("trip_id", "").strip()
            if tid in trip_ids:
                rid = row.get("route_id", "").strip()
                if rid:
                    trip_to_route[tid] = rid
                    route_ids.add(rid)

        route_to_short = {}
        for row in read_csv(zf, "routes.txt"):
            rid = row.get("route_id", "").strip()
            if rid in route_ids:
                short = row.get("route_short_name", "").strip() or rid
                route_to_short[rid] = short

    trips = {}
    for tid, rid in trip_to_route.items():
        short = route_to_short.get(rid)
        if short:
            trips[tid] = short

    payload = {
        "stop_id": STOP_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trip_count": len(trips),
        "trips": dict(sorted(trips.items()))
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")

    print("stop", STOP_ID, "trip_ids", len(trip_ids), "mapped", len(trips))

if __name__ == "__main__":
    main()
