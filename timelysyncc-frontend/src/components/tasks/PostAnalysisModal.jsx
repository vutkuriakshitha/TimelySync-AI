// src/components/tasks/PostAnalysisModal.jsx
import React from "react";
import { Modal, Button, ProgressBar, Alert, Badge } from "react-bootstrap";
import { CheckCircle, XCircle, Target, Brain, AlertCircle } from "lucide-react";

const PostAnalysisModal = ({ show, onHide, analysis, taskTitle }) => {
  if (!analysis) return null;

  const verdict = analysis.completedOnTime
    ? {
        icon: <CheckCircle size={32} className="text-success" />,
        title: "Successfully Completed! 🎉",
        message: `You completed "${taskTitle}" on time. Great job!`,
        variant: "success",
      }
    : {
        icon: <XCircle size={32} className="text-danger" />,
        title: "Task Missed",
        message: `You missed "${taskTitle}" by ${analysis.daysLate} days. Let's understand why.`,
        variant: "danger",
      };

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton className={`bg-${verdict.variant} text-white`}>
        <Modal.Title className="d-flex align-items-center gap-2">
          {verdict.icon}
          Post-Deadline Analysis
        </Modal.Title>
      </Modal.Header>
      <Modal.Body className="p-4">
        <div className="text-center mb-4">
          <div className="mb-3">{verdict.icon}</div>
          <h4>{verdict.title}</h4>
          <p className="text-muted">{verdict.message}</p>
        </div>

        <Alert variant="info" className="mb-4">
          <Brain size={18} className="me-2" />
          <strong>Root Cause Analysis</strong>
        </Alert>

        <h6 className="fw-semibold mb-3">Contributing Factors</h6>
        {analysis.causes?.map((cause, idx) => (
          <div key={idx} className="mb-3">
            <div className="d-flex justify-content-between mb-1">
              <div className="d-flex align-items-center gap-2">
                <AlertCircle size={14} className="text-warning" />
                <span className="fw-medium">{cause.type}</span>
              </div>
              <Badge bg="secondary" pill>
                {cause.percentage}%
              </Badge>
            </div>
            <ProgressBar
              now={cause.percentage}
              variant="warning"
              style={{ height: "6px" }}
            />
            <p className="small text-muted mt-1 mb-0">{cause.description}</p>
          </div>
        ))}

        <Alert variant="success" className="mb-4">
          <Target size={18} className="me-2" />
          <strong>Recommendation</strong>
          <p className="mb-0 mt-1">{analysis.recommendation}</p>
        </Alert>

        <div className="d-flex gap-2 mt-4">
          <Button
            variant="outline-primary"
            onClick={onHide}
            className="flex-grow-1"
          >
            Close
          </Button>
          <Button variant="primary" className="flex-grow-1">
            <Target size={16} className="me-2" />
            Create Similar Task
          </Button>
        </div>
      </Modal.Body>
    </Modal>
  );
};

export default PostAnalysisModal;
