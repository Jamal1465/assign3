import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import Logo from './Logo';
import TradingModal from './TradingModal';

function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview'); // overview, portfolio, trading, history
  const [riskMetrics, setRiskMetrics] = useState(null);
  const [tradeHistory, setTradeHistory] = useState([]);
  const [portfolio, setPortfolio] = useState([]);
  const [summary, setSummary] = useState({
    total_value: 0,
    day_gain_loss: 0,
    day_gain_loss_percent: 0,
    total_positions: 0,
    cash_available: 0,
    total_profit_loss: 0,
    total_profit_loss_percent: 0
  });
  const [allocation, setAllocation] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [marketPrices, setMarketPrices] = useState([]);
  const [showTradingModal, setShowTradingModal] = useState(false);
  const [selectedTicker, setSelectedTicker] = useState(null);
  const userId = parseInt(localStorage.getItem('userId')) || 1;
  const username = localStorage.getItem('username') || 'User';
  const navigate = useNavigate();

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    try {
      const [summaryRes, portfolioRes, riskRes, historyRes, allocRes, sectorsRes, marketRes] = await Promise.all([
        axios.get(`http://54.209.78.237:8000/portfolio/${userId}/summary`),
        axios.get(`http://54.209.78.237:8000/portfolio/${userId}`),
        axios.get(`http://54.209.78.237:8000/portfolio/${userId}/risk-metrics`),
        axios.get(`http://54.209.78.237:8000/trades/${userId}/history?limit=5`),
        axios.get(`http://54.209.78.237:8000/portfolio/${userId}/allocation`),
        axios.get(`http://54.209.78.237:8000/portfolio/${userId}/sectors`),
        axios.get(`http://54.209.78.237:8000/market/prices`)
      ]);

      setSummary(summaryRes.data);
      setPortfolio(portfolioRes.data);
      setRiskMetrics(riskRes.data);
      setTradeHistory(historyRes.data);
      setAllocation(allocRes.data);
      setSectors(sectorsRes.data);
      setMarketPrices(marketRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    localStorage.removeItem('rememberMe');
    navigate('/login');
  };

  const handleTrade = (ticker = null) => {
    setSelectedTicker(ticker);
    setShowTradingModal(true);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
  };

  const getStatusColor = (status) => {
    if (status === 'Good' || status === 'Low') return 'bg-green-500';
    if (status === 'Moderate' || status === 'Medium') return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getStatusProgress = (status) => {
    if (status === 'Good' || status === 'Low') return 85;
    if (status === 'Moderate' || status === 'Medium') return 60;
    return 30;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A1929] to-[#1A2B3D] text-white">
      {/* Navigation Bar */}
      <nav className="bg-[#0A1929] border-b border-[#1A2B3D] px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-3">
              <Logo />
              <span className="text-2xl font-bold">TradeX</span>
            </div>
            <div className="hidden md:flex items-center space-x-6">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-4 py-2 rounded-lg transition ${activeTab === 'overview' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('portfolio')}
                className={`px-4 py-2 rounded-lg transition ${activeTab === 'portfolio' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
              >
                Portfolio
              </button>
              <button
                onClick={() => setActiveTab('trading')}
                className={`px-4 py-2 rounded-lg transition ${activeTab === 'trading' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
              >
                Trading
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-4 py-2 rounded-lg transition ${activeTab === 'history' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
              >
                History
              </button>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => handleTrade()}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
            >
              + Trade
            </button>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg font-semibold transition"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Log Out</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <>
            {/* Portfolio Summary with Profit/Loss */}
            <div className="mb-8 grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-[#1A2B3D] rounded-xl p-6 border border-[#2A3B4D]">
                <p className="text-gray-400 text-sm mb-2">Total Portfolio Value</p>
                <p className="text-3xl font-bold">{formatCurrency(summary.total_value + summary.cash_available)}</p>
              </div>
              <div className="bg-[#1A2B3D] rounded-xl p-6 border border-[#2A3B4D]">
                <p className="text-gray-400 text-sm mb-2">Cash Available</p>
                <p className="text-3xl font-bold">{formatCurrency(summary.cash_available)}</p>
              </div>
              <div className={`bg-[#1A2B3D] rounded-xl p-6 border ${summary.total_profit_loss >= 0 ? 'border-green-500' : 'border-red-500'} border-[#2A3B4D]`}>
                <p className="text-gray-400 text-sm mb-2">Total Profit/Loss</p>
                <p className={`text-3xl font-bold ${summary.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatCurrency(summary.total_profit_loss || 0)}
                </p>
                <p className={`text-sm mt-1 ${summary.total_profit_loss_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatPercent(summary.total_profit_loss_percent || 0)}
                </p>
              </div>
              <div className="bg-[#1A2B3D] rounded-xl p-6 border border-[#2A3B4D]">
                <p className="text-gray-400 text-sm mb-2">Day Gain/Loss</p>
                <p className={`text-3xl font-bold ${summary.day_gain_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatCurrency(summary.day_gain_loss)}
                </p>
                <p className={`text-sm mt-1 ${summary.day_gain_loss_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatPercent(summary.day_gain_loss_percent)}
                </p>
              </div>
            </div>

            {/* Risk & Performance Metrics */}
            {riskMetrics && (
              <div className="mb-8">
                <h2 className="text-2xl font-bold mb-6">Risk & Performance Metrics</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {/* Sharpe Ratio */}
                  <div className="bg-[#1A2B3D] rounded-xl p-6 border border-[#2A3B4D]">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-gray-400 text-sm">Sharpe Ratio</h3>
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <p className="text-3xl font-bold mb-2">{riskMetrics.sharpe_ratio}</p>
                    <p className={`text-sm mb-3 ${riskMetrics.sharpe_status === 'Good' ? 'text-green-400' : riskMetrics.sharpe_status === 'Moderate' ? 'text-orange-400' : 'text-red-400'}`}>
                      {riskMetrics.sharpe_status}
                    </p>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getStatusColor(riskMetrics.sharpe_status)}`}
                        style={{ width: `${getStatusProgress(riskMetrics.sharpe_status)}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Beta */}
                  <div className="bg-[#1A2B3D] rounded-xl p-6 border border-[#2A3B4D]">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-gray-400 text-sm">Beta</h3>
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                      </svg>
                    </div>
                    <p className="text-3xl font-bold mb-2">{riskMetrics.beta}</p>
                    <p className={`text-sm mb-3 ${riskMetrics.beta_status === 'Low' ? 'text-green-400' : riskMetrics.beta_status === 'Moderate' ? 'text-orange-400' : 'text-red-400'}`}>
                      {riskMetrics.beta_status}
                    </p>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getStatusColor(riskMetrics.beta_status)}`}
                        style={{ width: `${getStatusProgress(riskMetrics.beta_status)}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Volatility */}
                  <div className="bg-[#1A2B3D] rounded-xl p-6 border border-[#2A3B4D]">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-gray-400 text-sm">Volatility</h3>
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    </div>
                    <p className="text-3xl font-bold mb-2">{riskMetrics.volatility}%</p>
                    <p className={`text-sm mb-3 ${riskMetrics.volatility_status === 'Low' ? 'text-green-400' : riskMetrics.volatility_status === 'Medium' ? 'text-orange-400' : 'text-red-400'}`}>
                      {riskMetrics.volatility_status}
                    </p>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getStatusColor(riskMetrics.volatility_status)}`}
                        style={{ width: `${getStatusProgress(riskMetrics.volatility_status)}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Max Drawdown */}
                  <div className="bg-[#1A2B3D] rounded-xl p-6 border border-[#2A3B4D]">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-gray-400 text-sm">Max Drawdown</h3>
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                      </svg>
                    </div>
                    <p className="text-3xl font-bold mb-2">{riskMetrics.max_drawdown}%</p>
                    <p className={`text-sm mb-3 ${riskMetrics.max_drawdown_status === 'Low' ? 'text-green-400' : riskMetrics.max_drawdown_status === 'Moderate' ? 'text-orange-400' : 'text-red-400'}`}>
                      {riskMetrics.max_drawdown_status}
                    </p>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getStatusColor(riskMetrics.max_drawdown_status)}`}
                        style={{ width: `${getStatusProgress(riskMetrics.max_drawdown_status)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Recent Activity */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Recent Activity</h2>
                <button
                  onClick={() => setActiveTab('history')}
                  className="text-blue-400 hover:text-blue-300 transition"
                >
                  View All →
                </button>
              </div>
              <div className="bg-[#1A2B3D] rounded-xl border border-[#2A3B4D] p-6">
                {tradeHistory.length === 0 ? (
                  <p className="text-gray-400 text-center py-8">No recent activity</p>
                ) : (
                  <div className="space-y-4">
                    {tradeHistory.map((trade) => (
                      <div key={trade.id} className="flex items-center justify-between py-3 border-b border-[#2A3B4D] last:border-0">
                        <div className="flex items-center space-x-4">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            trade.type === 'BUY' ? 'bg-green-500 bg-opacity-20' : 'bg-red-500 bg-opacity-20'
                          }`}>
                            {trade.type === 'BUY' ? (
                              <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                              </svg>
                            ) : (
                              <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                              </svg>
                            )}
                          </div>
                          <div>
                            <p className="font-semibold">
                              {trade.type === 'BUY' ? 'Bought' : 'Sold'} {trade.ticker}
                            </p>
                            <p className="text-sm text-gray-400">
                              {trade.quantity} shares at {formatCurrency(trade.price_per_share)}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">{formatCurrency(trade.total_amount)}</p>
                          <p className="text-sm text-gray-400">{formatTimeAgo(trade.timestamp)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

          </>
        )}

        {activeTab === 'portfolio' && (
          <div>
            {/* Portfolio Allocation Pie Charts */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold mb-6">Portfolio Allocation</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Cash vs Holdings Pie Chart */}
                <div className="bg-[#1A2B3D] rounded-xl border border-[#2A3B4D] p-6">
                  <h3 className="text-lg font-semibold mb-4">Cash vs Holdings</h3>
                  {(() => {
                    const totalValue = summary.total_value + summary.cash_available;
                    const holdingsValue = summary.total_value;
                    const cashValue = summary.cash_available;
                    
                    const pieData = [
                      { name: 'Holdings', value: holdingsValue, color: '#4FC3F7' },
                      { name: 'Cash', value: cashValue, color: '#4CAF50' }
                    ].filter(item => item.value > 0);

                    if (pieData.length === 0 || totalValue === 0) {
                      return <p className="text-gray-400 text-center py-8">No portfolio data</p>;
                    }

                    return (
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {pieData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value) => formatCurrency(value)} />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    );
                  })()}
                </div>

                {/* Stock Allocation Pie Chart */}
                <div className="bg-[#1A2B3D] rounded-xl border border-[#2A3B4D] p-6">
                  <h3 className="text-lg font-semibold mb-4">Stock Allocation</h3>
                  {allocation.length === 0 ? (
                    <p className="text-gray-400 text-center py-8">No holdings</p>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={allocation.slice(0, 10)}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ ticker, percentage }) => `${ticker}: ${percentage.toFixed(1)}%`}
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="percentage"
                        >
                          {allocation.slice(0, 10).map((entry, index) => {
                            const colors = ['#4FC3F7', '#9C27B0', '#2196F3', '#4CAF50', '#FF9800', '#F44336', '#00BCD4', '#E91E63', '#FFC107', '#795548'];
                            return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                          })}
                        </Pie>
                        <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </div>
            </div>

            {/* Sector Breakdown */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Sector Breakdown</h2>
                <button className="text-blue-400 hover:text-blue-300 transition">View Details</button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {sectors.length === 0 ? (
                  <p className="text-gray-400 col-span-3 text-center py-8">No sector data</p>
                ) : (
                  sectors.map((sector) => {
                    const sectorIcons = {
                      'Technology': '⚙️',
                      'Financial': '📈',
                      'Consumer': '🏪',
                      'Industrial': '🏭',
                      'Healthcare': '🏥',
                      'Energy': '⚡'
                    };
                    return (
                      <div key={sector.sector} className="bg-[#1A2B3D] rounded-xl border border-[#2A3B4D] p-6">
                        <div className="flex items-center space-x-3 mb-4">
                          <span className="text-3xl">{sectorIcons[sector.sector] || '📊'}</span>
                          <div>
                            <h3 className="font-semibold text-lg">{sector.sector}</h3>
                            <p className="text-sm text-gray-400">{sector.holdings} holdings</p>
                          </div>
                        </div>
                        <div className="mt-4">
                          <p className="text-2xl font-bold mb-1">{sector.percentage.toFixed(1)}%</p>
                          <p className="text-gray-400 text-sm">Total Value {formatCurrency(sector.total_value)}</p>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            <h2 className="text-2xl font-bold mb-6">Portfolio Holdings</h2>
            <div className="bg-[#1A2B3D] rounded-xl border border-[#2A3B4D] overflow-hidden">
              <table className="w-full">
                <thead className="bg-[#0A1929] border-b border-[#2A3B4D]">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">TICKER</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">COMPANY NAME</th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">QUANTITY</th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">CURRENT PRICE</th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">TOTAL VALUE</th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">DAY CHANGE</th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">TOTAL RETURN</th>
                    <th className="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase">ACTIONS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#2A3B4D]">
                  {portfolio.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="px-6 py-12 text-center text-gray-400">
                        No holdings. Start trading to build your portfolio!
                      </td>
                    </tr>
                  ) : (
                    portfolio.map((item) => (
                      <tr key={item.ticker} className="hover:bg-[#2A3B4D] transition">
                        <td className="px-6 py-4 font-semibold">{item.ticker}</td>
                        <td className="px-6 py-4 text-gray-300">{item.company_name}</td>
                        <td className="px-6 py-4 text-right font-medium">{item.quantity}</td>
                        <td className="px-6 py-4 text-right">{formatCurrency(item.current_price)}</td>
                        <td className="px-6 py-4 text-right font-bold">{formatCurrency(item.total_value)}</td>
                        <td className={`px-6 py-4 text-right font-medium ${item.day_change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {formatCurrency(item.day_change)} ({formatPercent(item.day_change_percent)})
                        </td>
                        <td className={`px-6 py-4 text-right font-medium ${item.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {formatCurrency(item.total_return)} ({formatPercent(item.total_return_percent)})
                        </td>
                        <td className="px-6 py-4 text-center">
                          <button
                            onClick={() => handleTrade(item.ticker)}
                            className="text-blue-400 hover:text-blue-300 transition"
                          >
                            Trade
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'trading' && (
          <div>
            <h2 className="text-2xl font-bold mb-6">Market Prices</h2>
            <div className="bg-[#1A2B3D] rounded-xl border border-[#2A3B4D] overflow-hidden">
              <table className="w-full">
                <thead className="bg-[#0A1929] border-b border-[#2A3B4D]">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">TICKER</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">COMPANY NAME</th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">CURRENT PRICE</th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">DAY CHANGE</th>
                    <th className="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase">ACTION</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#2A3B4D]">
                  {marketPrices.map((stock) => (
                    <tr key={stock.ticker} className="hover:bg-[#2A3B4D] transition">
                      <td className="px-6 py-4 font-semibold">{stock.ticker}</td>
                      <td className="px-6 py-4 text-gray-300">{stock.company_name}</td>
                      <td className="px-6 py-4 text-right font-bold">{formatCurrency(stock.current_price)}</td>
                      <td className={`px-6 py-4 text-right font-medium ${stock.day_change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {formatCurrency(stock.day_change)} ({formatPercent(stock.day_change_percent)})
                      </td>
                      <td className="px-6 py-4 text-center">
                        <button
                          onClick={() => handleTrade(stock.ticker)}
                          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
                        >
                          Trade
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div>
            <h2 className="text-2xl font-bold mb-6">Trade History</h2>
            <div className="bg-[#1A2B3D] rounded-xl border border-[#2A3B4D] p-6">
              {tradeHistory.length === 0 ? (
                <p className="text-gray-400 text-center py-8">No trade history</p>
              ) : (
                <div className="space-y-4">
                  {tradeHistory.map((trade) => (
                    <div key={trade.id} className="flex items-center justify-between py-3 border-b border-[#2A3B4D] last:border-0">
                      <div className="flex items-center space-x-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          trade.type === 'BUY' ? 'bg-green-500 bg-opacity-20' : 'bg-red-500 bg-opacity-20'
                        }`}>
                          {trade.type === 'BUY' ? (
                            <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                            </svg>
                          ) : (
                            <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                            </svg>
                          )}
                        </div>
                        <div>
                          <p className="font-semibold">
                            {trade.type === 'BUY' ? 'Bought' : 'Sold'} {trade.ticker} - {trade.company_name}
                          </p>
                          <p className="text-sm text-gray-400">
                            {trade.quantity} shares at {formatCurrency(trade.price_per_share)}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-semibold ${trade.type === 'BUY' ? 'text-red-400' : 'text-green-400'}`}>
                          {trade.type === 'BUY' ? '-' : '+'}{formatCurrency(trade.total_amount)}
                        </p>
                        <p className="text-sm text-gray-400">{new Date(trade.timestamp).toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Trading Modal */}
      {showTradingModal && (
        <TradingModal
          ticker={selectedTicker}
          marketPrices={marketPrices}
          cashAvailable={summary.cash_available}
          portfolio={portfolio}
          onClose={() => {
            setShowTradingModal(false);
            setSelectedTicker(null);
          }}
          onTradeSuccess={() => {
            fetchAllData();
            setShowTradingModal(false);
            setSelectedTicker(null);
          }}
        />
      )}
    </div>
  );
}

export default Dashboard;
