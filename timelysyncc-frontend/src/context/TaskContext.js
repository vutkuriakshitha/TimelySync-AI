// src/context/TaskContext.js
import React, {
  createContext,
  useState,
  useEffect,
  useContext,
  useCallback,
} from "react";
import toast from "react-hot-toast";
import taskService from "../services/taskService";
import aiService from "../services/aiService";
import { AuthContext } from "./AuthContext";

export const TaskContext = createContext();

const DASHBOARD_POLL_MS = Number(process.env.REACT_APP_DASHBOARD_POLL_MS) || 60000;

export const TaskProvider = ({ children }) => {
  const { user } = useContext(AuthContext);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [failurePredictions, setFailurePredictions] = useState([]);

  const loadTasks = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await taskService.getAllTasks();
      setTasks(response.data || []);
    } catch (error) {
      console.error("Error loading tasks:", error);
      toast.error("Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }, [user]);

  const loadFailurePredictions = useCallback(async () => {
    if (!user) return;
    try {
      const response = await aiService.getFailurePredictions();
      setFailurePredictions(response.data || []);
    } catch (error) {
      console.error("Error loading predictions:", error);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      loadTasks();
      loadFailurePredictions();
    } else {
      setTasks([]);
      setFailurePredictions([]);
      setLoading(false);
    }
  }, [user, loadTasks, loadFailurePredictions]);

  // Silent background refresh so task state stays close to real-time without
  // requiring the user to manually reload the page.
  useEffect(() => {
    if (!user) return undefined;
    const interval = setInterval(() => {
      loadTasks();
      loadFailurePredictions();
    }, DASHBOARD_POLL_MS);
    return () => clearInterval(interval);
  }, [user, loadTasks, loadFailurePredictions]);

  const createTask = async (taskData) => {
    try {
      const response = await taskService.createTask(taskData);
      const newTask = response.data;
      setTasks((prev) => [newTask, ...prev]);
      toast.success("Task created successfully!");
      return { success: true, task: newTask };
    } catch (error) {
      console.error("Error creating task:", error);
      const message = error.response?.data?.message || "Failed to create task";
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const updateTask = async (taskId, updates) => {
    try {
      const response = await taskService.updateTask(taskId, updates);
      const updatedTask = response.data;
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task)),
      );
      toast.success("Task updated!");
      return updatedTask;
    } catch (error) {
      console.error("Error updating task:", error);
      toast.error(error.response?.data?.message || "Failed to update task");
      throw error;
    }
  };

  const completeTask = async (taskId, proofFile) => {
    try {
      const response = await taskService.completeTask(taskId, proofFile);
      const completedTask = response.data;
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? completedTask : task)),
      );
      toast.success("Task completed! 🎉");
      return completedTask;
    } catch (error) {
      console.error("Error completing task:", error);
      toast.error(error.response?.data?.message || "Failed to complete task");
      throw error;
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await taskService.deleteTask(taskId);
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
      toast.success("Task deleted");
    } catch (error) {
      console.error("Error deleting task:", error);
      toast.error("Failed to delete task");
    }
  };

  const toggleSubtask = async (taskId, subtaskId) => {
    try {
      const response = await taskService.toggleSubtask(taskId, subtaskId);
      const updatedTask = response.data;
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task)),
      );
      return updatedTask;
    } catch (error) {
      console.error("Error updating subtask:", error);
      toast.error("Failed to update subtask");
      throw error;
    }
  };

  const addSubtask = async (taskId, subtask) => {
    try {
      const response = await taskService.addSubtask(taskId, subtask);
      const updatedTask = response.data;
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task)),
      );
      return updatedTask;
    } catch (error) {
      console.error("Error adding subtask:", error);
      toast.error("Failed to add subtask");
      throw error;
    }
  };

  const getTaskById = (taskId) => tasks.find((task) => task.id === taskId);

  const getActiveTasks = () => tasks.filter((task) => task.status === "ACTIVE");

  const getHighRiskTasks = () =>
    tasks.filter(
      (task) =>
        task.riskAnalysis?.riskLevel === "CRITICAL" && task.status === "ACTIVE",
    );

  const getOverdueTasks = () => {
    const now = new Date();
    return tasks.filter(
      (task) =>
        task.status === "ACTIVE" &&
        task.dueDate &&
        new Date(task.dueDate) < now,
    );
  };

  const getCompletedTasks = () => tasks.filter((task) => task.status === "COMPLETED");

  const getTasksByCategory = (category) =>
    tasks.filter((task) => task.category === category);

  const getTodayTasks = () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    return tasks.filter((task) => {
      if (!task.dueDate || task.status !== "ACTIVE") return false;
      const dueDate = new Date(task.dueDate);
      return dueDate >= today && dueDate < tomorrow;
    });
  };

  const getUpcomingTasks = (days = 7) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const futureDate = new Date(today);
    futureDate.setDate(today.getDate() + days);

    return tasks.filter((task) => {
      if (!task.dueDate || task.status !== "ACTIVE") return false;
      const dueDate = new Date(task.dueDate);
      return dueDate >= today && dueDate <= futureDate;
    });
  };

  const stats = {
    active: tasks.filter((t) => t.status === "ACTIVE").length,
    completed: tasks.filter((t) => t.status === "COMPLETED").length,
    overdue: getOverdueTasks().length,
  };

  return (
    <TaskContext.Provider
      value={{
        tasks,
        stats,
        loading,
        failurePredictions,
        loadTasks,
        loadFailurePredictions,
        createTask,
        updateTask,
        completeTask,
        deleteTask,
        toggleSubtask,
        addSubtask,
        getTaskById,
        getActiveTasks,
        getHighRiskTasks,
        getOverdueTasks,
        getCompletedTasks,
        getTodayTasks,
        getUpcomingTasks,
        getTasksByCategory,
      }}
    >
      {children}
    </TaskContext.Provider>
  );
};
