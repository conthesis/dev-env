#!/usr/bin/env python
import sys
import yaml
import json
import asyncio
from nats.aio.client import Client as NATS

nc = NATS()

async def cas_store(data):
    if isinstance(data, dict):
        data = json.dumps(data).encode("utf-8")
    res = await nc.request("conthesis.cas.store", data, timeout=3)
    if res.data is None or len(res.data) == 0:
        return None
    return res.data


async def insert_vsn(entity: str, pointer: bytes):
    data = entity.encode("utf-8") + b"\n" + pointer
    res = await nc.request("conthesis.dcollect.store", data, timeout=3)
    if res.data == b"ERR":
        raise RuntimeError("dcollect.store failed")
    return res.data


async def store_ent(entity: str, data):
    ptr = await cas_store(data)
    return await insert_vsn(entity, ptr)

async def main():
    if len(sys.argv) != 3:
        print("usage: apply.py entity filename")

    await nc.connect("nats://localhost:4222", loop=asyncio.get_running_loop())
    print(sys.argv)
    data = yaml.load(open(sys.argv[2]))
    await store_ent(sys.argv[1].strip(), data)
    await nc.drain()

asyncio.run(main())
