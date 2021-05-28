import asyncio
import csv
import mimetypes
import os
from pathlib import Path

import aioboto3
import aiofiles
import pandas as pd
from aiohttp import ClientSession
from slugify import slugify

AWS_S3_CUSTOM_DOMAIN = "https://flyline-api-backend-storages.s3-us-west-1.amazonaws.com"
BASE_FILE_STORE_DIR = os.path.join(Path(__file__).parent.resolve(), "images")


def get_extension(url):
    dot_index = url.rfind(".")
    return url[dot_index + 1 :]


def get_s3_object_base_name(row, suffix=""):
    airline_code = row["airline_code"]
    aircraft_description = row["aircraft_description"]
    airline_name = row["airline_name"]
    s3_base_path = f"media/seatmaps/{slugify(airline_name)}({airline_code})/{slugify(aircraft_description)}"
    if suffix:
        s3_base_path = f"{s3_base_path}/{suffix}"
    return s3_base_path


async def upload_image(i, file_path, s3_client, s3_uri, bucket="flyline-api-backend-storages"):
    try:
        await asyncio.sleep(i)
        async with aiofiles.open(file_path, mode="rb") as f:
            content = await f.read()
            await s3_client.upload_fileobj(
                content,
                bucket,
                s3_uri,
                ExtraArgs={"ACL": "public-read", "ContentType": mimetypes.guess_type(file_path)},
            )
    except Exception as e:
        return f"Error occurred while uploading {file_path}: {e}"


async def upload_images():
    async with aioboto3.client("s3") as s3:
        tasks = (
            upload_image(i, file_path, s3, s3_seat_map_uri)
            for i, (file_path, s3_seat_map_uri) in enumerate(images_link_generator())
        )
        await asyncio.gather(*tasks, return_exceptions=True)


def images_link_generator():
    csv_path = "cleaned.csv"
    df = pd.read_csv(csv_path, sep=";", keep_default_na=False)

    for _, row in df.iterrows():
        extension = get_extension(row["seat_map"])
        s3_base_url = get_s3_object_base_name(row)
        s3_seat_map_uri = f"{s3_base_url}/seatmap.{extension}"
        file_name = s3_seat_map_uri.replace("/", "_")
        file_path = os.path.join(BASE_FILE_STORE_DIR, file_name)
        yield file_path, s3_seat_map_uri


async def download_image(i, session, file_path, s3_uri):
    try:
        await asyncio.sleep(i // 10)
        s3_link = f"{AWS_S3_CUSTOM_DOMAIN}/{s3_uri}"
        async with session.get(s3_link) as r:
            content = await r.read()
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

    except Exception as e:
        s3_link = f"Error occurred while downloading {s3_link}: {e}"
    return file_path, s3_link


async def download_images():
    async with ClientSession() as session:
        tasks = (
            download_image(i, session, file_path, s3_seat_map_uri)
            for i, (file_path, s3_seat_map_uri) in enumerate(images_link_generator())
        )
        return await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    with open("file_mapping.csv", "w") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["file_path", "link_url"])
        for file_path, s3_seat_map_uri in images_link_generator():
            s3_link = f"{AWS_S3_CUSTOM_DOMAIN}/{s3_seat_map_uri}"
            csvwriter.writerow([file_path, s3_link])

    with open("success_download.csv", "w") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["file_path", "link_url"])
        res = asyncio.run(download_images())
        for file_path, s3_link in res:
            csvwriter.writerow([file_path, s3_link])

        # print(asyncio.run(upload_images()))
