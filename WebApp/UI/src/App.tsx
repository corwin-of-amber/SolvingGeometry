import React from 'react';
import './App.css';
import { Header } from './components/AppHeader/Header';
import { MainContent } from './components/MainContent/MainContent';

function App() {

  return (
    <div className="root">
      <Header/>
      <MainContent/>
    </div>
  );
}

export default App;
