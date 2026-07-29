// src/components/dashboard/CognitiveLoadWarning.jsx
import React from "react";
import { Alert, Button, ProgressBar } from "react-bootstrap";
import { AlertTriangle, CheckCircle, ArrowRight } from "lucide-react";

const CognitiveLoadWarning = ({
  activeCount,
  warningMessage,
  maxCapacity = 5,
  onViewTasks,
  onPrioritize,
}) => {
  const loadPercentage = Math.min((activeCount / maxCapacity) * 100, 100);
  const isOverCapacity = activeCount >= maxCapacity;

  const getLoadColor = () => {
    if (activeCount >= maxCapacity) return "danger";
    if (activeCount >= maxCapacity - 1) return "warning";
    return "info";
  };

  return (
    <Alert variant={getLoadColor()} className="mb-0 border-0 shadow-sm p-3">
      <div className="d-flex align-items-start gap-3">
        <div className="flex-shrink-0 d-inline-flex align-items-center mt-1">
          {isOverCapacity ? (
            <AlertTriangle size={24} className="text-danger" />
          ) : (
            <CheckCircle size={24} className="text-success" />
          )}
        </div>
        <div className="flex-grow-1 min-w-0">
          <h6 className="dash-card-title mb-2">
            Cognitive Load: {activeCount} / {maxCapacity} Active Tasks
          </h6>
          <ProgressBar
            now={loadPercentage}
            variant={getLoadColor()}
            className="mb-2"
            style={{ height: "8px" }}
          />
          {warningMessage && <p className="mb-2 dash-body">{warningMessage}</p>}
          {isOverCapacity ? (
            <div className="d-flex flex-wrap gap-2 align-items-center">
              <Button
                size="sm"
                variant="danger"
                className="dash-btn-icon"
                onClick={onViewTasks}
              >
                View Active Tasks
              </Button>
              <Button
                size="sm"
                variant="outline-danger"
                className="dash-btn-icon"
                onClick={onPrioritize}
              >
                <ArrowRight size={14} />
                Review & Prioritize
              </Button>
            </div>
          ) : (
            <p className="mb-0 dash-meta text-muted">
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
