import asyncio, os
from nats.aio.client import Client as NATS
SUBJECT = os.getenv("ETL_SUBJECT", "etl.jobs")
async def main():
    nc = NATS(); await nc.connect(os.getenv("NATS_URL","nats://nats:4222"))
    print("ETL worker connected to NATS.")
    async def handler(msg):
        print("Received job:", msg.data.decode()); await asyncio.sleep(0.1)
    await nc.subscribe(SUBJECT, cb=handler)
    print(f"Listening on '{SUBJECT}'"); 
    while True: await asyncio.sleep(1)
if __name__ == "__main__": asyncio.run(main())
