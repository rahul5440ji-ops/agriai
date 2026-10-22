import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './screens/Home';
import Dashboard from './screens/Dashboard';
import MyFarm from './screens/MyFarm';
import Soil from './screens/Soil';
import YieldPrediction from './screens/YieldPrediction';
import Advisory from './screens/Advisory';
import MarketAdvisor from './screens/MarketAdvisor';
import MarketComparison from './screens/MarketComparison';
import PriceForecast from './screens/PriceForecast';
import History from './screens/History';
import Settings from './screens/Settings';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout><Home /></Layout>} />
        <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
        <Route path="/farm" element={<Layout><MyFarm /></Layout>} />
        <Route path="/soil" element={<Layout><Soil /></Layout>} />
        <Route path="/yield" element={<Layout><YieldPrediction /></Layout>} />
        <Route path="/advisory" element={<Layout><Advisory /></Layout>} />
        <Route path="/market" element={<Layout><MarketAdvisor /></Layout>} />
        <Route path="/compare" element={<Layout><MarketComparison /></Layout>} />
        <Route path="/forecast" element={<Layout><PriceForecast /></Layout>} />
        <Route path="/history" element={<Layout><History /></Layout>} />
        <Route path="/settings" element={<Layout><Settings /></Layout>} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);