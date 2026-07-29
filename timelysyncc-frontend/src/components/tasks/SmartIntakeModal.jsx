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

const mapDeadlineToCategory = (type) => {
  const t = (type || "").toLowerCase();
  if (
    t.includes("exam") ||
    t.includes("submission") ||
    t.includes("verification") ||
    t.includes("registration") ||
    t.includes("fee") ||
    t.includes("admit") ||
    t.includes("project") ||
    t.includes("viva") ||
    t.includes("thesis") ||
    t.includes("assignment") ||
    t.includes("approval") ||
    t.includes("review")
  ) {
    return "ACADEMIC";
  }
  if (
    t.includes("apply") ||
    t.includes("tender") ||
    t.includes("bid") ||
    t.includes("internship") ||
    t.includes("placement")
  ) {
    return "OPPORTUNITY";
  }
  if (
    t.includes("event") ||
    t.includes("meeting") ||
    t.includes("hearing") ||
    t.includes("seminar") ||
    t.includes("workshop")
  ) {
    return "EVENT";
  }
  return "PERSONAL_GOAL";
};

const toApplyPayload = (suggested) => {
  const fineNote = suggested.lateFee || suggested.fineAmount;
  return {
    title: suggested.title,
    description: fineNote
      ? `${suggested.description || ""}${suggested.description ? " " : ""}Late fee/fine: ${fineNote}`.trim()
      : suggested.description,
    category: suggested.category || mapDeadlineToCategory(suggested.sourceDeadlineType),
    priority: suggested.priority || "MEDIUM",
    dueDate: suggested.dueDate ? `${suggested.dueDate}T23:59:00` : null,
    dueDateDisplay: suggested.dueDateDisplay,
  };
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

  const actionableSuggestedTasks = () =>
    (deadlineResult?.suggestedTasks || []).filter((t) => t.title && t.dueDate);

  const suggestedTaskFromDeadlines = (deadlineData) => {
    const suggested =
      deadlineData?.suggestedTasks?.find((t) => t.dueDate) ||
      deadlineData?.suggestedTasks?.[0];
    if (suggested) {
      return toApplyPayload(suggested);
    }
    const actionable = (deadlineData?.deadlines || []).find(
      (d) =>
        d.date &&
        d.isActionable !== false &&
        d.deadlineType &&
        d.deadlineType !== "Document Date" &&
        d.deadlineType !== "Registration Closed",
    );
    if (!actionable) return null;
    const iso =
      actionable.dateIso ||
      (() => {
        const [day, month, year] = actionable.date.split("-");
        return `${year}-${month}-${day}`;
      })();
    return {
      title: actionable.taskTitle || actionable.deadlineType,
      description: actionable.description || actionable.originalSentence,
      category:
        actionable.suggestedCategory || mapDeadlineToCategory(actionable.deadlineType),
      priority: actionable.priority || "MEDIUM",
      dueDate: `${iso}T23:59:00`,
    };
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
      const deadlineResp = await aiService.extractDeadlines(text.trim());
      setDeadlineResult(deadlineResp.data);
      const fromDeadlines = suggestedTaskFromDeadlines(deadlineResp.data);
      if (fromDeadlines) {
        setIntakeResult(fromDeadlines);
      } else {
        const intakeResp = await aiService.smartIntake(text.trim());
        setIntakeResult(intakeResp.data);
      }
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
      const fromDeadlines = suggestedTaskFromDeadlines(deadlineResp.data);
      if (fromDeadlines) {
        setIntakeResult(fromDeadlines);
      } else {
        const extracted = deadlineResp.data?.extractedText || "";
        if (extracted.trim()) {
          const intakeResp = await aiService.smartIntake(extracted.slice(0, 50000));
          setIntakeResult(intakeResp.data);
        }
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
      mode: "single",
      title: intakeResult.title,
      description: intakeResult.description,
      category: intakeResult.category,
      priority: intakeResult.priority,
      dueDate: intakeResult.dueDate,
    });
    handleClose();
  };

  const handleApplyDeadline = (deadline) => {
    if (!deadline?.date || deadline.deadlineType === "Document Date") return;
    const [day, month, year] = deadline.date.split("-");
    const isoDue = `${year}-${month}-${day}T23:59:00`;
    const suggested = deadlineResult?.suggestedTasks?.find(
      (t) =>
        t.sourceDeadlineType === deadline.deadlineType &&
        t.dueDate === `${year}-${month}-${day}`,
    );
    onApply({
      mode: "single",
      title: suggested?.title || deadline.taskTitle || deadline.deadlineType,
      description: suggested?.description || deadline.originalSentence,
      category:
        suggested?.category || mapDeadlineToCategory(deadline.deadlineType),
      priority: suggested?.priority || "MEDIUM",
      dueDate: isoDue,
    });
    handleClose();
  };

  const handleApplySuggested = (task) => {
    onApply({ mode: "single", ...toApplyPayload(task) });
    handleClose();
  };

  const handleCreateAllSuggested = () => {
    const tasks = actionableSuggestedTasks().map(toApplyPayload);
    if (!tasks.length) return;
    onApply({ mode: "batch", tasks });
    handleClose();
  };

  const hasResults = intakeResult || deadlineResult;
  const multiSuggested = actionableSuggestedTasks();

  return (
    <Modal show={show} onHide={handleClose} centered size="lg" scrollable>
      <Modal.Header closeButton>
        <Modal.Title className="d-flex align-items-center gap-2">
          <Sparkles size={20} className="text-primary" /> Smart Intake – OCR Deadline
          Extraction
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p className="text-muted small">
          Paste OCR text or upload a PDF/image notice. Our ML models extract every
          important date, classify its purpose, and suggest one task per deadline. Use{" "}
          <strong>Create All Tasks</strong> when a notice has multiple due dates.
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
                  PDF and images (PNG/JPG) supported — not Word (.docx). Max 15 MB.
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
                      <th>Fee</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {deadlineResult.dateRanges.map((range, idx) => (
                      <tr key={`range-${idx}`}>
                        <td>{range.purpose}</td>
                        <td>{range.startDate}</td>
                        <td>{range.endDate}</td>
                        <td>{range.lateFee || range.fineAmount || "—"}</td>
                        <td>
                          <Badge bg={confidenceVariant(range.confidence)}>
                            {range.confidence}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </>
            )}

            {deadlineResult.relationships?.length > 0 && (
              <>
                <h6 className="fw-semibold mt-3">Related Process Stages</h6>
                <ul className="small mb-3">
                  {deadlineResult.relationships.map((rel, idx) => (
                    <li key={`rel-${idx}`}>
                      <strong>{rel.processName}:</strong> {(rel.stages || []).join(" → ")}
                    </li>
                  ))}
                </ul>
              </>
            )}

            {multiSuggested.length > 0 && (
              <>
                <div className="d-flex justify-content-between align-items-center mt-3 mb-2">
                  <h6 className="fw-semibold mb-0">
                    Suggested Tasks ({multiSuggested.length})
                  </h6>
                  {multiSuggested.length > 1 && (
                    <Button size="sm" variant="success" onClick={handleCreateAllSuggested}>
                      Create All {multiSuggested.length} Tasks
                    </Button>
                  )}
                </div>
                <Table responsive size="sm" bordered className="mb-3">
                  <thead className="table-light">
                    <tr>
                      <th>Task</th>
                      <th>Due</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {multiSuggested.map((task, idx) => (
                      <tr key={`task-${idx}`}>
                        <td>
                          <div className="fw-semibold small">{task.title}</div>
                          {task.lateFee && (
                            <Badge bg="warning" text="dark" className="mt-1">
                              {task.lateFee} late fee
                            </Badge>
                          )}
                        </td>
                        <td className="text-nowrap small">
                          {task.dueDateDisplay || task.dueDate}
                        </td>
                        <td>
                          <Button
                            size="sm"
                            variant="outline-success"
                            onClick={() => handleApplySuggested(task)}
                          >
                            Prefill Form
                          </Button>
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
                            {deadline.fineAmount && (
                              <Badge bg="warning" text="dark" className="mt-1">
                                Fine {deadline.fineAmount}
                              </Badge>
                            )}
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
                            {deadline.priority && (
                              <div className="small mt-1">
                                <Badge bg="light" text="dark">
                                  {deadline.priority}
                                </Badge>
                              </div>
                            )}
                          </td>
                          <td>
                            <Badge bg={confidenceVariant(deadline.confidence)}>
                              {deadline.confidence}
                            </Badge>
                          </td>
                          <td>
                            {deadline.date && deadline.deadlineType !== "Document Date" && (
                              <Button
                                size="sm"
                                variant="outline-success"
                                onClick={() => handleApplyDeadline(deadline)}
                              >
                                Prefill Form
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
            <h6 className="fw-semibold mb-2">
              {multiSuggested.length > 1
                ? "Earliest / Primary Task"
                : "Suggested Primary Task"}
            </h6>
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
                Detected due date:{" "}
                {intakeResult.dueDateDisplay ||
                  new Date(intakeResult.dueDate).toLocaleDateString(undefined, {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                  })}
              </p>
            )}
            {intakeResult.description && (
              <p className="mb-0 mt-2 small">{intakeResult.description}</p>
            )}
            <div className="d-flex flex-wrap gap-2 mt-3">
              <Button variant="outline-secondary" size="sm" onClick={resetState}>
                Analyze Another
              </Button>
              {multiSuggested.length > 1 && (
                <Button variant="success" size="sm" onClick={handleCreateAllSuggested}>
                  Create All {multiSuggested.length} Tasks
                </Button>
              )}
              <Button
                variant={multiSuggested.length > 1 ? "outline-success" : "success"}
                size="sm"
                onClick={handleApplyIntake}
              >
                Prefill This One
              </Button>
            </div>
          </div>
        )}

        {hasResults && !intakeResult && (
          <div className="d-flex gap-2 mt-3">
            <Button variant="outline-secondary" size="sm" onClick={resetState}>
              Analyze Another
            </Button>
            {multiSuggested.length > 1 && (
              <Button size="sm" variant="success" onClick={handleCreateAllSuggested}>
                Create All {multiSuggested.length} Tasks
              </Button>
            )}
          </div>
        )}
      </Modal.Body>
    </Modal>
  );
};

export default SmartIntakeModal;
