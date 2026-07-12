import React, { useState, useContext, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Form,
  Button,
  Alert,
} from "react-bootstrap";
import { ArrowLeft, Sparkles } from "lucide-react";

import { TaskContext } from "../context/TaskContext";
import SmartIntakeModal from "../components/tasks/SmartIntakeModal";

// Converts an ISO date string into the "yyyy-MM-ddTHH:mm" format required by
// <input type="datetime-local">.
const toDatetimeLocalValue = (isoString) => {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
};

const emptyForm = {
  title: "",
  description: "",
  category: "ACADEMIC",
  dueDate: "",
  priority: "MEDIUM",
  impact: "MEDIUM",
  effort: "MEDIUM",
  notes: "",
  tags: "",
};

const CreateTask = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { createTask } = useContext(TaskContext);

  const [formData, setFormData] = useState({
    ...emptyForm,
    category: searchParams.get("category") || "ACADEMIC",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSmartIntake, setShowSmartIntake] = useState(
    searchParams.get("smart") === "true",
  );
  const [formError, setFormError] = useState("");

  useEffect(() => {
    if (searchParams.get("smart") === "true") {
      setShowSmartIntake(true);
    }
  }, [searchParams]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSmartIntakeResult = (result) => {
    setFormData((prev) => ({
      ...prev,
      title: result.title || prev.title,
      description: result.description || prev.description,
      category: result.category || prev.category,
      priority: result.priority || prev.priority,
      dueDate: result.dueDate ? toDatetimeLocalValue(result.dueDate) : prev.dueDate,
    }));
    setShowSmartIntake(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");

    if (!formData.title || !formData.dueDate) {
      setFormError("Please fill in the title and due date.");
      return;
    }

    setIsSubmitting(true);
    try {
      const tags = formData.tags
        ? formData.tags.split(",").map((tag) => tag.trim()).filter(Boolean)
        : [];

      const payload = {
        title: formData.title,
        description: formData.description,
        category: formData.category,
        priority: formData.priority,
        impact: formData.impact,
        effort: formData.effort,
        dueDate: new Date(formData.dueDate).toISOString(),
        tags,
        notes: formData.notes,
      };

      const result = await createTask(payload);
      if (result.success) {
        navigate(`/task/${result.task.id}`);
      }
    } catch (error) {
      console.error("Error creating task:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container fluid className="py-4">
      <Button
        variant="link"
        onClick={() => navigate(-1)}
        className="text-decoration-none mb-4 p-0"
      >
        <ArrowLeft className="me-2" />
        Back
      </Button>

      <Row>
        <Col lg={8} className="mx-auto">
          <Card className="shadow-sm">
            <Card.Header className="bg-primary text-white d-flex justify-content-between align-items-center">
              <h4 className="mb-0">Create New Task</h4>
              <Button
                variant="light"
                size="sm"
                onClick={() => setShowSmartIntake(true)}
              >
                <Sparkles size={16} className="me-1" /> Smart Intake
              </Button>
            </Card.Header>

            <Card.Body>
              {formError && <Alert variant="danger">{formError}</Alert>}

              <Alert variant="info" className="small">
                Task risk, impact simulation, and failure prediction are
                computed automatically by our machine learning models right
                after you create the task - you'll see them on the task
                details page.
              </Alert>

              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Task Title <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    placeholder="e.g., Submit Internship Application"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Description</Form.Label>
                  <Form.Control
                    as="textarea"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={3}
                    placeholder="Add details about this task..."
                  />
                </Form.Group>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Category</Form.Label>
                      <Form.Select
                        name="category"
                        value={formData.category}
                        onChange={handleChange}
                      >
                        <option value="ACADEMIC">📚 Academic</option>
                        <option value="OPPORTUNITY">💼 Opportunity</option>
                        <option value="PERSONAL_GOAL">🎯 Personal Goal</option>
                        <option value="EVENT">📅 Event</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>

                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>
                        Due Date & Time <span className="text-danger">*</span>
                      </Form.Label>
                      <Form.Control
                        type="datetime-local"
                        name="dueDate"
                        value={formData.dueDate}
                        onChange={handleChange}
                        required
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Row>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Priority</Form.Label>
                      <Form.Select
                        name="priority"
                        value={formData.priority}
                        onChange={handleChange}
                      >
                        <option value="HIGH">🔴 High</option>
                        <option value="MEDIUM">🟡 Medium</option>
                        <option value="LOW">🟢 Low</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>

                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Impact if Missed</Form.Label>
                      <Form.Select
                        name="impact"
                        value={formData.impact}
                        onChange={handleChange}
                      >
                        <option value="HIGH">🔴 High (Career/Grade affecting)</option>
                        <option value="MEDIUM">🟡 Medium (Important but not critical)</option>
                        <option value="LOW">🟢 Low (Can be rescheduled)</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>

                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Effort Required</Form.Label>
                      <Form.Select
                        name="effort"
                        value={formData.effort}
                        onChange={handleChange}
                      >
                        <option value="HIGH">🔴 High (8+ hours)</option>
                        <option value="MEDIUM">🟡 Medium (4-7 hours)</option>
                        <option value="LOW">🟢 Low (1-3 hours)</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>

                <Form.Group className="mb-3">
                  <Form.Label>Tags (comma separated)</Form.Label>
                  <Form.Control
                    type="text"
                    name="tags"
                    value={formData.tags}
                    onChange={handleChange}
                    placeholder="e.g., important, exam, project"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Additional Notes</Form.Label>
                  <Form.Control
                    as="textarea"
                    name="notes"
                    value={formData.notes}
                    onChange={handleChange}
                    rows={2}
                    placeholder="Any additional information..."
                  />
                </Form.Group>

                <div className="d-flex gap-2 mt-4">
                  <Button
                    variant="secondary"
                    onClick={() => navigate(-1)}
                    disabled={isSubmitting}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={isSubmitting}
                    className="flex-grow-1"
                  >
                    {isSubmitting ? "Creating..." : "Create Task"}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <SmartIntakeModal
        show={showSmartIntake}
        onHide={() => setShowSmartIntake(false)}
        onApply={handleSmartIntakeResult}
      />
    </Container>
  );
};

export default CreateTask;
