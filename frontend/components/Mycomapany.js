"use client";
import { useState } from "react";

const Mycompany = () => {
  const [formData, setFormData] = useState({
    technicalCapability: "",
    pastExperience: "",
    certifications: "",
    teamAvailability: "",
    domainExperience: "",
    maxDuration: "",
    dealSizeRange: "",
    clientType: ""
  });

  // Handle input/select changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    const response = await fetch("http://localhost:8000/mycompanydata", {
      method: "POST",
      body: JSON.stringify(formData)
    });

    const result = await response.json();
    console.log(result);
  } catch (error) {
    console.error("Error:", error);
  }
};

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Bidding Company Profile</h2>

      <div style={styles.card}>
        <label style={styles.label}>1. Technical Capability Level</label>
        <select
          name="technicalCapability"
          value={formData.technicalCapability}
          onChange={handleChange}
          style={styles.input}
        >
          <option value="">Select</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
      </div>

      <div style={styles.card}>
        <label style={styles.label}>2. Past Project Experience (Years)</label>
        <input
          type="number"
          name="pastExperience"
          value={formData.pastExperience}
          onChange={handleChange}
          placeholder="e.g. 8"
          style={styles.input}
        />
      </div>

      <div style={styles.card}>
        <label style={styles.label}>3. Certifications Held</label>
        <input
          type="text"
          name="certifications"
          value={formData.certifications}
          onChange={handleChange}
          placeholder="ISO 9001, ISO 27001, HIPAA"
          style={styles.input}
        />
      </div>

      <div style={styles.card}>
        <label style={styles.label}>4. Team Availability (%)</label>
        <input
          type="number"
          name="teamAvailability"
          value={formData.teamAvailability}
          onChange={handleChange}
          placeholder="e.g. 70"
          style={styles.input}
        />
      </div>

      <div style={styles.card}>
        <label style={styles.label}>5. Domain Experience</label>
        <input
          type="text"
          name="domainExperience"
          value={formData.domainExperience}
          onChange={handleChange}
          placeholder="Healthcare IT, Government Systems"
          style={styles.input}
        />
      </div>

      <div style={styles.card}>
        <label style={styles.label}>6. Maximum Project Duration (Months)</label>
        <input
          type="number"
          name="maxDuration"
          value={formData.maxDuration}
          onChange={handleChange}
          placeholder="e.g. 18"
          style={styles.input}
        />
      </div>

      <div style={styles.card}>
        <label style={styles.label}>7. Preferred Deal Size Range</label>
        <input
          type="text"
          name="dealSizeRange"
          value={formData.dealSizeRange}
          onChange={handleChange}
          placeholder="2M – 25M"
          style={styles.input}
        />
      </div>

      <div style={styles.card}>
        <label style={styles.label}>8. Client Types Worked With</label>
        <select
          name="clientType"
          value={formData.clientType}
          onChange={handleChange}
          style={styles.input}
        >
          <option value="">Select</option>
          <option value="Government">Government</option>
          <option value="Private">Private</option>
          <option value="Both">Both</option>
        </select>
      </div>

      <button style={styles.button} onClick={handleSubmit}>
        Save Company Profile
      </button>
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