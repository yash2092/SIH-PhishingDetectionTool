import React, { useState } from 'react';
import axios from 'axios'; // No need for axios for mock response

function BulkQuery() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
  };

  const runBulkQuery = () => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const fileContent = event.target.result;
        const urlsArray = fileContent.split('\n').map((url) => url.trim());
        console.log(typeof(urlsArray))
        axios
      .post("http://127.0.0.1:5000/scanUrls", { urls: urlsArray }, { headers: { 'Content-Type': 'application/json' } })
      .then((response) => {
        console.log('Response:', typeof(response.data['Result']));
        // Uncomment the line below when using actual response
        setResults(response.data['Result']);
        downloadResultsFile(response.data['Result']);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
              };

      reader.readAsText(file);
    }
  };

  const downloadResultsFile = (data) => {
    // Check if data is an array and not empty
    if (Array.isArray(data) && data.length > 0) {
        console.log(data)
      const content = data.map(({ url, status }) => `${url},${status}`).join('\n');
      const blob = new Blob([content], { type: 'csv' });
      const url = URL.createObjectURL(blob);

      // Create a link and trigger the download
      const link = document.createElement('a');
      link.href = url;
      link.download = 'bulk_query_results.txt';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  // Axios-related code remains unchanged
  // Replace 'YOUR_API_ENDPOINT' with the actual API endpoint
  const API_ENDPOINT = 'http://127.0.0.1:5000/scanUrls';

  // Uncomment the axios code when using the actual API endpoint

  const sendBulkRequest = () => {
    console.log("hi")
    let urlsArray = runBulkQuery()
    
  };

  return (
    <div style={{ marginLeft: '15vw', textAlign:"center",marginTop: '10vw', marginBottom: '22vw', width: '70vw', padding: '4vw' }}>
      <h2 style={{color:"#164863"}}>Bulk Query - Query Multiple URLs at once to get results</h2>
      <p style={{fontWeight: '30px', fontSize: '20px', color: '#427D9D'}}>Select a text file with URLs to check for phishing</p>
      <br/><br></br>
      <input id="bulk" hidden type="file" accept=".txt" onChange={handleFileChange}  />
      
      <label for="bulk" style={{ width: '200px', marginTop:"50px",padding:"20px", fontFamily: 'Calibri',height: '100px',color:"white", backgroundColor:  '#164863'}}>Choose file</label>
      <br/><br/><br/>
      <button onClick={runBulkQuery} style={{ width: '130px', height: '48px', backgroundColor:  '#164863', color: 'white', fontFamily: 'Calibri',}}>Run Bulk Query</button>

      {/* Display results */}
      <div style={{ boxShadow: '4px 4px 8px rgba(0, 77, 153, 0.3)',}}>
        <br/>
        <h3 >Results:</h3>
        <ul>
          {results.map(({ url, status }, index) => (
            <li key={index}>{`${url}: ${status}`}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default BulkQuery;
