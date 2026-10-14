import asyncio

from app.services.openalex import search_works


async def main():
    print("Starting OpenAlex test...", flush=True)

    print("Sending request to OpenAlex...", flush=True)

    results = await search_works("transformers", per_page=3)

    print("Response received!", flush=True)

    print("Total results:", results["meta"]["count"], flush=True)

    for work in results["results"]:
        print("\nTitle:", work.get("title"), flush=True)
        print("Year:", work.get("publication_year"), flush=True)
        print("OpenAlex ID:", work.get("id"), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
    
        

