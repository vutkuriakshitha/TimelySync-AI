// src/pages/AcademicPlanner.jsx
import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Badge,
  Form,
  InputGroup,
} from "react-bootstrap";
import {
  PlusCircle,
  Search,
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import { TaskContext } from "../context/TaskContext";

const AcademicPlanner = () => {
  const navigate = useNavigate();
  const { tasks, completeTask } = useContext(TaskContext);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("ALL");

  const academicTasks = tasks.filter((task) => task.category === "ACADEMIC");

  const filteredTasks = academicTasks.filter((task) => {
    const matchesSearch =
      task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (task.description &&
        task.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus =
      filterStatus === "ALL" ||
      (filterStatus === "ACTIVE" && task.status === "ACTIVE") ||
      (filterStatus === "COMPLETED" && task.status === "COMPLETED") ||
      (filterStatus === "OVERDUE" &&
        task.dueDate &&
        new Date(task.dueDate) < new Date() &&
        task.status !== "COMPLETED");
    return matchesSearch && matchesStatus;
  });

  const getRiskBadge = (riskLevel, riskScore) => {
    if (riskLevel === "CRITICAL") {
      return (
        <Badge bg="danger" pill>
          <AlertTriangle size={12} className="me-1" /> Critical ({riskScore}%)
        </Badge>
      );
    }
    if (riskLevel === "WARNING") {
      return (
        <Badge bg="warning" pill>
          <AlertTriangle size={12} className="me-1" /> Warning ({riskScore}%)
        </Badge>
      );
    }
    return (
      <Badge bg="success" pill>
        Safe ({riskScore}%)
      </Badge>
    );
  };

  const formatDate = (date) => {
    if (!date) return "No date";
    return new Date(date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getDaysRemaining = (dueDate) => {
    const days = Math.ceil(
      (new Date(dueDate) - new Date()) / (1000 * 60 * 60 * 24),
    );
    if (days < 0) return `${Math.abs(days)} days overdue`;
    if (days === 0) return "Due today";
    return `${days} days left`;
  };

  return (
    <Container fluid className="py-4">
      <Row className="mb-4 align-items-center">
        <Col>
          <h2 className="text-primary mb-1">Academic Planner</h2>
          <p className="text-muted">
            Manage your assignments, exams, and submissions
          </p>
        </Col>
        <Col xs="auto">
          <Button
            variant="primary"
            onClick={() => navigate("/create-task?category=ACADEMIC")}
          >
            <PlusCircle size={18} className="me-2" />
            Add Academic Task
          </Button>
        </Col>
      </Row>

      {/* Search and Filters */}
      <Row className="mb-4">
        <Col md={6}>
          <InputGroup>
            <InputGroup.Text className="bg-white">
              <Search size={18} />
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Search academic tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Col>
        <Col md={3}>
          <Form.Select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="ALL">All Tasks</option>
            <option value="ACTIVE">Active</option>
            <option value="COMPLETED">Completed</option>
            <option value="OVERDUE">Overdue</option>
          </Form.Select>
        </Col>
      </Row>

      {/* Tasks Grid */}
      <Row>
        {filteredTasks.length > 0 ? (
          filteredTasks.map((task) => (
            <Col md={6} lg={4} key={task.id} className="mb-4">
              <Card
                className="shadow-sm h-100 hover-shadow"
                style={{ cursor: "pointer" }}
                onClick={() => navigate(`/task/${task.id}`)}
              >
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <h5 className="mb-0">{task.title}</h5>
                    {task.riskAnalysis &&
                      getRiskBadge(task.riskAnalysis.riskLevel, task.riskAnalysis.riskScore)}
                  </div>

                  {task.description && (
                    <p className="text-muted small mb-3">
                      {task.description.length > 100
                        ? task.description.substring(0, 100) + "..."
                        : task.description}
                    </p>
                  )}

                  <div className="mb-3">
                    <div className="d-flex align-items-center gap-2 mb-1">
                      <Calendar size={14} className="text-muted" />
                      <small className="text-muted">
                        Due: {formatDate(task.dueDate)}
                      </small>
                    </div>
                    <div className="d-flex align-items-center gap-2">
                      <Clock size={14} className="text-muted" />
                      <small
                        className={`${task.dueDate && new Date(task.dueDate) < new Date() && task.status !== "COMPLETED" ? "text-danger" : "text-muted"}`}
                      >
                        {getDaysRemaining(task.dueDate)}
                      </small>
                    </div>
                  </div>

                  <div className="d-flex gap-2">
                    <Badge
                      bg={task.status === "COMPLETED" ? "success" : "primary"}
                      pill
                    >
                      {task.status === "COMPLETED"
                        ? "Completed"
                        : "In Progress"}
                    </Badge>
                    {task.priority && (
                      <Badge
                        bg={
                          task.priority === "HIGH"
                            ? "danger"
                            : task.priority === "MEDIUM"
                              ? "warning"
                              : "success"
                        }
                        pill
                      >
                        {task.priority} Priority
                      </Badge>
                    )}
                  </div>
                </Card.Body>
                <Card.Footer className="bg-white border-top-0">
                  <div className="d-flex justify-content-between">
                    <small className="text-muted">
                      {task.subtasks?.filter((s) => s.completed).length || 0}/
                      {task.subtasks?.length || 0} subtasks
                    </small>
                    {task.status !== "COMPLETED" && (
                      <Button
                        variant="success"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          completeTask(task.id);
                        }}
                      >
                        <CheckCircle size={14} className="me-1" />
                        Complete
                      </Button>
                    )}
                  </div>
                </Card.Footer>
              </Card>
            </Col>
          ))
        ) : (
          <Col>
            <div className="text-center py-5">
              <Calendar size={48} className="text-muted mb-3" />
              <h6 className="text-muted">No academic tasks found</h6>
              <Button
                variant="primary"
                onClick={() => navigate("/create-task?category=ACADEMIC")}
                className="mt-2"
              >
                <PlusCircle className="me-2" />
                Add your first academic task
              </Button>
            </div>
          </Col>
        )}
      </Row>
    </Container>
  );
};

export default AcademicPlanner;
