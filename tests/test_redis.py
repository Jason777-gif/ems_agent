import asyncio
import redis.asyncio as aioredis


async def test_redis():
    # 尝试不同的 URL 格式
    urls = [
        "redis://:025@SMts@113.44.214.114:6379/4",
        "redis://default:025%40SMts@113.44.214.114:6379/4",
        "redis://113.44.214.114:6379/4",  # 无密码
    ]

    for url in urls:
        print(f"\nTesting: {url}")
        try:
            redis_client = aioredis.from_url(url, encoding="utf-8", decode_responses=True)
            await redis_client.ping()
            print(f"✓ Success!")
            await redis_client.close()
            return url
        except Exception as e:
            print(f"✗ Failed: {e}")

    return None


if __name__ == "__main__":
    result = asyncio.run(test_redis())
    if result:
        print(f"\nWorking URL: {result}")
    else:
        print("\nNo working URL found. Please check Redis server and credentials.")
