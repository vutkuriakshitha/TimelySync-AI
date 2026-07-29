// src/components/tasks/FailurePredictionCard.jsx
import React from "react";
import { Card, Badge, ProgressBar } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { Brain, ArrowRight } from "lucide-react";

const FailurePredictionCard = ({ predictions }) => {
  const navigate = useNavigate();

  const getRiskColor = (probability) => {
    if (probability >= 70) return "danger";
    if (probability >= 40) return "warning";
    return "success";
  };

  if (!predictions || predictions.length === 0) return null;

  return (
    <Card className="shadow-sm border-0 mb-0 dash-ai-card">
      <Card.Header className="dash-ai-card__header text-white dash-card-header">
        <div className="d-flex align-items-center gap-2">
          <Brain size={16} className="flex-shrink-0" />
          <h6 className="mb-0 dash-card-title text-truncate">AI Failure Predictions</h6>
        </div>
      </Card.Header>
      <Card.Body className="p-0">
        {predictions.slice(0, 3).map((pred) => (
          <div
            key={pred.taskId}
            className="dash-list-item dash-ai-item"
            style={{ cursor: "pointer" }}
            onClick={() => navigate(`/task/${pred.taskId}`)}
          >
            <div className="d-flex justify-content-between align-items-center gap-2 mb-2">
              <span className="fw-semibold dash-body text-truncate min-w-0">
                {pred.title}
              </span>
              <Badge bg={getRiskColor(pred.probability)} pill className="dash-meta flex-shrink-0">
                {pred.probability}% risk
              </Badge>
            </div>
            {pred.riskFactors && pred.riskFactors.length > 0 && (
              <p className="dash-meta text-muted mb-2 dash-task-desc">{pred.riskFactors[0]}</p>
            )}
            <ProgressBar
              now={pred.probability}
              variant={getRiskColor(pred.probability)}
              style={{ height: "8px" }}
              className="mb-2"
            />
            <div className="d-flex justify-content-end">
              <small className="text-primary dash-icon-text dash-meta">
                View Task <ArrowRight size={12} />
              </small>
            </div>
          </div>
        ))}
      </Card.Body>
    </Card>
  );
};

export default FailurePredictionCard;
