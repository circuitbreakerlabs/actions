import asyncio


async def main() -> None:
    """Entry point for the actions CLI."""
    print("Hello from actions!")


def cli() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    cli()
