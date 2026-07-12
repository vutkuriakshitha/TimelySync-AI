import logging

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import save_outcome_feedback, save_prediction
from app.ml import deadline_extractor, failure_predictor, impact_predictor, intake_predictor, ocr_reader, postanalysis_predictor
from app.ml.model_registry import is_ready, reload as reload_models
from app.schemas import (
    DeadlineExtractionResponse,
    DeadlineTextRequest,
    FailurePredictionResponse,
    ImpactPredictionResponse,
    IntakeRequest,
    IntakeResponse,
    OutcomeFeedback,
    PostAnalysisRequest,
    PostAnalysisResponse,
    TaskFeatures,
)
from app.security import verify_internal_api_key

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO),
                     format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger("ai-service")

app = FastAPI(
    title="TimelySync AI Microservice",
    description="Real trained machine-learning models for failure-risk prediction, "
                "impact simulation, post-completion root-cause analysis, and smart task intake.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    if is_ready():
        logger.info("All ML model artifacts loaded successfully.")
    else:
        logger.warning(
            "One or more model artifacts are missing. Run `python -m app.training.train_all` "
            "to train and save them before serving predictions."
        )


@app.get("/health")
def health():
    return {"status": "ok", "modelsReady": is_ready()}


@app.post("/admin/reload-models", dependencies=[Depends(verify_internal_api_key)])
def reload_models_endpoint():
    loaded = reload_models()
    return {"reloaded": loaded}


@app.post("/predict/failure", response_model=FailurePredictionResponse, dependencies=[Depends(verify_internal_api_key)])
def predict_failure(features: TaskFeatures):
    try:
        result = failure_predictor.predict(features)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    save_prediction("failure", features.model_dump(), result.model_dump())
    return result


@app.post("/predict/impact", response_model=ImpactPredictionResponse, dependencies=[Depends(verify_internal_api_key)])
def predict_impact(features: TaskFeatures):
    try:
        result = impact_predictor.predict(features)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    save_prediction("impact", features.model_dump(), result.model_dump())
    return result


@app.post("/predict/postanalysis", response_model=PostAnalysisResponse, dependencies=[Depends(verify_internal_api_key)])
def predict_postanalysis(features: PostAnalysisRequest):
    try:
        result = postanalysis_predictor.predict(features)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    save_prediction("postanalysis", features.model_dump(), result.model_dump())
    return result


@app.post("/predict/intake", response_model=IntakeResponse, dependencies=[Depends(verify_internal_api_key)])
def predict_intake(request: IntakeRequest):
    try:
        result = intake_predictor.predict(request.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    save_prediction("intake", request.model_dump(), result.model_dump())
    return result


@app.post(
    "/predict/deadline-extraction",
    response_model=DeadlineExtractionResponse,
    dependencies=[Depends(verify_internal_api_key)],
)
def predict_deadline_extraction(request: DeadlineTextRequest):
    try:
        result = deadline_extractor.extract_deadlines(request.text, request.documentName)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    save_prediction("deadline_extraction", request.model_dump(), result.model_dump())
    return result


@app.post(
    "/predict/document-deadlines",
    response_model=DeadlineExtractionResponse,
    dependencies=[Depends(verify_internal_api_key)],
)
async def predict_document_deadlines(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 15 MB.")

    try:
        ocr_result = ocr_reader.extract_text(file.filename or "document", file.content_type, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        result = deadline_extractor.extract_deadlines(ocr_result["text"], file.filename)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    payload = result.model_dump()
    payload["extractedText"] = ocr_result["text"][:20000]
    payload["extractionMethod"] = ocr_result["extractionMethod"]
    payload["characterCount"] = ocr_result["characterCount"]
    payload["estimatedPages"] = ocr_result["estimatedPages"]
    save_prediction("document_deadlines", {"filename": file.filename}, payload)
    return DeadlineExtractionResponse(**payload)


@app.post("/feedback/outcome", dependencies=[Depends(verify_internal_api_key)])
def feedback_outcome(feedback: OutcomeFeedback):
    save_outcome_feedback(feedback.model_dump())
    return {"status": "recorded"}
