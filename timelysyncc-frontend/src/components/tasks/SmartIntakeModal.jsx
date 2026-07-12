// src/components/tasks/SmartIntakeModal.jsx
import React, { useRef, useState } from "react";
import {
  Modal,
  Form,
  Button,
  Alert,
  Spinner,
  Badge,
  Nav,
  Table,
} from "react-bootstrap";
import { Sparkles, Upload, FileText } from "lucide-react";
import aiService from "../../services/aiService";

const CATEGORY_LABELS = {
  ACADEMIC: "Academic",
  OPPORTUNITY: "Opportunity",
  PERSONAL_GOAL: "Personal Goal",
  EVENT: "Event",
};

const confidenceVariant = (level) => {
  if (level === "High") return "success";
  if (level === "Medium") return "warning";
  return "secondary";
};

const SmartIntakeModal = ({ show, onHide, onApply }) => {
  const fileInputRef = useRef(null);
  const [mode, setMode] = useState("text");
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [intakeResult, setIntakeResult] = useState(null);
  const [deadlineResult, setDeadlineResult] = useState(null);

  const resetState = () => {
    setText("");
    setFile(null);
    setError("");
    setIntakeResult(null);
    setDeadlineResult(null);
    setMode("text");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleClose = () => {
    resetState();
    onHide();
  };

  const handleAnalyzeText = async () => {
    if (!text.trim()) {
      setError("Please paste OCR text or a notice excerpt first.");
      return;
    }
    setError("");
    setLoading(true);
    setIntakeResult(null);
    setDeadlineResult(null);
    try {
      const [intakeResp, deadlineResp] = await Promise.all([
        aiService.smartIntake(text.trim()),
        aiService.extractDeadlines(text.trim()),
      ]);
      setIntakeResult(intakeResp.data);
      setDeadlineResult(deadlineResp.data);
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "Could not analyze this text right now. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeDocument = async () => {
    if (!file) {
      setError("Please choose a PDF or image to upload.");
      return;
    }
    setError("");
    setLoading(true);
    setIntakeResult(null);
    setDeadlineResult(null);
    try {
      const deadlineResp = await aiService.extractDocumentDeadlines(file);
      setDeadlineResult(deadlineResp.data);
      const extracted = deadlineResp.data?.extractedText || "";
      if (extracted.trim()) {
        const intakeResp = await aiService.smartIntake(extracted.slice(0, 50000));
        setIntakeResult(intakeResp.data);
      }
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "Could not process this document. Use a readable PDF or scanned image.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleApplyIntake = () => {
    if (!intakeResult) return;
    onApply({
      title: intakeResult.title,
      description: intakeResult.description,
      category: intakeResult.category,
      priority: intakeResult.priority,
      dueDate: intakeResult.dueDate,
    });
    handleClose();
  };

  const handleApplyDeadline = (deadline) => {
    if (!deadline?.date) return;
    const [day, month, year] = deadline.date.split("-");
    const isoDue = `${year}-${month}-${day}T23:59:00`;
    onApply({
      title: `${deadline.deadlineType}${deadline.sectionHeading ? ` – ${deadline.sectionHeading}` : ""}`,
      description: deadline.originalSentence,
      category: mapDeadlineToCategory(deadline.deadlineType),
      priority: deadline.confidence === "High" ? "HIGH" : "MEDIUM",
      dueDate: isoDue,
    });
    handleClose();
  };

  const mapDeadlineToCategory = (type) => {
    const t = (type || "").toLowerCase();
    if (t.includes("exam") || t.includes("submission") || t.includes("verification")) {
      return "ACADEMIC";
    }
    if (
      t.includes("apply") ||
      t.includes("tender") ||
      t.includes("bid") ||
      t.includes("registration")
    ) {
      return "OPPORTUNITY";
    }
    if (t.includes("event") || t.includes("meeting") || t.includes("hearing")) {
      return "EVENT";
    }
    return "PERSONAL_GOAL";
  };

  const hasResults = intakeResult || deadlineResult;

  return (
    <Modal show={show} onHide={handleClose} centered size="lg" scrollable>
      <Modal.Header closeButton>
        <Modal.Title className="d-flex align-items-center gap-2">
          <Sparkles size={20} className="text-primary" /> Smart Intake – OCR Deadline Extraction
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p className="text-muted small">
          Paste OCR text or upload a PDF/image notice. Our ML models extract every
          important date, classify its purpose, detect ranges, and suggest a task.
        </p>

        {error && <Alert variant="danger">{error}</Alert>}

        <Nav variant="tabs" className="mb-3">
          <Nav.Item>
            <Nav.Link active={mode === "text"} onClick={() => setMode("text")}>
              <FileText size={14} className="me-1" /> Paste OCR Text
            </Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link active={mode === "document"} onClick={() => setMode("document")}>
              <Upload size={14} className="me-1" /> Upload Document
            </Nav.Link>
          </Nav.Item>
        </Nav>

        {!hasResults && (
          <>
            {mode === "text" ? (
              <Form.Group className="mb-3">
                <Form.Control
                  as="textarea"
                  rows={6}
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste OCR text from a circular, tender, university notice, or official letter..."
                />
              </Form.Group>
            ) : (
              <Form.Group className="mb-3">
                <Form.Control
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.webp,.tif,.tiff"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
                <Form.Text className="text-muted">
                  PDF (text or scanned) and images supported. Max 15 MB.
                </Form.Text>
              </Form.Group>
            )}

            <Button
              variant="primary"
              className="w-100"
              onClick={mode === "text" ? handleAnalyzeText : handleAnalyzeDocument}
              disabled={loading}
            >
              {loading ? (
                <>
                  <Spinner size="sm" animation="border" className="me-2" />
                  Analyzing document...
                </>
              ) : (
                <>
                  <Sparkles size={16} className="me-2" />
                  Extract Deadlines with AI
                </>
              )}
            </Button>
          </>
        )}

        {deadlineResult && (
          <div className="mt-3">
            <Alert variant="info" className="small py-2">
              {deadlineResult.summary}
              {deadlineResult.extractionMethod && (
                <span className="d-block text-muted mt-1">
                  Extraction: {deadlineResult.extractionMethod}
                  {deadlineResult.characterCount
                    ? ` · ${deadlineResult.characterCount} characters`
                    : ""}
                </span>
              )}
            </Alert>

            {deadlineResult.dateRanges?.length > 0 && (
              <>
                <h6 className="fw-semibold mt-3">Date Ranges</h6>
                <Table responsive size="sm" bordered className="mb-3">
                  <thead>
                    <tr>
                      <th>Purpose</th>
                      <th>Start</th>
                      <th>End</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {deadlineResult.dateRanges.map((range, idx) => (
                      <tr key={`range-${idx}`}>
                        <td>{range.purpose}</td>
                        <td>{range.startDate}</td>
                        <td>{range.endDate}</td>
                        <td>
                          <Badge bg={confidenceVariant(range.confidence)}>{range.confidence}</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </>
            )}

            {deadlineResult.deadlines?.length > 0 ? (
              <>
                <h6 className="fw-semibold">Extracted Deadlines</h6>
                <div style={{ maxHeight: "280px", overflowY: "auto" }}>
                  <Table responsive size="sm" bordered>
                    <thead className="table-light sticky-top">
                      <tr>
                        <th>Type</th>
                        <th>Date</th>
                        <th>Confidence</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {deadlineResult.deadlines.map((deadline, idx) => (
                        <tr key={`deadline-${idx}`}>
                          <td>
                            <div className="fw-semibold small">{deadline.deadlineType}</div>
                            {deadline.needsReferenceDate && (
                              <Badge bg="warning" className="mt-1">
                                Needs reference date
                              </Badge>
                            )}
                            <div className="text-muted small mt-1">
                              {deadline.originalSentence?.slice(0, 120)}
                              {deadline.originalSentence?.length > 120 ? "…" : ""}
                            </div>
                          </td>
                          <td className="text-nowrap">
                            {deadline.date || "—"}
                            {deadline.dateOriginal && (
                              <div className="text-muted small">({deadline.dateOriginal})</div>
                            )}
                          </td>
                          <td>
                            <Badge bg={confidenceVariant(deadline.confidence)}>
                              {deadline.confidence}
                            </Badge>
                          </td>
                          <td>
                            {deadline.date && (
                              <Button
                                size="sm"
                                variant="outline-success"
                                onClick={() => handleApplyDeadline(deadline)}
                              >
                                Create Task
                              </Button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </>
            ) : (
              !deadlineResult.dateRanges?.length && (
                <p className="text-muted small mb-0">No actionable deadlines were found.</p>
              )
            )}
          </div>
        )}

        {intakeResult && (
          <div className="border rounded p-3 bg-light mt-3">
            <h6 className="fw-semibold mb-2">Suggested Primary Task</h6>
            <p className="mb-2">
              <strong>Title:</strong> {intakeResult.title}
            </p>
            <p className="mb-2">
              <Badge bg="info" className="me-2">
                {CATEGORY_LABELS[intakeResult.category] || intakeResult.category}
              </Badge>
              <Badge
                bg={
                  intakeResult.priority === "HIGH"
                    ? "danger"
                    : intakeResult.priority === "MEDIUM"
                      ? "warning"
                      : "success"
                }
              >
                {intakeResult.priority} priority
              </Badge>
            </p>
            {intakeResult.dueDate && (
              <p className="mb-0 small text-muted">
                Detected due date: {new Date(intakeResult.dueDate).toLocaleString()}
              </p>
            )}
            <div className="d-flex gap-2 mt-3">
              <Button variant="outline-secondary" size="sm" onClick={resetState}>
                Analyze Another
              </Button>
              <Button variant="success" size="sm" onClick={handleApplyIntake}>
                Use Primary Suggestion
              </Button>
            </div>
          </div>
        )}

        {hasResults && !intakeResult && (
          <div className="d-flex gap-2 mt-3">
            <Button variant="outline-secondary" size="sm" onClick={resetState}>
              Analyze Another
            </Button>
          </div>
        )}
      </Modal.Body>
    </Modal>
  );
};

export default SmartIntakeModal;
