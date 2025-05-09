# app/routers/shipment.py

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pymongo import DESCENDING

from core.database import shipments_collection
from core.auth import get_required_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/create-shipment", response_class=HTMLResponse)
async def get_create_shipment_form(request: Request):
    last_shipment = shipments_collection.find_one(sort=[("shipment_number", DESCENDING)])
    if last_shipment and "shipment_number" in last_shipment:
        last_id = last_shipment["shipment_number"]
        num_part = int(last_id.replace("exfscm", ""))
        new_id = f"exfscm{num_part+1:02}"
    else:
        new_id = "exfscm01"

    success_message = request.query_params.get("success")
    return templates.TemplateResponse("create_shipment.html", {
        "request": request,
        "shipment_id": new_id,
        "success": success_message
    })


@router.post("/create-shipment")
async def create_shipment(
    shipmentNumber: str = Form(...),
    route: str = Form(...),
    device: str = Form(...),
    poNumber: str = Form(...),
    ndcNumber: str = Form(...),
    serialNumber: str = Form(...),
    goodsType: str = Form(...),
    deliveryDate: str = Form(...),
    deliveryNumber: str = Form(...),
    batchId: str = Form(...),
    shipmentDesc: str = Form(...)
):
    shipment_data = {
        "shipment_number": shipmentNumber,
        "route": route,
        "device": device,
        "po_number": poNumber,
        "ndc_number": ndcNumber,
        "serial_number": serialNumber,
        "goods_type": goodsType,
        "expected_delivery_date": deliveryDate,
        "delivery_number": deliveryNumber,
        "batch_id": batchId,
        "shipment_description": shipmentDesc,
        "created_at": datetime.utcnow()
    }
    shipments_collection.insert_one(shipment_data)
    return RedirectResponse(url="/create-shipment?success=Shipment%20created%20successfully", status_code=303)
