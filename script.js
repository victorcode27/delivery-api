// Updated script.js

// Example of relative fetch calls

fetch('/api/resource')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));

// Further logic based on relative paths would be added here