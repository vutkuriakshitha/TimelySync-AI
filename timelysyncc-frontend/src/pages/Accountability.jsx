import React, { useEffect, useState } from "react";
import {
  Container,
  Row,
  Col,
  Card,
  Table,
  Badge,
  ProgressBar,
  Spinner,
} from "react-bootstrap";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
} from "recharts";
import analyticsService from "../services/analyticsService";

const COLORS = ["#0d6efd", "#198754", "#ffc107", "#dc3545", "#6f42c1"];

const CATEGORY_LABELS = {
  ACADEMIC: "Academic",
  OPPORTUNITY: "Opportunities",
  PERSONAL_GOAL: "Personal",
  EVENT: "Events",
};

const Accountability = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoading(true);
        const response = await analyticsService.getAnalytics();
        setAnalytics(response.data);
        setError("");
      } catch (err) {
        console.error("Error loading analytics:", err);
        setError("Failed to load analytics. Please try again later.");
      } finally {
        setLoading(false);
      }
    };
    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3 text-muted">Loading your analytics...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5 text-center">
        <p className="text-danger">{error}</p>
      </Container>
    );
  }

  const weeklyCompletion = (analytics?.weeklyCompletion || []).map((entry) => ({
    name: entry.weekLabel,
    tasks: entry.completed,
  }));

  const categoryData = (analytics?.categoryBreakdown || []).map((entry) => ({
    name: CATEGORY_LABELS[entry.category] || entry.category,
    value: entry.count,
  }));

  const categoryPerformance = analytics?.categoryPerformance || [];

  return (
    <Container fluid className="p-4">
      <h2 className="mb-4">Accountability & Analytics</h2>

      {/* Summary Cards */}
      <Row className="mb-4 g-3">
        <Col md={3}>
          <Card className="shadow-sm border-0 bg-primary text-white">
            <Card.Body>
              <h6>Compliance Score</h6>
              <h2>{Math.round(analytics?.complianceScore || 0)}%</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="shadow-sm border-0 bg-success text-white">
            <Card.Body>
              <h6>Completed Tasks</h6>
              <h2>{analytics?.completedTasks || 0}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="shadow-sm border-0 bg-danger text-white">
            <Card.Body>
              <h6>Overdue Tasks</h6>
              <h2>{analytics?.overdueTasks || 0}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="shadow-sm border-0 bg-warning text-white">
            <Card.Body>
              <h6>Active Tasks</h6>
              <h2>{analytics?.activeTasks || 0}</h2>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row className="mb-4 g-3">
        <Col md={8}>
          <Card className="shadow-sm">
            <Card.Body>
              <h5 className="card-title">Weekly Task Completion</h5>
              {weeklyCompletion.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={weeklyCompletion}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="tasks" fill="#0d6efd" name="Completed" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-muted text-center py-5 mb-0">
                  No completion data yet - finish some tasks to see your trend.
                </p>
              )}
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="shadow-sm h-100">
            <Card.Body>
              <h5 className="card-title">Tasks by Category</h5>
              {categoryData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => entry.name}
                      outerRadius={80}
                      dataKey="value"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-muted text-center py-5 mb-0">No tasks yet.</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Category Performance Table */}
      <Card className="shadow-sm">
        <Card.Body>
          <h5 className="card-title mb-3">Category Performance</h5>
          {categoryPerformance.length > 0 ? (
            <Table striped hover responsive>
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Total Tasks</th>
                  <th>Completion Rate</th>
                  <th>On-Time Rate</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {categoryPerformance.map((cat, index) => (
                  <tr key={index}>
                    <td>{CATEGORY_LABELS[cat.category] || cat.category}</td>
                    <td>{cat.totalTasks}</td>
                    <td style={{ width: "200px" }}>
                      <ProgressBar
                        now={cat.completionRate}
                        label={`${Math.round(cat.completionRate)}%`}
                        variant={cat.completionRate >= 80 ? "success" : cat.completionRate >= 50 ? "warning" : "danger"}
                      />
                    </td>
                    <td>{Math.round(cat.onTimeRate)}%</td>
                    <td>
                      <Badge
                        bg={cat.completionRate >= 80 ? "success" : cat.completionRate >= 50 ? "warning" : "danger"}
                      >
                        {cat.completionRate >= 80 ? "Strong" : cat.completionRate >= 50 ? "Average" : "Weak"}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          ) : (
            <p className="text-muted text-center mb-0">
              No tasks yet - create tasks in different categories to see performance breakdowns.
            </p>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Accountability;
