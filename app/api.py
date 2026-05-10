from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import tempfile, os, time, shutil

from preprocessing import preprocess_image
from ocr_eng import extract_text
from extraction import extract_fields
from confidence import get_avg_confidence, field_confidence
from utils import save_json

app = FastAPI(
    title="Receipt Smart API",
    description="MLOps-powered OCR receipt data extraction",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/ui")
def frontend():
    return FileResponse("index.html")

REQUEST_COUNT   = Counter("receipt_requests_total", "Total API requests")
SUCCESS_COUNT   = Counter("receipt_success_total", "Successful extractions")
FAILURE_COUNT   = Counter("receipt_failure_total", "Failed extractions")
LATENCY         = Histogram("receipt_latency_seconds", "Processing time")
CONFIDENCE_HIST = Histogram("receipt_confidence_score", "OCR confidence scores",
                             buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0])

@app.get("/")
def root():
    return {"message": "Receipt Smart API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/process")
async def process_receipt(file: UploadFile = File(...)):
    REQUEST_COUNT.inc()
    start = time.time()

    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        FAILURE_COUNT.inc()
        raise HTTPException(status_code=400, detail="Only PNG/JPG supported.")

    suffix = os.path.splitext(file.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        processed = preprocess_image(tmp_path)
        results, text = extract_text(processed)
        extracted = extract_fields(text)
        ocr_conf = get_avg_confidence(results)

        output = {
            "store_name":   {"value": extracted["store_name"],
                             "confidence": field_confidence(extracted["store_name"], ocr_conf)},
            "date":         {"value": extracted["date"],
                             "confidence": field_confidence(extracted["date"], ocr_conf)},
            "items":        extracted["items"],
            "total_amount": {"value": extracted["total_amount"],
                             "confidence": field_confidence(extracted["total_amount"], ocr_conf)},
        }

        CONFIDENCE_HIST.observe(ocr_conf)
        LATENCY.observe(time.time() - start)
        SUCCESS_COUNT.inc()

        basename = os.path.splitext(file.filename)[0]
        save_json(output, basename + ".json")

        return JSONResponse(content={"status": "success",
                                     "filename": file.filename,
                                     "data": output})
    except Exception as e:
        FAILURE_COUNT.inc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)