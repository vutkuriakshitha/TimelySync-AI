// src/pages/TaskDetail.jsx
import React, { useState, useEffect, useContext } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Badge,
  ProgressBar,
  ListGroup,
  Spinner,
  Form,
  Modal,
  Alert,
  Breadcrumb,
  InputGroup,
} from "react-bootstrap";
import {
  Calendar,
  Clock,
  Flag,
  Tag,
  FileText,
  CheckCircle,
  Trash2,
  Edit2,
  AlertTriangle,
  Brain,
  Shield,
  Target,
  BarChart3,
  Plus,
} from "lucide-react";
import { TaskContext } from "../context/TaskContext";
import ImpactSimulationModal from "../components/tasks/ImpactSimulationModal";
import PostAnalysisModal from "../components/tasks/PostAnalysisModal";

const TaskDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const {
    tasks,
    loading: tasksLoading,
    updateTask,
    deleteTask,
    completeTask,
    toggleSubtask,
    addSubtask,
  } = useContext(TaskContext);

  const task = tasks.find((t) => t.id === id);

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showImpactModal, setShowImpactModal] = useState(false);
  const [showPostAnalysis, setShowPostAnalysis] = useState(false);
  const [completionProof, setCompletionProof] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [newSubtaskTitle, setNewSubtaskTitle] = useState("");

  useEffect(() => {
    if (!tasksLoading && !task) {
      navigate("/dashboard");
      return;
    }
    if (task) {
      setEditForm({
        title: task.title,
        description: task.description || "",
        dueDate: task.dueDate ? new Date(task.dueDate).toISOString().slice(0, 16) : "",
        priority: task.priority || "MEDIUM",
        impact: task.impact || "MEDIUM",
        effort: task.effort || "MEDIUM",
        category: task.category || "ACADEMIC",
        tags: task.tags?.join(", ") || "",
        notes: task.notes || "",
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, task?.id, tasksLoading]);

  const handleUpdate = async () => {
    setIsSubmitting(true);
    try {
      await updateTask(id, {
        ...editForm,
        dueDate: editForm.dueDate ? new Date(editForm.dueDate).toISOString() : null,
        tags: editForm.tags ? editForm.tags.split(",").map((t) => t.trim()).filter(Boolean) : [],
      });
      setShowEditModal(false);
    } catch (error) {
      console.error("Error updating task:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    await deleteTask(id);
    setShowDeleteModal(false);
    navigate("/dashboard");
  };

  const handleComplete = async () => {
    setIsSubmitting(true);
    try {
      const completed = await completeTask(id, completionProof);
      setShowCompleteModal(false);
      setCompletionProof(null);
      if (completed.postAnalysis) {
        setShowPostAnalysis(true);
      }
    } catch (error) {
      console.error("Error completing task:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddSubtask = async (e) => {
    e.preventDefault();
    if (!newSubtaskTitle.trim()) return;
    try {
      await addSubtask(id, { title: newSubtaskTitle.trim() });
      setNewSubtaskTitle("");
    } catch (error) {
      console.error("Error adding subtask:", error);
    }
  };

  const handleToggleSubtask = async (subtaskId) => {
    try {
      await toggleSubtask(id, subtaskId);
    } catch (error) {
      console.error("Error toggling subtask:", error);
    }
  };

  const getRiskConfig = (riskLevel) => {
    switch (riskLevel) {
      case "CRITICAL":
        return { bg: "danger", text: "Critical Risk", icon: <AlertTriangle />, color: "#dc2626" };
      case "WARNING":
        return { bg: "warning", text: "Warning", icon: <AlertTriangle />, color: "#f59e0b" };
      default:
        return { bg: "success", text: "Safe", icon: <Shield />, color: "#10b981" };
    }
  };

  const getPriorityConfig = (priority) => {
    switch (priority) {
      case "HIGH":
        return { bg: "danger", text: "High Priority" };
      case "MEDIUM":
        return { bg: "warning", text: "Medium Priority" };
      default:
        return { bg: "success", text: "Low Priority" };
    }
  };

  const formatDate = (date) => {
    if (!date) return "Not set";
    return new Date(date).toLocaleString();
  };

  const getDaysRemaining = () => {
    if (!task?.dueDate) return null;
    const days = Math.ceil((new Date(task.dueDate) - new Date()) / (1000 * 60 * 60 * 24));
    if (days < 0) return `${Math.abs(days)} days overdue`;
    if (days === 0) return "Due today";
    return `${days} days remaining`;
  };

  if (tasksLoading || !task) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3">Loading task details...</p>
      </Container>
    );
  }

  const riskConfig = getRiskConfig(task.riskAnalysis?.riskLevel);
  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date() && task.status !== "COMPLETED";
  const needsDecomposition =
    task.status === "ACTIVE" &&
    task.riskAnalysis?.riskLevel === "CRITICAL" &&
    (!task.subtasks || task.subtasks.length === 0);

  return (
    <Container fluid className="py-4">
      <Breadcrumb className="mb-4">
        <Breadcrumb.Item onClick={() => navigate("/dashboard")} style={{ cursor: "pointer" }}>
          Dashboard
        </Breadcrumb.Item>
        <Breadcrumb.Item active>{task.title}</Breadcrumb.Item>
      </Breadcrumb>

      <Row>
        <Col lg={8}>
          <Card className="shadow-sm mb-4">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start mb-3 flex-wrap gap-2">
                <div>
                  <h2 className="mb-2">{task.title}</h2>
                  <div className="d-flex gap-2 flex-wrap">
                    {task.riskAnalysis && (
                      <Badge bg={riskConfig.bg} pill className="px-3 py-2">
                        {riskConfig.icon} {riskConfig.text} ({task.riskAnalysis?.riskScore}%)
                      </Badge>
                    )}
                    <Badge bg={getPriorityConfig(task.priority).bg} pill className="px-3 py-2">
                      <Flag size={12} className="me-1" />
                      {getPriorityConfig(task.priority).text}
                    </Badge>
                    {task.status === "COMPLETED" && (
                      <Badge bg="success" pill className="px-3 py-2">
                        <CheckCircle size={12} className="me-1" />
                        Completed
                      </Badge>
                    )}
                    {isOverdue && (
                      <Badge bg="danger" pill className="px-3 py-2">
                        <AlertTriangle size={12} className="me-1" />
                        Overdue
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="d-flex gap-2">
                  {task.status !== "COMPLETED" && (
                    <Button variant="success" onClick={() => setShowCompleteModal(true)}>
                      <CheckCircle className="me-2" />
                      Complete
                    </Button>
                  )}
                  <Button variant="outline-primary" onClick={() => setShowEditModal(true)}>
                    <Edit2 className="me-2" />
                    Edit
                  </Button>
                  <Button variant="outline-danger" onClick={() => setShowDeleteModal(true)}>
                    <Trash2 className="me-2" />
                    Delete
                  </Button>
                </div>
              </div>

              {task.description && (
                <div className="mb-4">
                  <h6 className="fw-semibold mb-2">Description</h6>
                  <p className="text-muted">{task.description}</p>
                </div>
              )}

              <Row className="g-3 mb-4">
                <Col md={6}>
                  <div className="d-flex align-items-center gap-2">
                    <Calendar className="text-primary" />
                    <div>
                      <small className="text-muted d-block">Due Date</small>
                      <span className="fw-semibold">{formatDate(task.dueDate)}</span>
                    </div>
                  </div>
                </Col>
                <Col md={6}>
                  <div className="d-flex align-items-center gap-2">
                    <Clock className="text-primary" />
                    <div>
                      <small className="text-muted d-block">Time Status</small>
                      <span className={isOverdue ? "text-danger fw-semibold" : "fw-semibold"}>
                        {getDaysRemaining()}
                      </span>
                    </div>
                  </div>
                </Col>
                <Col md={6}>
                  <div className="d-flex align-items-center gap-2">
                    <Target className="text-primary" />
                    <div>
                      <small className="text-muted d-block">Category</small>
                      <span className="fw-semibold">{task.category?.replace("_", " ")}</span>
                    </div>
                  </div>
                </Col>
                <Col md={6}>
                  <div className="d-flex align-items-center gap-2">
                    <BarChart3 className="text-primary" />
                    <div>
                      <small className="text-muted d-block">Impact</small>
                      <span className="fw-semibold">{task.impact} impact if missed</span>
                    </div>
                  </div>
                </Col>
              </Row>

              {task.tags && task.tags.length > 0 && (
                <div className="mb-4">
                  <h6 className="fw-semibold mb-2">Tags</h6>
                  <div className="d-flex flex-wrap gap-2">
                    {task.tags.map((tag, idx) => (
                      <Badge key={idx} bg="secondary" pill className="px-3 py-2">
                        <Tag size={10} className="me-1" />
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {task.notes && (
                <div className="mb-4">
                  <h6 className="fw-semibold mb-2">Notes</h6>
                  <p className="text-muted bg-light p-3 rounded">{task.notes}</p>
                </div>
              )}

              {task.proofFileName && (
                <div className="mb-4">
                  <h6 className="fw-semibold mb-2">Proof of Completion</h6>
                  <Alert variant="success" className="d-flex align-items-center mb-0">
                    <FileText size={18} className="me-2" />
                    <span>{task.proofFileName}</span>
                  </Alert>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Subtasks Section */}
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-white">
              <h6 className="mb-0 fw-semibold">Subtasks</h6>
            </Card.Header>
            {task.subtasks && task.subtasks.length > 0 && (
              <ListGroup variant="flush">
                {task.subtasks.map((subtask) => (
                  <ListGroup.Item key={subtask.id} className="d-flex align-items-center gap-3">
                    <Form.Check
                      type="checkbox"
                      checked={subtask.completed}
                      onChange={() => handleToggleSubtask(subtask.id)}
                    />
                    <span className={subtask.completed ? "text-muted text-decoration-line-through" : ""}>
                      {subtask.title}
                    </span>
                    {subtask.dueDate && (
                      <small className="text-muted ms-auto">Due: {formatDate(subtask.dueDate)}</small>
                    )}
                  </ListGroup.Item>
                ))}
              </ListGroup>
            )}
            <Card.Body className="pt-3">
              <Form onSubmit={handleAddSubtask}>
                <InputGroup>
                  <Form.Control
                    placeholder="Add a subtask..."
                    value={newSubtaskTitle}
                    onChange={(e) => setNewSubtaskTitle(e.target.value)}
                  />
                  <Button type="submit" variant="outline-primary">
                    <Plus size={16} />
                  </Button>
                </InputGroup>
              </Form>
            </Card.Body>
          </Card>

          {/* Impact Simulation */}
          {task.impactSimulation && (
            <Card className="shadow-sm mb-4 border-warning">
              <Card.Header className="bg-warning text-white">
                <div className="d-flex align-items-center gap-2">
                  <AlertTriangle size={18} />
                  <h6 className="mb-0 fw-semibold">Impact Simulation</h6>
                </div>
              </Card.Header>
              <Card.Body>
                <p className="small text-muted mb-3">
                  If you miss this deadline, here's what could happen:
                </p>
                {task.impactSimulation.consequences?.map((cons, idx) => (
                  <div key={idx} className="mb-2">
                    <div className="d-flex justify-content-between small mb-1">
                      <span>{cons.description}</span>
                      <span className="text-danger">{cons.probabilityPercent}% probability</span>
                    </div>
                    <ProgressBar now={cons.probabilityPercent} variant="danger" style={{ height: "4px" }} />
                  </div>
                ))}
                <Button
                  variant="outline-warning"
                  size="sm"
                  className="mt-3"
                  onClick={() => setShowImpactModal(true)}
                >
                  View Full Impact Analysis →
                </Button>
              </Card.Body>
            </Card>
          )}
        </Col>

        <Col lg={4}>
          {task.riskAnalysis && task.status === "ACTIVE" && (
            <Card className="shadow-sm mb-4 border-primary">
              <Card.Header className="bg-primary text-white">
                <div className="d-flex align-items-center gap-2">
                  <Brain size={18} />
                  <h6 className="mb-0 fw-semibold">AI Intelligence</h6>
                </div>
              </Card.Header>
              <Card.Body>
                <div className="mb-3">
                  <h6 className="fw-semibold">Failure Risk</h6>
                  <div className="d-flex align-items-center gap-2 mb-2">
                    <span className="fw-bold">{task.riskAnalysis.riskScore}%</span>
                    <ProgressBar
                      now={task.riskAnalysis.riskScore}
                      variant={task.riskAnalysis.riskScore > 70 ? "danger" : "warning"}
                      style={{ width: "100%" }}
                    />
                  </div>
                </div>

                {task.riskAnalysis.riskFactors && task.riskAnalysis.riskFactors.length > 0 && (
                  <div className="mb-3">
                    <h6 className="fw-semibold">Risk Factors</h6>
                    <ul className="small text-muted mb-0">
                      {task.riskAnalysis.riskFactors.map((factor, idx) => (
                        <li key={idx}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {needsDecomposition && (
                  <Alert variant="warning" className="mb-0">
                    <strong>⚠️ High Risk Task</strong>
                    <p className="small mb-0 mt-1">
                      This task needs to be broken down into smaller steps.
                      Consider adding subtasks below.
                    </p>
                  </Alert>
                )}
              </Card.Body>
            </Card>
          )}

          {task.riskAnalysis && task.status === "ACTIVE" && (
            <Card className="shadow-sm mb-4">
              <Card.Body className="text-center">
                <h6 className="text-muted mb-2">Risk Score</h6>
                <div className="position-relative d-inline-block mb-3">
                  <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="54" fill="none" stroke="#e5e7eb" strokeWidth="12" />
                    <circle
                      cx="60"
                      cy="60"
                      r="54"
                      fill="none"
                      stroke={riskConfig.color}
                      strokeWidth="12"
                      strokeDasharray={`${(task.riskAnalysis.riskScore / 100) * 339.292} 339.292`}
                      strokeLinecap="round"
                      transform="rotate(-90 60 60)"
                    />
                  </svg>
                  <div className="position-absolute top-50 start-50 translate-middle">
                    <span className="h2 fw-bold" style={{ color: riskConfig.color }}>
                      {task.riskAnalysis.riskScore}%
                    </span>
                  </div>
                </div>
                <p className="mb-0">Risk Level: {riskConfig.text}</p>
              </Card.Body>
            </Card>
          )}

          <Card className="shadow-sm">
            <Card.Body>
              <h6 className="fw-semibold mb-3">Timeline</h6>
              <div className="position-relative ps-3">
                <div className="position-absolute start-0 top-0 bottom-0 w-px bg-light" />
                <div className="mb-3">
                  <small className="text-muted">Created</small>
                  <p className="mb-0 fw-semibold">{formatDate(task.createdAt)}</p>
                </div>
                {task.completedAt && (
                  <div className="mb-3">
                    <small className="text-muted">Completed</small>
                    <p className="mb-0 fw-semibold text-success">{formatDate(task.completedAt)}</p>
                  </div>
                )}
                {task.postAnalysis && (
                  <div>
                    <Button variant="link" className="p-0" onClick={() => setShowPostAnalysis(true)}>
                      View Post-Analysis Report →
                    </Button>
                  </div>
                )}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modals */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)} size="lg" centered>
        <Modal.Header closeButton>
          <Modal.Title>Edit Task</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                value={editForm.title || ""}
                onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={editForm.description || ""}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Due Date</Form.Label>
                  <Form.Control
                    type="datetime-local"
                    value={editForm.dueDate || ""}
                    onChange={(e) => setEditForm({ ...editForm, dueDate: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Category</Form.Label>
                  <Form.Select
                    value={editForm.category || "ACADEMIC"}
                    onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                  >
                    <option value="ACADEMIC">Academic</option>
                    <option value="OPPORTUNITY">Opportunity</option>
                    <option value="PERSONAL_GOAL">Personal Goal</option>
                    <option value="EVENT">Event</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Priority</Form.Label>
                  <Form.Select
                    value={editForm.priority || "MEDIUM"}
                    onChange={(e) => setEditForm({ ...editForm, priority: e.target.value })}
                  >
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Impact</Form.Label>
                  <Form.Select
                    value={editForm.impact || "MEDIUM"}
                    onChange={(e) => setEditForm({ ...editForm, impact: e.target.value })}
                  >
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Effort</Form.Label>
                  <Form.Select
                    value={editForm.effort || "MEDIUM"}
                    onChange={(e) => setEditForm({ ...editForm, effort: e.target.value })}
                  >
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Tags (comma separated)</Form.Label>
              <Form.Control
                type="text"
                value={editForm.tags || ""}
                onChange={(e) => setEditForm({ ...editForm, tags: e.target.value })}
                placeholder="urgent, project, important"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Notes</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                value={editForm.notes || ""}
                onChange={(e) => setEditForm({ ...editForm, notes: e.target.value })}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowEditModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleUpdate} disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : "Save Changes"}
          </Button>
        </Modal.Footer>
      </Modal>

      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Delete Task</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="danger" className="mb-0">
            <AlertTriangle className="me-2" />
            Are you sure you want to delete "{task.title}"? This action cannot be undone.
          </Alert>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            Delete Task
          </Button>
        </Modal.Footer>
      </Modal>

      <Modal show={showCompleteModal} onHide={() => setShowCompleteModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Complete Task</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Mark "{task.title}" as completed?</p>
          <Form.Group className="mt-3">
            <Form.Label>Upload Proof (Optional)</Form.Label>
            <Form.Control type="file" onChange={(e) => setCompletionProof(e.target.files[0])} />
            <Form.Text className="text-muted">
              Upload screenshot, document, or evidence of completion
            </Form.Text>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowCompleteModal(false)}>
            Cancel
          </Button>
          <Button variant="success" onClick={handleComplete} disabled={isSubmitting}>
            {isSubmitting ? <Spinner size="sm" className="me-2" /> : <CheckCircle className="me-2" />}
            Complete Task
          </Button>
        </Modal.Footer>
      </Modal>

      <ImpactSimulationModal show={showImpactModal} onHide={() => setShowImpactModal(false)} task={task} />

      <PostAnalysisModal
        show={showPostAnalysis}
        onHide={() => setShowPostAnalysis(false)}
        analysis={task?.postAnalysis}
        taskTitle={task?.title}
      />
    </Container>
  );
};

export default TaskDetail;
