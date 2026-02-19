(function() {
    // Sample content of the script.js

    // Fetch call using relative paths
    fetch('/api/some-endpoint')
        .then(response => response.json())
        .then(data => {
            console.log(data);
        })
        .catch(error => console.error('Error:', error));

    // Other code...

})();