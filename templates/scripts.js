document.addEventListener("DOMContentLoaded", () => {
  const deviceInput = document.getElementById("deviceFilter");
  const timestampInput = document.getElementById("timestampFilter");
  const fileEntries = document.querySelectorAll(".file-entry");

  function filterFiles() {
    const device = deviceInput.value.toLowerCase();
    const timestamp = timestampInput.value.toLowerCase();

    fileEntries.forEach(entry => {
      const entryDevice = entry.dataset.device?.toLowerCase() || "";
      const entryTimestamp = entry.dataset.timestamp?.toLowerCase() || "";
      const matchesDevice = entryDevice.includes(device);
      const matchesTime = entryTimestamp.includes(timestamp);

      if (matchesDevice && matchesTime) {
        entry.style.display = "flex";
      } else {
        entry.style.display = "none";
      }
    });
  }

  deviceInput.addEventListener("input", filterFiles);
  timestampInput.addEventListener("input", filterFiles);
});
