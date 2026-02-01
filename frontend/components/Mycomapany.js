const Mycompany = () => {
  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Bidding Company Profile</h2>

      {/* 1. Technical Requirements Match */}
      <div style={styles.card}>
        <label style={styles.label}>1. Technical Capability Level</label>
        <select style={styles.input}>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
      </div>

      {/* 2. Past Project Similarity */}
      <div style={styles.card}>
        <label style={styles.label}>2. Past Project Experience (Years)</label>
        <input type="number" placeholder="e.g. 8" style={styles.input} />
      </div>

      {/* 3. Certifications Match */}
      <div style={styles.card}>
        <label style={styles.label}>3. Certifications Held</label>
        <input
          type="text"
          placeholder="ISO 9001, ISO 27001, HIPAA"
          style={styles.input}
        />
      </div>

      {/* 4. Team Availability */}
      <div style={styles.card}>
        <label style={styles.label}>4. Team Availability (%)</label>
        <input type="number" placeholder="e.g. 70" style={styles.input} />
      </div>

      {/* 5. Domain Experience */}
      <div style={styles.card}>
        <label style={styles.label}>5. Domain Experience</label>
        <input
          type="text"
          placeholder="Healthcare IT, Government Systems"
          style={styles.input}
        />
      </div>

      {/* 6. Timeline Feasibility */}
      <div style={styles.card}>
        <label style={styles.label}>6. Maximum Project Duration (Months)</label>
        <input type="number" placeholder="e.g. 18" style={styles.input} />
      </div>

      {/* 7. Deal Size Fit */}
      <div style={styles.card}>
        <label style={styles.label}>7. Preferred Deal Size Range</label>
        <input
          type="text"
          placeholder="2M – 25M"
          style={styles.input}
        />
      </div>

      {/* 8. Client Type Familiarity */}
      <div style={styles.card}>
        <label style={styles.label}>8. Client Types Worked With</label>
        <select style={styles.input}>
          <option>Government</option>
          <option>Private</option>
          <option>Both</option>
        </select>
      </div>

      <button style={styles.button}>Save Company Profile</button>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "700px",
    margin: "40px auto",
    padding: "30px",
    backgroundColor: "#f9f9f9",
    borderRadius: "12px",
    fontFamily: "Arial, sans-serif"
  },
  title: {
    textAlign: "center",
    marginBottom: "25px",
    color: "#333"
  },
  card: {
    marginBottom: "18px"
  },
  label: {
    display: "block",
    marginBottom: "6px",
    fontWeight: "600",
    color: "#444"
  },
  input: {
    width: "100%",
    padding: "10px",
    borderRadius: "6px",
    border: "1px solid #ccc"
  },
  button: {
    width: "100%",
    padding: "12px",
    marginTop: "20px",
    backgroundColor: "#2563eb",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "16px",
    cursor: "pointer"
  }
};

export default Mycompany;