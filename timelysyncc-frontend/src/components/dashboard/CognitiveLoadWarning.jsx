// src/components/dashboard/CognitiveLoadWarning.jsx
import React from "react";
import { Alert, Button, ProgressBar } from "react-bootstrap";
import { AlertTriangle, CheckCircle, ArrowRight } from "lucide-react";

const CognitiveLoadWarning = ({
  activeCount,
  warningMessage,
  maxCapacity = 5,
}) => {
  const loadPercentage = Math.min((activeCount / maxCapacity) * 100, 100);
  const isOverCapacity = activeCount >= maxCapacity;

  const getLoadColor = () => {
    if (activeCount >= maxCapacity) return "danger";
    if (activeCount >= maxCapacity - 1) return "warning";
    return "info";
  };

  return (
    <Alert variant={getLoadColor()} className="mb-4 border-0 shadow-sm">
      <div className="d-flex align-items-start gap-3">
        <div className="flex-shrink-0">
          {isOverCapacity ? (
            <AlertTriangle size={32} className="text-danger" />
          ) : (
            <CheckCircle size={32} className="text-success" />
          )}
        </div>
        <div className="flex-grow-1">
          <h6 className="fw-semibold mb-1">
            Cognitive Load: {activeCount} / {maxCapacity} Active Tasks
          </h6>
          <ProgressBar
            now={loadPercentage}
            variant={getLoadColor()}
            className="mb-2"
            style={{ height: "8px" }}
          />
          {warningMessage && <p className="mb-2 small">{warningMessage}</p>}
          {isOverCapacity ? (
            <div className="d-flex gap-2">
              <Button size="sm" variant="danger">
                View Active Tasks
              </Button>
              <Button size="sm" variant="outline-danger">
                <ArrowRight size={14} /> Review & Prioritize
              </Button>
            </div>
          ) : (
            <p className="mb-0 small text-muted">
              You have capacity for {maxCapacity - activeCount} more task
              {maxCapacity - activeCount !== 1 ? "s" : ""}
            </p>
          )}
        </div>
      </div>
    </Alert>
  );
};

export default CognitiveLoadWarning;
