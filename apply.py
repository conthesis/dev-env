#!/usr/bin/env python
import sys
import yaml
import json
import asyncio
from nats.aio.client import Client as NATS

nc = NATS()

async def store_ent(entity: str, data):
    payload = entity.encode("utf-8") + b"\n" + json.dumps(data).encode("utf-8")
    res = await nc.request("conthesis.cfs.put", payload)

async def main():
    if len(sys.argv) != 3:
        print("usage: apply.py entity filename")

    await nc.connect("nats://localhost:4222", loop=asyncio.get_running_loop())
    print(sys.argv)
    data = yaml.load(open(sys.argv[2]))
    await store_ent(sys.argv[1].strip(), data)
    await nc.drain()

asyncio.run(main())
