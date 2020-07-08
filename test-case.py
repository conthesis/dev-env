#!/usr/bin/env python3
import asyncio
import json

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


async def store_ents(ents):
    await asyncio.gather(*[store_ent(ent, val) for (ent, val) in ents])


async def main():
    await nc.connect("nats://localhost:4222", loop=asyncio.get_running_loop())
    await store_ents(
        [
            ("foo", {"foo": 1}),
            ("bar", {"bar": 1}),
            (
                "template",
                {
                    "name": "foo",
                    "entries": [
                        {"name": "step1", "inputs": ["a"], "action": "identity"}
                    ],
                },
            ),
            (
                "_conthesis.watcher.my_dag_watcher",
                {
                    "kind": "TriggerDAG",
                    "properties": [
                        {"name": "$Template", "kind": "ENTITY", "value": "template",},
                        {"name": "foo", "kind": "ENTITY", "value": "foo",},
                        {"name": "bar", "kind": "ENTITY", "value": "bar",},
                    ],
                },
            ),
        ]
    )
    await store_ents(
        [("foo", {"foo": 2}), ("bar", {"bar": 2}),]
    )

if __name__ == "__main__":
    asyncio.run(main())
