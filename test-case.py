#!/usr/bin/env python3
import asyncio
import json
import httpx

http = httpx.AsyncClient()

async def cas_store(data):
    if isinstance(data, dict):
        data = json.dumps(data)
    resp = await http.post("http://cas.tspnhq.com/store", data=data)
    resp.raise_for_status()
    return await resp.aread()

async def insert_vsn(entity: str, pointer: bytes):
    resp = await http.post("http://dcollect.tspnhq.com/entity-ptr/{entity}", data=pointer)
    resp.raise_for_status()
    return resp.json()

async def store_ent(entity: str, data):
    ptr = await cas_store(data)
    return await insert_vsn(entity, ptr)

async def store_ents(ents):
    asyncio.gather([store_ents(ent, val) for (ent, val) in ents])


async def subscribe(name, trigger_url, entities):
    resp = await http.post("http://entwatcher.tspnhq.com/v1/subscribe/{name}", json=dict(trigger_url=trigger_url, entities=entities))
    resp.raise_for_status()
    return resp



async def main():
    await store_ents([
        ("foo", { "foo": 1}),
        ("bar", { "bar": 1}),
        ("template", {"name":"foo","entries":[{"name":"step1","inputs":["a"],"command":{"kind":"identity"}}]}),
    ])

    await subscribe("my_dag", "TriggerDAG", {
        "$Template": "template",
        "foo": "foo",
        "bar": "bar",
    })

    await store_ents([
        ("foo", {"foo": 2}),
        ("bar", {"bar": 2}),
    ])
