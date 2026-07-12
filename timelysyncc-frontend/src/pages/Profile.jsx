// src/pages/Profile.jsx
import React, { useContext, useState } from "react";
import {
  Container,
  Row,
  Col,
  Card,
  Form,
  Button,
} from "react-bootstrap";
import { User, Mail, Calendar, Award, Shield, CheckCircle, AlertTriangle } from "lucide-react";
import { AuthContext } from "../context/AuthContext";
import { TaskContext } from "../context/TaskContext";
import toast from "react-hot-toast";

const Profile = () => {
  const { user, updateUser } = useContext(AuthContext);
  const { tasks } = useContext(TaskContext);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || "",
    bio: user?.bio || "",
  });

  const stats = {
    totalTasks: tasks.length,
    completedTasks: tasks.filter((t) => t.status === "COMPLETED").length,
    onTimeRate: tasks.filter((t) => t.status === "COMPLETED" && t.postAnalysis?.completedOnTime).length,
    highRiskTasks: tasks.filter((t) => t.riskAnalysis?.riskLevel === "CRITICAL" && t.status === "ACTIVE").length,
  };

  const handleSave = async () => {
    setIsSaving(true);
    const result = await updateUser(formData);
    setIsSaving(false);
    if (result.success) {
      setIsEditing(false);
      toast.success("Profile updated successfully!");
    }
  };

  return (
    <Container fluid className="py-4">
      <Row>
        <Col lg={4} className="mb-4">
          <Card className="shadow-sm text-center">
            <Card.Body>
              <div
                className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3"
                style={{ width: "100px", height: "100px" }}
              >
                <span className="display-4">{user?.name?.charAt(0) || "U"}</span>
              </div>
              <h4>{user?.name}</h4>
              <p className="text-muted">{user?.email}</p>
              <Button
                variant="outline-primary"
                onClick={() => {
                  setFormData({ name: user?.name || "", bio: user?.bio || "" });
                  setIsEditing(!isEditing);
                }}
              >
                {isEditing ? "Cancel" : "Edit Profile"}
              </Button>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={8}>
          {isEditing ? (
            <Card className="shadow-sm">
              <Card.Body>
                <h5 className="mb-4">Edit Profile</h5>
                <Form>
                  <Form.Group className="mb-3">
                    <Form.Label>Name</Form.Label>
                    <Form.Control
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Email</Form.Label>
                    <Form.Control type="email" value={user?.email || ""} disabled />
                    <Form.Text className="text-muted">Email cannot be changed</Form.Text>
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Bio</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={3}
                      value={formData.bio}
                      onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                      placeholder="Tell us about yourself..."
                    />
                  </Form.Group>
                  <Button variant="primary" onClick={handleSave} disabled={isSaving}>
                    {isSaving ? "Saving..." : "Save Changes"}
                  </Button>
                </Form>
              </Card.Body>
            </Card>
          ) : (
            <>
              <Card className="shadow-sm mb-4">
                <Card.Body>
                  <h5 className="mb-3">Account Information</h5>
                  <div className="mb-2 d-flex align-items-center gap-2">
                    <User size={18} className="text-muted" />
                    <strong>Name:</strong> {user?.name}
                  </div>
                  <div className="mb-2 d-flex align-items-center gap-2">
                    <Mail size={18} className="text-muted" />
                    <strong>Email:</strong> {user?.email}
                  </div>
                  <div className="mb-2 d-flex align-items-center gap-2">
                    <Calendar size={18} className="text-muted" />
                    <strong>Joined:</strong>{" "}
                    {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : "Recently"}
                  </div>
                  {user?.bio && (
                    <div className="mt-3">
                      <strong>Bio:</strong>
                      <p className="text-muted mt-1">{user.bio}</p>
                    </div>
                  )}
                </Card.Body>
              </Card>

              <Card className="shadow-sm">
                <Card.Body>
                  <h5 className="mb-3">Statistics</h5>
                  <Row>
                    <Col md={6}>
                      <div className="mb-3 d-flex align-items-center gap-2">
                        <Award size={18} className="text-primary" />
                        <div>
                          <small className="text-muted d-block">Total Tasks</small>
                          <strong>{stats.totalTasks}</strong>
                        </div>
                      </div>
                    </Col>
                    <Col md={6}>
                      <div className="mb-3 d-flex align-items-center gap-2">
                        <CheckCircle size={18} className="text-success" />
                        <div>
                          <small className="text-muted d-block">Completed</small>
                          <strong>{stats.completedTasks}</strong>
                        </div>
                      </div>
                    </Col>
                    <Col md={6}>
                      <div className="mb-3 d-flex align-items-center gap-2">
                        <Shield size={18} className="text-info" />
                        <div>
                          <small className="text-muted d-block">On-Time Rate</small>
                          <strong>
                            {stats.totalTasks > 0
                              ? Math.round((stats.onTimeRate / stats.totalTasks) * 100)
                              : 0}
                            %
                          </strong>
                        </div>
                      </div>
                    </Col>
                    <Col md={6}>
                      <div className="mb-3 d-flex align-items-center gap-2">
                        <AlertTriangle size={18} className="text-danger" />
                        <div>
                          <small className="text-muted d-block">High Risk Tasks</small>
                          <strong>{stats.highRiskTasks}</strong>
                        </div>
                      </div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            </>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default Profile;
