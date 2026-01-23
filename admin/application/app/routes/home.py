import json
from json import JSONDecodeError

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi import Request, File, UploadFile
from starlette.responses import JSONResponse, FileResponse, Response
from collections.abc import MutableMapping
import csv
import io
from ..config_models.database import db_config
from datetime import datetime
from ..models.user import User
from pymongo import AsyncMongoClient
from beanie.operators import In

templates = Jinja2Templates(directory="src/templates")

route = APIRouter()

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, str(v)))
        else:
            items.append((new_key, v))
    return dict(items)

def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime(item) for item in obj]
    return obj

async def get_json():
    documents = await db_config.get_all()

    for doc in documents:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])

    converted = convert_datetime(documents)
    return json.dumps(converted, indent=4)

async def get_csv():
    documents = await db_config.get_all()

    flattened = [flatten_dict(doc) for doc in documents]

    for doc in flattened:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])

    output = io.StringIO()
    if flattened:
        all_keys = set()
        for doc in flattened:
            all_keys.update(doc.keys())
        writer = csv.DictWriter(output, fieldnames=sorted(all_keys))
        writer.writeheader()
        writer.writerows(flattened)

    return output.getvalue()

async def get_aggregation():
    documents = await db_config.get_aggregation()
    for doc in documents:
        doc['_id'] = str(doc['_id'])

    return json.dumps(documents, indent=4)

async def verify_csv(file: bytes):
    file_data = io.StringIO(file.decode('utf-8'))

    data = csv.DictReader(file_data, lineterminator='\n', quotechar='"', delimiter=',')
    data_list = []
    for line in data:
        print(line)
        athena_id = line.get("athenaId", None)
        if athena_id is not None:
            data_list.append(athena_id)
        else:
            return False

    return data_list


async def verify_json(file: bytes):
    try:
        data = json.loads(file)
    except JSONDecodeError:
        return False

    data_list = []

    for entry in data:
        athena_id = entry.get("athenaId", None)
        if athena_id is not None:
            data_list.append(athena_id)
        else:
            return False
    return data_list

@route.get('/')
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@route.post('/upload')
async def upload(request: Request, file: UploadFile = File(...)):
    file_data = await file.read()
    print("Read the file")
    if file.filename.endswith('.csv'):
        data = await verify_csv(file_data)
    elif file.filename.endswith('.json'):
        data = await verify_json(file_data)
    else:
        return JSONResponse({"error": "Invalid filetype"}, status_code=400)
    print(data)
    if data:
        await User.insert_users(data)
    else:
        return JSONResponse({"error": "Invalid Data"}, status_code=400)

    return JSONResponse({"success": True}, status_code=200)


@route.get('/download')
async def download(request: Request):
    params = request.query_params

    data_type = params.get("type", None)

    if data_type == "csv":
        data = await get_csv()
    elif data_type == "json":
        data = await get_json()
    elif data_type == "aggregation":
        data = await get_aggregation()

    else:
        return JSONResponse({"error": "Invalid filetype"}, status_code=400)

    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=download.{data_type}"}
    )
