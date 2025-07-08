// Initialize Chart.js
const ctx = document.getElementById("ear-chart").getContext("2d");
const earChart = new Chart(ctx, {
  type: "line",
  data: {
    datasets: [
      {
        label: "EAR",
        data: [],
        borderColor: "#4ade80",
        backgroundColor: "rgba(74, 222, 128, 0.1)",
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.1,
        fill: true,
      },
      {
        label: "Threshold",
        data: [],
        borderColor: "#f87171",
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: "linear",
        position: "bottom",
        min: 0,
        max: 100,
        title: {
          display: true,
          text: "Frames",
        },
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },
      },
      y: {
        min: 0,
        max: 0.4,
        title: {
          display: true,
          text: "EAR Value",
        },
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        enabled: false,
      },
    },
    animation: false,
  },
});

// DOM Elements
const toggleBtn = document.getElementById("toggle-btn");

// Function to update button state
function updateButtonState(isActive) {
  if (isActive) {
    toggleBtn.textContent = "Stop Detection";
    toggleBtn.classList.remove("start-btn");
    toggleBtn.classList.add("stop-btn");
  } else {
    toggleBtn.textContent = "Start Detection";
    toggleBtn.classList.remove("stop-btn");
    toggleBtn.classList.add("start-btn");
  }
}

// Toggle detection
function toggleDetection() {
  fetch("/toggle_detection", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      updateButtonState(data.detection_active);
    })
    .catch((error) => console.error("Error toggling detection:", error));
}

// Function to update the chart
function updateChart(data) {
  const earData = data.ear_values.map((value, index) => ({
    x: data.timestamps[index],
    y: value,
  }));

  // Calculate threshold line
  const thresholdData = [];
  if (earData.length > 0) {
    const minX = Math.max(0, earData[0].x);
    const maxX = earData[earData.length - 1].x;
    thresholdData.push({ x: minX, y: data.threshold });
    thresholdData.push({ x: maxX, y: data.threshold });
  }

  // Update chart datasets
  earChart.data.datasets[0].data = earData;
  earChart.data.datasets[1].data = thresholdData;

  // Update x-axis scale
  if (earData.length > 0) {
    const maxX = earData[earData.length - 1].x;
    earChart.options.scales.x.min = Math.max(0, maxX - 100);
    earChart.options.scales.x.max = maxX;
  }

  earChart.update();
}

// Function to update status display
function updateStatus(data) {
  document.getElementById("current-ear").textContent =
    data.current_ear.toFixed(2);
  document.getElementById("status-text").textContent = data.status;

  // Update status color
  const statusElem = document.getElementById("status-text");
  statusElem.classList.remove("status-ready", "status-awake", "status-drowsy");

  if (data.status === "READY") {
    statusElem.classList.add("status-ready");
  } else if (data.status === "AWAKE") {
    statusElem.classList.add("status-awake");
  } else if (data.status === "DROWSY") {
    statusElem.classList.add("status-drowsy");
  } else {
    statusElem.classList.add("status-ready");
  }

  // Show/hide alert
  const alertBox = document.getElementById("alert-box");
  if (data.alert_active && data.detection_active) {
    alertBox.classList.add("active");
  } else {
    alertBox.classList.remove("active");
  }

  // Update button state based on detection status
  updateButtonState(data.detection_active);
}

// Fetch data from server periodically
function fetchData() {
  fetch("/data")
    .then((response) => response.json())
    .then((data) => {
      updateChart(data);
      updateStatus(data);
    })
    .catch((error) => console.error("Error fetching data:", error));
}

// Play alert sound
function playAlertSound() {
  const audio = new Audio(
    "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqMkJKTlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/"
  );
  audio.play();
}

// Check for alerts and play sound
let lastAlertState = false;
function checkForAlert() {
  fetch("/data")
    .then((response) => response.json())
    .then((data) => {
      if (data.alert_active && !lastAlertState && data.detection_active) {
        playAlertSound();
      }
      lastAlertState = data.alert_active;
    });
}

// Initialize and start periodic updates
setInterval(fetchData, 100); // Update every 100ms
setInterval(checkForAlert, 500); // Check for alerts every 500ms

// Event listener for toggle button
toggleBtn.addEventListener("click", toggleDetection);

// Initialize button state
updateButtonState(false);
