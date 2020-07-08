#!/usr/bin/env python
import asyncio
from jsonlines import Reader
import json
import os
import lzma
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

def get_all():
    with Reader(lzma.open("./enron.json.xz")) as reader:
        yield from reader

async def main():
    bfr = []
    await nc.connect("nats://localhost:4222", loop=asyncio.get_running_loop())
    for l in get_all():
        msg_id = l["messageId"].replace(".", "_")
        bfr.append(asyncio.create_task(store_ent(f"sample-enron.email.{msg_id}", l)))
        if len(bfr) > 100:
            old_bfr = bfr
            await asyncio.wait(old_bfr)
            bfr = []
    await asyncio.wait(bfr)


if __name__ == "__main__":
    asyncio.run(main())
