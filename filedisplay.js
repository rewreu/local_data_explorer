// Define the URL of the Flask web service
var url = "http://localhost:5000";

// Function to get a list of subfolders from the Flask web service
function getSubfolders() {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            var subfolders = document.getElementById("subfolders");
            subfolders.innerHTML = "";
            for (var i = 0; i < data.length; i++) {
                var option = document.createElement("option");
                option.value = data[i];
                option.text = data[i];
                subfolders.add(option);
            }
        });
}

// Function to get a list of CSV files for a selected subfolder from the Flask web service
function getCsvFiles() {
    var subfolder = document.getElementById("subfolders").value;
    var csvFiles = document.getElementById("csvFiles");
    csvFiles.innerHTML = "";
    fetch(url + "/csv_files?subfolder=" + subfolder)
        .then(response => response.json())
        .then(data => {
            for (var i = 0; i < data.length; i++) {
                var option = document.createElement("option");
                option.value = data[i];
                option.text = data[i];
                csvFiles.add(option);
            }
        });
}

// Function to execute an SQL query on a selected CSV file using the Flask web service
function executeQuery() {
    var subfolder = document.getElementById("subfolders").value;
    var csvFile = document.getElementById("csvFiles").value;
    var query = document.getElementById("query").value;
    var resultTable = document.getElementById("resultTable");
    resultTable.innerHTML = "";
    fetch(url + "/query?subfolder=" + subfolder + "&csv_file=" + csvFile + "&query=" + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => {
            var table = document.createElement("table");
            var headerRow = table.insertRow();
            for (var key in data[0]) {
                var headerCell = document.createElement("th");
                headerCell.innerHTML = key;
                headerRow.appendChild(headerCell);
            }
            for (var i = 0; i < data.length; i++) {
                var row = table.insertRow();
                for (var key in data[i]) {
                    var cell = row.insertCell();
                    cell.innerHTML = data[i][key];
                }
            }
            resultTable.appendChild(table);
        });
}
