#!/usr/bin/env python3
import urllib.request, json, base64, subprocess, textwrap, os, sys

URL="https://romamobilita.it/sites/default/files/rome_rtgtfs_trip_updates_feed.pb"
req=urllib.request.Request(URL, headers={"User-Agent":"bus-dashboard/1.0","Origin":"https://marcocaponigro.github.io"})
with urllib.request.urlopen(req, timeout=30) as r:
    data=r.read()
    headers={k.lower():v for k,v in r.headers.items()}
open("current_trip_updates.pb","wb").write(data)

result={
  "bytes":len(data),
  "access_control_allow_origin":headers.get("access-control-allow-origin"),
  "content_type":headers.get("content-type"),
  "cache_control":headers.get("cache-control")
}
open("rt_headers.json","w").write(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
