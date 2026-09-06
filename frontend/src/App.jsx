import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/disagreements/";

const REASON_LABELS = {
  all: "All disagreements",
  missing_in_system_b: "Missing in System B",
  orphan_system_b: "Orphan in System B",
  duplicate_in_system_b: "Duplicate in System B",
  value_mismatch: "Value mismatch",
};

function App() {
  const [disagreements, setDisagreements] = useState([]);
  const [reason, setReason] = useState("all");
  const [sortDirection, setSortDirection] = useState("none");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(API_URL)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch disagreements");
        }

        return response.json();
      })
      .then((data) => {
        setDisagreements(data.results);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const filteredDisagreements = useMemo(() => {
    let result = [...disagreements];

    if (reason !== "all") {
      result = result.filter(
        (item) => item.reason === reason
      );
    }

    if (sortDirection !== "none") {
      result.sort((a, b) => {
        const aValue = parseFloat(
          String(a.system_a_value ?? "")
            .replace(/,/g, "")
        ) || 0;

        const bValue = parseFloat(
          String(b.system_a_value ?? "")
            .replace(/,/g, "")
        ) || 0;

        return sortDirection === "asc"
          ? aValue - bValue
          : bValue - aValue;
      });
    }

    return result;
  }, [disagreements, reason, sortDirection]);

  const handleSort = () => {
    if (sortDirection === "none") {
      setSortDirection("asc");
    } else if (sortDirection === "asc") {
      setSortDirection("desc");
    } else {
      setSortDirection("none");
    }
  };

  const formatReason = (value) => {
    return REASON_LABELS[value] || value;
  };

  const formatValue = (value) => {
    if (value === null || value === undefined) {
      return "—";
    }

    if (Array.isArray(value)) {
      return value.join(", ");
    }

    if (typeof value === "object") {
      return JSON.stringify(value);
    }

    return String(value);
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>ADOSX Reconciliation</h1>
          <p>
            Compare System A and System B records
          </p>
        </div>

        <div className="summary">
  <span>
    Total disagreements
  </span>

  <strong>
    {disagreements.length}
  </strong>

  {reason !== "all" && (
    <small>
      Showing {filteredDisagreements.length}
    </small>
  )}
</div>
      </header>

      <main className="container">
        <section className="controls">
          <div className="filter-group">
            <label htmlFor="reason">
              Filter by reason
            </label>

            <select
              id="reason"
              value={reason}
              onChange={(event) =>
                setReason(event.target.value)
              }
            >
              <option value="all">
                All disagreements
              </option>

              <option value="missing_in_system_b">
                Missing in System B
              </option>

              <option value="orphan_system_b">
                Orphan in System B
              </option>

              <option value="duplicate_in_system_b">
                Duplicate in System B
              </option>

              <option value="value_mismatch">
                Value mismatch
              </option>
            </select>
          </div>

          <button
            className="sort-button"
            onClick={handleSort}
          >
            Sort by System A value
            {sortDirection === "asc" && " ↑"}
            {sortDirection === "desc" && " ↓"}
          </button>
        </section>

        {loading && (
          <div className="message">
            Loading disagreements...
          </div>
        )}

        {error && (
          <div className="message error">
            {error}
          </div>
        )}

        {!loading && !error && (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Reason</th>
                  <th>Record ID</th>
                  <th>Field</th>
                  <th>System A</th>
                  <th>System B</th>
                  <th>Location</th>
                  <th>Organization</th>
                </tr>
              </thead>

              <tbody>
                {filteredDisagreements.length === 0 ? (
                  <tr>
                    <td
                      colSpan="7"
                      className="empty"
                    >
                      No disagreements found.
                    </td>
                  </tr>
                ) : (
                  filteredDisagreements.map(
                    (item, index) => (
                      <tr key={`${item.record_id}-${index}`}>
                        <td>
                          <span
                            className={`reason ${item.reason}`}
                          >
                            {formatReason(item.reason)}
                          </span>
                        </td>

                        <td>
                          {item.record_id || "—"}
                        </td>

                        <td>
                          {item.field || "—"}
                        </td>

                        <td className="value">
                          {formatValue(
                            item.system_a_value
                          )}
                        </td>

                        <td className="value">
                          {formatValue(
                            item.system_b_value
                          )}
                        </td>

                        <td>
                          {item.location || "—"}
                        </td>

                        <td>
                          {item.organization || "—"}
                        </td>
                      </tr>
                    )
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;