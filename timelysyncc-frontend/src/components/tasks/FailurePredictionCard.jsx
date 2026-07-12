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
    <Card className="shadow-sm border-0 mb-4">
      <Card.Header className="bg-danger text-white">
        <div className="d-flex align-items-center gap-2">
          <Brain size={18} />
          <h6 className="mb-0 fw-semibold">AI Failure Predictions</h6>
        </div>
      </Card.Header>
      <Card.Body className="p-0">
        {predictions.slice(0, 3).map((pred) => (
          <div
            key={pred.taskId}
            className="p-3 border-bottom"
            style={{ cursor: "pointer" }}
            onClick={() => navigate(`/task/${pred.taskId}`)}
          >
            <div className="d-flex justify-content-between align-items-start mb-2">
              <span className="fw-semibold">{pred.title}</span>
              <Badge bg={getRiskColor(pred.probability)} pill>
                {pred.probability}% risk
              </Badge>
            </div>
            {pred.riskFactors && pred.riskFactors.length > 0 && (
              <p className="small text-muted mb-2">{pred.riskFactors[0]}</p>
            )}
            <ProgressBar
              now={pred.probability}
              variant={getRiskColor(pred.probability)}
              style={{ height: "6px" }}
              className="mb-2"
            />
            <div className="d-flex justify-content-end">
              <small className="text-primary d-flex align-items-center gap-1">
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
