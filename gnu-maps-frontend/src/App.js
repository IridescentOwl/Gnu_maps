import React from 'react';
import './App.css';
import Map from './components/Map';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>GNU Maps</h1>
        <p>Select a start and destination to estimate the ETA</p>
      </header>
      <Map />
    </div>
  );
}

export default App;