import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";

const API = "https://smart-waste-api-do95.onrender.com";

const emptyForm = {
  bin_name: "",
  city: "Aschaffenburg",
  location: "",
  area: "",
  fill_level: 0,
  status: "Empty",
};

const normalizeBin = (bin) => {
  // Old city-based schema
  if (bin.city !== undefined && bin.fill_level !== undefined) {
    return bin;
  }

  // New sensor-style schema from deployed backend
  const fillLevel =
    bin.load_status === "full"
      ? 100
      : Math.max(0, Math.min(100, Math.round((bin.weight || 0) * 2)));

  const status =
    bin.alert || bin.gas_status?.status === "methane_detected"
      ? "Critical"
      : fillLevel >= 80
      ? "Full"
      : fillLevel >= 40
      ? "Half Full"
      : "Empty";

  return {
    id: bin.id,
    bin_name: `Bin ${bin.id}`,
    city: "Sensor Network",
    location: `Node ${bin.id}`,
    area:
      bin.gas_status?.status === "methane_detected"
        ? "Gas Alert Zone"
        : "General Zone",
    fill_level: fillLevel,
    status,
    last_updated: bin.last_updated,
    load_status: bin.load_status,
    gas_status: bin.gas_status,
    weight: bin.weight,
    alert: bin.alert,
    light_indicator: bin.light_indicator,
    buzzer: bin.buzzer,
  };
};

function App() {
  const [bins, setBins] = useState([]);
  const [cityFilter, setCityFilter] = useState("All");
  const [formData, setFormData] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [simulationMessage, setSimulationMessage] = useState("");
  const [activePage, setActivePage] = useState("Overview");

  const loadBins = async () => {
    try {
      const res = await axios.get(`${API}/bins/`);
      setBins((res.data || []).map(normalizeBin));
    } catch (error) {
      console.error("Error loading bins:", error);
    }
  };

  useEffect(() => {
    loadBins();
  }, []);

  const cities = useMemo(() => {
    const uniqueCities = [...new Set(bins.map((bin) => bin.city))];
    return ["All", ...uniqueCities];
  }, [bins]);

  const filteredBins = useMemo(() => {
    if (cityFilter === "All") return bins;
    return bins.filter((bin) => bin.city === cityFilter);
  }, [bins, cityFilter]);
  const optimizedRoute = useMemo(() => {
    return [...filteredBins]
      .filter((bin) => bin.fill_level >= 60 || bin.status === "Critical")
      .sort((a, b) => b.fill_level - a.fill_level)
      .slice(0, 8);
  }, [filteredBins]);

  const totalBins = filteredBins.length;
  const criticalBins = filteredBins.filter(
    (bin) => bin.fill_level >= 80 || bin.status === "Critical"
  ).length;
  const mediumBins = filteredBins.filter(
    (bin) => bin.fill_level >= 40 && bin.fill_level < 80
  ).length;
  const lowBins = filteredBins.filter((bin) => bin.fill_level < 40).length;

  const coverageCities = useMemo(
    () => new Set(bins.map((bin) => bin.city)).size,
    [bins]
  );
  const citySummary = useMemo(() => {
    const summary = {};

    bins.forEach((bin) => {
      if (!summary[bin.city]) {
        summary[bin.city] = {
          total: 0,
          critical: 0,
          medium: 0,
          low: 0,
        };
      }

      summary[bin.city].total += 1;

      if (bin.fill_level >= 80 || bin.status === "Critical") {
        summary[bin.city].critical += 1;
      } else if (bin.fill_level >= 40) {
        summary[bin.city].medium += 1;
      } else {
        summary[bin.city].low += 1;
      }
    });

    return Object.entries(summary);
  }, [bins]);

  const getStatusFromFill = (fillLevel) => {
    if (fillLevel >= 80) return "Full";
    if (fillLevel >= 40) return "Half Full";
    return "Empty";
  };

  const getStatusClass = (fillLevel, status = "") => {
    if (status === "Critical") return "critical";
    if (fillLevel >= 80) return "critical";
    if (fillLevel >= 40) return "warning";
    return "safe";
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === "fill_level") {
      const fill = Number(value);
      setFormData({
        ...formData,
        fill_level: fill,
        status: getStatusFromFill(fill),
      });
      return;
    }

    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const resetForm = () => {
    setFormData(emptyForm);
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const payload = {
        ...formData,
        fill_level: Number(formData.fill_level),
        status: getStatusFromFill(Number(formData.fill_level)),
      };

      if (editingId) {
        await axios.put(`${API}/bins/${editingId}`, payload);
      } else {
        await axios.post(`${API}/bins/`, payload);
      }

      resetForm();
      loadBins();
      setActivePage("Bin Network Status");
    } catch (error) {
      console.error("Error saving bin:", error);
    }
  };

  const handleEdit = (bin) => {
    setFormData({
      bin_name: bin.bin_name,
      city: bin.city,
      location: bin.location,
      area: bin.area,
      fill_level: bin.fill_level,
      status: bin.status,
    });
    setEditingId(bin.id);
    setActivePage("Control Panel");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDelete = async (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this smart bin?"
    );

    if (!confirmed) return;

    try {
      await axios.delete(`${API}/bins/${id}`);
      loadBins();
    } catch (error) {
      console.error("Error deleting bin:", error);
    }
  };

  const handleCollected = async (bin) => {
    try {
      await axios.put(`${API}/bins/${bin.id}`, {
        bin_name: bin.bin_name,
        city: bin.city,
        location: bin.location,
        area: bin.area,
        fill_level: 0,
        status: "Empty",
      });
      loadBins();
    } catch (error) {
      console.error("Error marking bin as collected:", error);
    }
  };

  const runSimulation = async () => {
    try {
      const res = await axios.post(`${API}/bins/simulate`);
      setSimulationMessage(
        `${res.data.message} - ${res.data.updated_bins} bins updated`
      );
      loadBins();
    } catch (error) {
      console.error("Error running sensor simulation:", error);
    }
  };

  return (
    <div className="ops-shell">
      <aside className="ops-sidebar">
        <div>
          <div className="ops-brand">
            <div className="ops-logo">SW</div>
            <div>
              <div className="ops-title">Smart Waste</div>
              <div className="ops-subtitle">Operations Center</div>
            </div>
          </div>

          <div className="sidebar-nav">
            <button
              className={`nav-btn ${activePage === "Overview" ? "active" : ""}`}
              onClick={() => setActivePage("Overview")}
            >
              Overview
            </button>

            <button
              className={`nav-btn ${activePage === "Control Panel" ? "active" : ""}`}
              onClick={() => setActivePage("Control Panel")}
            >
              Control Panel
            </button>

            <button
              className={`nav-btn ${activePage === "Bin Network Status" ? "active" : ""}`}
              onClick={() => setActivePage("Bin Network Status")}
            >
              Bin Network Status
            </button>

            <button
              className={`nav-btn ${activePage === "Route Optimizer" ? "active" : ""}`}
              onClick={() => setActivePage("Route Optimizer")}
            >
              Route Optimizer
            </button>
          </div>

          <div className="sidebar-block">
            <div className="sidebar-label">System Status</div>
            <div className="status-chip online">Online</div>
          </div>

          <div className="sidebar-block">
            <div className="sidebar-label">Sensor Feed</div>
            <div className="status-chip active">Active</div>
          </div>

          <div className="sidebar-block">
            <div className="sidebar-label">Monitoring Region</div>
            <select
              className="sidebar-select"
              value={cityFilter}
              onChange={(e) => setCityFilter(e.target.value)}
            >
              {cities.map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>
          </div>

          <div className="sidebar-block">
            <div className="sidebar-label">Coverage</div>
            <div className="mini-metric">{coverageCities} Cities</div>
            <div className="mini-metric">{bins.length} Total Bins</div>
          </div>
        </div>
      </aside>

      <main className="ops-main">
        {activePage === "Overview" && (
          <>
            <section className="top-banner">
              <div>
                <p className="eyebrow">SMART CITY MONITORING</p>
                <h1>Waste Network Command Center</h1>
                <p className="banner-text">
                  Monitor fill levels, manage smart bins, trigger sensor
                  simulations, and detect critical collection zones across
                  multiple cities.
                </p>
              </div>

              <div className="banner-panel">
                <div className="banner-kpi">
                  <span>Selected Region</span>
                  <strong>{cityFilter}</strong>
                </div>
                <div className="banner-kpi">
                  <span>Critical Alerts</span>
                  <strong>{criticalBins}</strong>
                </div>
              </div>
            </section>

            <section className="metric-grid">
              <div className="metric-card">
                <span className="metric-label">Monitored Bins</span>
                <h3>{totalBins}</h3>
              </div>

              <div className="metric-card critical-card">
                <span className="metric-label">Critical Fill</span>
                <h3>{criticalBins}</h3>
              </div>

              <div className="metric-card warning-card">
                <span className="metric-label">Medium Load</span>
                <h3>{mediumBins}</h3>
              </div>

              <div className="metric-card safe-card">
                <span className="metric-label">Low Fill</span>
                <h3>{lowBins}</h3>
              </div>
            </section>
            <section className="ops-panel">
              <div className="panel-header">
                <h2>City Overview</h2>
                <span className="panel-badge">{coverageCities} Cities</span>
              </div>

              <div className="city-grid">
                {citySummary.map(([city, stats]) => (
                  <div className="city-card" key={city}>
                    <div className="city-card-header">
                      <h3>{city}</h3>
                      <span>{stats.total} bins</span>
                    </div>

                    <div className="city-stats">
                      <div className="city-stat critical-text">
                        Critical: {stats.critical}
                      </div>
                      <div className="city-stat warning-text">
                        Medium: {stats.medium}
                      </div>
                      <div className="city-stat safe-text">
                        Low: {stats.low}
                      </div>
                    </div>

                    <button
                      className="city-view-btn"
                      onClick={() => {
                        setCityFilter(city);
                        setActivePage("Bin Network Status");
                      }}
                    >
                      View Network
                    </button>
                  </div>
                ))}
              </div>
            </section>

            <section className="ops-panel">
              <div className="panel-header">
                <h2>Critical Alerts</h2>
                <span className="panel-badge">{criticalBins} Active</span>
              </div>

              {criticalBins > 0 ? (
                <div className="alert-list">
                  {filteredBins
                    .filter((bin) => bin.fill_level >= 80 || bin.status === "Critical")
                    .map((bin) => (
                      <div className="alert-item" key={bin.id}>
                        <div>
                          <strong>{bin.bin_name}</strong>
                          <p>
                            {bin.location}, {bin.city}
                            {bin.gas_status?.status === "methane_detected"
                              ? " • Methane detected"
                              : ""}
                          </p>
                        </div>
                        <div className="alert-fill">
                          {bin.gas_status?.status === "methane_detected"
                            ? "Gas Alert"
                            : `${bin.fill_level}%`}
                        </div>
                      </div>
                    ))}
                </div>
              ) : (
                <p className="empty-state">
                  No critical alerts for this region.
                </p>
              )}
            </section>
          </>
        )}

        {activePage === "Control Panel" && (
          <>
            <section className="ops-panel">
              <div className="panel-header">
                <h2>Simulation Control</h2>
                <span className="panel-badge">IoT Feed</span>
              </div>

              <button className="simulate-btn main-sim-btn" onClick={runSimulation}>
                Run Sensor Simulation
              </button>

              {simulationMessage && (
                <p className="simulation-message">{simulationMessage}</p>
              )}
            </section>

            <section className="ops-panel">
              <div className="panel-header">
                <h2>{editingId ? "Edit Smart Bin" : "Add New Smart Bin"}</h2>
                <span className="panel-badge">
                  {editingId ? "Editing Bin" : "Create Bin"}
                </span>
              </div>

              <form className="control-form" onSubmit={handleSubmit}>
                <input
                  type="text"
                  name="bin_name"
                  placeholder="Bin Name"
                  value={formData.bin_name}
                  onChange={handleChange}
                  required
                />

                <select
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                >
                  <option value="Aschaffenburg">Aschaffenburg</option>
                  <option value="Frankfurt">Frankfurt</option>
                  <option value="Dietzenbach">Dietzenbach</option>
                  <option value="Offenbach">Offenbach</option>
                  <option value="Darmstadt">Darmstadt</option>
                </select>

                <input
                  type="text"
                  name="location"
                  placeholder="Location"
                  value={formData.location}
                  onChange={handleChange}
                  required
                />

                <input
                  type="text"
                  name="area"
                  placeholder="Area"
                  value={formData.area}
                  onChange={handleChange}
                  required
                />

                <input
                  type="number"
                  name="fill_level"
                  min="0"
                  max="100"
                  placeholder="Fill Level"
                  value={formData.fill_level}
                  onChange={handleChange}
                  required
                />

                <input
                  type="text"
                  name="status"
                  value={formData.status}
                  readOnly
                  className="readonly-input"
                />

                <div className="form-actions">
                  <button type="submit" className="primary-btn">
                    {editingId ? "Update Bin" : "Add Bin"}
                  </button>

                  {editingId && (
                    <button
                      type="button"
                      className="secondary-btn"
                      onClick={resetForm}
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </form>
            </section>
          </>
        )}

        {activePage === "Bin Network Status" && (
          <section className="ops-panel table-panel">
            <div className="panel-header">
              <h2>Bin Network Status</h2>
              <span className="panel-badge">
                {cityFilter === "All" ? "All Cities" : cityFilter}
              </span>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Bin Name</th>
                    <th>City</th>
                    <th>Location</th>
                    <th>Area</th>
                    <th>Fill Level</th>
                    <th>Status</th>
                    <th>Last Updated</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredBins.length > 0 ? (
                    filteredBins.map((bin) => (
                      <tr key={bin.id}>
                        <td>{bin.id}</td>
                        <td>{bin.bin_name}</td>
                        <td>{bin.city}</td>
                        <td>{bin.location}</td>
                        <td>{bin.area}</td>
                        <td>
                          <div className="fill-cell">
                            <div className="fill-track">
                              <div
                                className={`fill-bar ${getStatusClass(
                                  bin.fill_level,
                                  bin.status
                                )}`}
                                style={{ width: `${bin.fill_level}%` }}
                              ></div>
                            </div>
                            <span>{bin.fill_level}%</span>
                          </div>
                        </td>
                        <td>
                          <span
                            className={`status ${getStatusClass(
                              bin.fill_level,
                              bin.status
                            )}`}
                          >
                            {bin.status}
                          </span>
                        </td>
                        <td>{new Date(bin.last_updated).toLocaleString()}</td>
                        <td>
                          <div className="action-buttons">
                            <button
                              className="collect-btn"
                              onClick={() => handleCollected(bin)}
                            >
                              Collected
                            </button>

                            <button
                              className="edit-btn"
                              onClick={() => handleEdit(bin)}
                            >
                              Edit
                            </button>

                            <button
                              className="delete-btn"
                              onClick={() => handleDelete(bin.id)}
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="9">No bins found for this city.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}
        {activePage === "Route Optimizer" && (
  <>
    <section className="ops-panel">
      <div className="panel-header">
        <h2>Collection Route Optimizer</h2>
        <span className="panel-badge">
          {cityFilter === "All" ? "All Cities" : cityFilter}
        </span>
      </div>

      <p className="route-intro">
        The system prioritizes bins with higher fill levels to support
        daily collection planning. Bins shown below should be collected first.
      </p>

      {optimizedRoute.length > 0 ? (
        <div className="route-list">
          {optimizedRoute.map((bin, index) => (
            <div className="route-card" key={bin.id}>

              <div className="route-rank">
                {index + 1}
              </div>

              <div className="route-info">
                <h3>{bin.bin_name}</h3>
                <p>
                  {bin.location}, {bin.city} • {bin.area}
                  {bin.gas_status?.status === "methane_detected"
                    ? " • Methane detected"
                    : ""}
                </p>
              </div>

              <div className="route-priority">
                <span>Priority</span>
                <strong>
                  {bin.gas_status?.status === "methane_detected"
                    ? "Gas Alert"
                    : `${bin.fill_level}%`}
                </strong>
              </div>

            </div>
          ))}
        </div>
      ) : (
        <p className="empty-state">
          No high-priority bins for this region right now.
        </p>
      )}
    </section>

    <section className="ops-panel">
      <div className="panel-header">
        <h2>Optimization Logic</h2>
        <span className="panel-badge">Current Rule</span>
      </div>

      <div className="logic-box">
        <p>Current prioritization is based on:</p>

        <ul>
          <li>Bins above 60% fill level</li>
          <li>Highest fill level first</li>
          <li>Top 8 bins shown for collection planning</li>
        </ul>

        <p>
          This can later be extended with truck capacity,
          route distance and city zone clustering.
        </p>
      </div>
    </section>
  </>
)}
      </main>
    </div>
  );
}

export default App;