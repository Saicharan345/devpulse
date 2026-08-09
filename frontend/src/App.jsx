import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "https://api-2c0c-8000.prg1.zerops.app";

function App() {
  const [monitors, setMonitors] = useState([]);
  const [incidents, setIncidents] = useState([]);

  const [monitorName, setMonitorName] = useState("");
  const [monitorUrl, setMonitorUrl] = useState("");
  const [isAdding, setIsAdding] = useState(false);

  useEffect(() => {
    fetchMonitors();
    fetchIncidents();
  }, []);

  async function fetchMonitors() {
    try {
      const response = await fetch(`${API_URL}/monitors/`);

      if (!response.ok) {
        throw new Error("Failed to fetch monitors");
      }

      const data = await response.json();
      setMonitors(data);
    } catch (error) {
      console.error("Failed to fetch monitors:", error);
    }
  }

  async function fetchIncidents() {
    try {
      const response = await fetch(`${API_URL}/incidents/`);

      if (!response.ok) {
        throw new Error("Failed to fetch incidents");
      }

      const data = await response.json();
      setIncidents(data);
    } catch (error) {
      console.error("Failed to fetch incidents:", error);
    }
  }

  async function refreshDashboard() {
    await Promise.all([
      fetchMonitors(),
      fetchIncidents(),
    ]);
  }

  async function addMonitor(event) {
    event.preventDefault();

    if (!monitorName.trim() || !monitorUrl.trim()) {
      alert("Please enter both monitor name and URL.");
      return;
    }

    setIsAdding(true);

    try {
      const response = await fetch(`${API_URL}/monitors/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: monitorName.trim(),
          url: monitorUrl.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        console.error("Backend error:", errorData);

        throw new Error("Failed to create monitor");
      }

      setMonitorName("");
      setMonitorUrl("");

      await fetchMonitors();

      alert("Monitor added successfully!");
    } catch (error) {
      console.error("Failed to add monitor:", error);
      alert(
        "Failed to add monitor. Please check the URL and try again."
      );
    } finally {
      setIsAdding(false);
    }
  }

  const upCount = monitors.filter(
    (monitor) => monitor.status === "up"
  ).length;

  const downCount = monitors.filter(
    (monitor) => monitor.status === "down"
  ).length;

  const openIncidents = incidents.filter(
    (incident) => incident.status === "open"
  ).length;

  return (
    <div className="app">

      {/* HEADER */}
      <header className="header">
        <div>
          <h1>DevPulse</h1>
          <p>Application Monitoring Dashboard</p>
        </div>

        <button
          className="refresh-button"
          onClick={refreshDashboard}
        >
          Refresh
        </button>
      </header>


      {/* ADD MONITOR */}
      <section className="add-monitor">
        <div className="section-heading">
          <div>
            <h2>Add Monitor</h2>
            <p>
              Start monitoring a website or API endpoint.
            </p>
          </div>
        </div>

        <form onSubmit={addMonitor}>
          <div className="form-group">
            <label htmlFor="monitor-name">
              Monitor Name
            </label>

            <input
              id="monitor-name"
              type="text"
              placeholder="e.g. My Website"
              value={monitorName}
              onChange={(event) =>
                setMonitorName(event.target.value)
              }
            />
          </div>

          <div className="form-group">
            <label htmlFor="monitor-url">
              Website URL
            </label>

            <input
              id="monitor-url"
              type="url"
              placeholder="https://example.com"
              value={monitorUrl}
              onChange={(event) =>
                setMonitorUrl(event.target.value)
              }
            />
          </div>

          <button
            className="add-button"
            type="submit"
            disabled={isAdding}
          >
            {isAdding ? "Adding..." : "+ Add Monitor"}
          </button>
        </form>
      </section>


      {/* STATISTICS */}
      <section className="stats">

        <div className="stat-card">
          <div className="stat-icon green">
            🟢
          </div>

          <div>
            <h2>{upCount}</h2>
            <p>UP</p>
          </div>
        </div>


        <div className="stat-card">
          <div className="stat-icon red">
            🔴
          </div>

          <div>
            <h2>{downCount}</h2>
            <p>DOWN</p>
          </div>
        </div>


        <div className="stat-card">
          <div className="stat-icon orange">
            🚨
          </div>

          <div>
            <h2>{openIncidents}</h2>
            <p>OPEN INCIDENTS</p>
          </div>
        </div>

      </section>


      {/* MONITORS */}
      <section className="section">

        <div className="section-heading">
          <div>
            <h2>Monitors</h2>
            <p>
              Websites and services currently being monitored.
            </p>
          </div>

          <span className="count-badge">
            {monitors.length} total
          </span>
        </div>


        {monitors.length === 0 ? (

          <div className="empty-state">
            <h3>No monitors yet</h3>
            <p>
              Add your first website above to start monitoring.
            </p>
          </div>

        ) : (

          <div className="monitor-list">

            {monitors.map((monitor) => (

              <div
                className="monitor-card"
                key={monitor.id}
              >

                <div className="monitor-info">

                  <div className="monitor-title">

                    <span
                      className={
                        monitor.status === "up"
                          ? "status-dot up"
                          : "status-dot down"
                      }
                    />

                    <h3>{monitor.name}</h3>

                  </div>

                  <a
                    href={monitor.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="monitor-url"
                  >
                    {monitor.url}
                  </a>

                </div>


                <div className="monitor-status">

                  <strong
                    className={
                      monitor.status === "up"
                        ? "status-up"
                        : "status-down"
                    }
                  >
                    {monitor.status.toUpperCase()}
                  </strong>

                  <span>
                    {monitor.response_time !== null
                      ? `${monitor.response_time} ms`
                      : "No response"}
                  </span>

                </div>

              </div>

            ))}

          </div>

        )}

      </section>


      {/* INCIDENTS */}
      <section className="section">

        <div className="section-heading">
          <div>
            <h2>Recent Incidents</h2>
            <p>
              Problems detected by DevPulse.
            </p>
          </div>

          <span className="count-badge">
            {incidents.length} total
          </span>
        </div>


        {incidents.length === 0 ? (

          <div className="empty-state">
            <h3>No incidents</h3>
            <p>
              Everything looks healthy.
            </p>
          </div>

        ) : (

          <div className="incident-list">

            {incidents.map((incident) => (

              <div
                className="incident-card"
                key={incident.id}
              >

                <div className="incident-info">

                  <h3>
                    Incident #{incident.id}
                  </h3>

                  <p>
                    {incident.error_message}
                  </p>

                  <small>
                    Started:{" "}
                    {new Date(
                      incident.started_at
                    ).toLocaleString()}
                  </small>

                  {incident.resolved_at && (
                    <small>
                      Resolved:{" "}
                      {new Date(
                        incident.resolved_at
                      ).toLocaleString()}
                    </small>
                  )}

                </div>


                <strong
                  className={
                    incident.status === "open"
                      ? "incident-open"
                      : "incident-resolved"
                  }
                >
                  {incident.status.toUpperCase()}
                </strong>

              </div>

            ))}

          </div>

        )}

      </section>

    </div>
  );
}

export default App;