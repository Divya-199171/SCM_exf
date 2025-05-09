from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
from fastapi import Form
from fastapi.responses import RedirectResponse


# Load .env variables
load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# MongoDB connection using MONGO_URI from .env
client = MongoClient(os.getenv("MONGO_URI"))
db = client['projectfast']
shipments_collection = db['shipments']

@router.get("/allshipment")
async def allshipments(request: Request):
    shipments = list(shipments_collection.find())

    for shipment in shipments:
        shipment['_id'] = str(shipment['_id'])


    return templates.TemplateResponse("allshipments.html", {
        "request": request,
        "shipments": shipments
    })

@router.get("/editshipment/{shipment_id}")
async def edit_shipment_form(request: Request, shipment_id: str):
    shipment = shipments_collection.find_one({"_id": ObjectId(shipment_id)})
    if shipment:
        shipment['_id'] = str(shipment['_id'])
        return templates.TemplateResponse("editshipment.html", {"request": request, "shipment": shipment})
    else:
        raise HTTPException(status_code=404, detail="Shipment not found")


# Handle form submission
@router.post("/editshipment/{shipment_id}")
async def update_shipment(
    shipment_id: str,
    shipment_number: str = Form(...),
    route: str = Form(...),
    device: str = Form(...),
    po_number: str = Form(...),
    ndc_number: str = Form(...),
    serial_number: str = Form(...),
    goods_type: str = Form(...),
    expected_delivery_date: str = Form(...),
    delivery_number: str = Form(...),
    batch_id: str = Form(...),
    shipment_description: str = Form(...)
):
    result = shipments_collection.update_one(
        {"_id": ObjectId(shipment_id)},
        {"$set": {
            "shipment_number": shipment_number,
            "route": route,
            "device": device,
            "po_number": po_number,
            "ndc_number": ndc_number,
            "serial_number": serial_number,
            "goods_type": goods_type,
            "expected_delivery_date": expected_delivery_date,
            "delivery_number": delivery_number,
            "batch_id": batch_id,
            "shipment_description": shipment_description
        }}
    )
    return RedirectResponse(url="/allshipment", status_code=303)


# Delete route
@router.post("/deleteshipments")
async def delete_selected_shipments(request: Request):
    form_data = await request.form()
    selected_ids = form_data.getlist("selected_shipments")
    
    if selected_ids:
        for sid in selected_ids:
            # Delete from DB
            shipments_collection.delete_one({"_id": ObjectId(sid)})
    return RedirectResponse("/allshipment", status_code=303)