from typing import Optional

from pydantic import BaseModel, Field


class TaskFeatures(BaseModel):
    hoursUntilDue: float = 72
    priority: str = "MEDIUM"
    category: str = "PERSONAL_GOAL"
    impact: str = "MEDIUM"
    effort: str = "MEDIUM"
    userCompletionRate: float = 0.7
    userOnTimeRate: float = 0.6
    riskScoreAtCreation: float = 0
    taskId: Optional[str] = None
    userId: Optional[str] = None


class OutcomeFeedback(TaskFeatures):
    completedOnTime: bool
    daysLate: float = 0


class PostAnalysisRequest(TaskFeatures):
    completedOnTime: bool
    daysLate: float = 0


class IntakeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50000)


class DeadlineTextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500000)
    documentName: Optional[str] = None


class DeadlineRecord(BaseModel):
    deadlineType: str
    date: Optional[str] = None
    dateOriginal: Optional[str] = None
    confidence: str
    confidenceScore: float = 0.0
    originalSentence: str = ""
    contextBefore: str = ""
    contextAfter: str = ""
    sectionHeading: Optional[str] = None
    pageNumber: Optional[int] = None
    needsReferenceDate: bool = False
    explanation: Optional[str] = None


class DateRangeRecord(BaseModel):
    startDate: str
    endDate: str
    startDateOriginal: str = ""
    endDateOriginal: str = ""
    purpose: str
    confidence: str
    originalSentence: str = ""
    contextBefore: str = ""
    contextAfter: str = ""
    sectionHeading: Optional[str] = None
    pageNumber: Optional[int] = None


class DeadlineExtractionResponse(BaseModel):
    deadlines: list[DeadlineRecord]
    dateRanges: list[DateRangeRecord]
    summary: str
    totalDeadlines: int
    totalDateRanges: int
    modelVersion: str
    extractedText: Optional[str] = None
    extractionMethod: Optional[str] = None
    characterCount: Optional[int] = None
    estimatedPages: Optional[int] = None


class ConsequenceOut(BaseModel):
    description: str
    probabilityPercent: int


class CauseOut(BaseModel):
    type: str
    percentage: int
    description: str


class FailurePredictionResponse(BaseModel):
    probability: int
    riskLevel: str
    riskFactors: list[str]
    modelVersion: str


class ImpactPredictionResponse(BaseModel):
    severityLevel: str
    consequences: list[ConsequenceOut]
    modelVersion: str


class PostAnalysisResponse(BaseModel):
    causes: list[CauseOut]
    recommendation: str
    modelVersion: str


class IntakeResponse(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    dueDate: Optional[str] = None
    modelVersion: str
