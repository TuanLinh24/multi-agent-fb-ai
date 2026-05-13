import asyncio

from training.router_dataset_builder import generate_dataset


if __name__ == "__main__":
    asyncio.run(generate_dataset())
