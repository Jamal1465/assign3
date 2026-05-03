import React, { useState, useEffect } from 'react';
import axios from 'axios';

function TradingModal({ ticker, marketPrices, cashAvailable, portfolio, onClose, onTradeSuccess }) {
  const [selectedTicker, setSelectedTicker] = useState(ticker || '');
  const [tradeType, setTradeType] = useState('BUY');
  const [quantity, setQuantity] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const userId = parseInt(localStorage.getItem('userId')) || 1;

  const selectedStock = marketPrices.find(s => s.ticker === selectedTicker);
  const currentPrice = selectedStock?.current_price || 0;
  const totalCost = currentPrice * (parseInt(quantity) || 0);
  const ownedShares = portfolio.find(p => p.ticker === selectedTicker)?.quantity || 0;

  useEffect(() => {
    if (ticker) {
      setSelectedTicker(ticker);
    }
  }, [ticker]);

  const handleTrade = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!selectedTicker) {
      setError('Please select a stock');
      setLoading(false);
      return;
    }

    if (!quantity || parseInt(quantity) <= 0) {
      setError('Please enter a valid quantity');
      setLoading(false);
      return;
    }

    const qty = tradeType === 'BUY' ? parseInt(quantity) : -parseInt(quantity);

    try {
      const response = await axios.post('http://54.209.78.237:8000/trade', {
        user_id: userId,
        ticker: selectedTicker,
        quantity: qty
      });

      if (response.data) {
        onTradeSuccess();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Trade failed. Please try again.');
      setLoading(false);
    }
  };

  const handleMaxBuy = () => {
    if (currentPrice > 0) {
      const maxShares = Math.floor(cashAvailable / currentPrice);
      setQuantity(maxShares.toString());
    }
  };

  const handleMaxSell = () => {
    setQuantity(ownedShares.toString());
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1A2B3D] rounded-xl border border-[#2A3B4D] w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Trade Stock</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Trade Type Tabs */}
        <div className="flex space-x-2 mb-6">
          <button
            onClick={() => {
              setTradeType('BUY');
              setError('');
            }}
            className={`flex-1 py-2 rounded-lg font-semibold transition ${
              tradeType === 'BUY'
                ? 'bg-green-600 text-white'
                : 'bg-[#0A1929] text-gray-400 hover:text-white'
            }`}
          >
            Buy
          </button>
          <button
            onClick={() => {
              setTradeType('SELL');
              setError('');
            }}
            className={`flex-1 py-2 rounded-lg font-semibold transition ${
              tradeType === 'SELL'
                ? 'bg-red-600 text-white'
                : 'bg-[#0A1929] text-gray-400 hover:text-white'
            }`}
          >
            Sell
          </button>
        </div>

        <form onSubmit={handleTrade}>
          {/* Stock Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Select Stock
            </label>
            <select
              value={selectedTicker}
              onChange={(e) => {
                setSelectedTicker(e.target.value);
                setError('');
              }}
              className="w-full bg-[#0A1929] border border-[#2A3B4D] rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
              required
            >
              <option value="">Select a stock...</option>
              {marketPrices.map((stock) => (
                <option key={stock.ticker} value={stock.ticker}>
                  {stock.ticker} - {stock.company_name}
                </option>
              ))}
            </select>
          </div>

          {/* Current Price */}
          {selectedStock && (
            <div className="mb-4 p-4 bg-[#0A1929] rounded-lg">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Current Price:</span>
                <span className="text-xl font-bold">{new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: 'USD'
                }).format(currentPrice)}</span>
              </div>
              <div className="flex justify-between items-center mt-2">
                <span className="text-gray-400">Day Change:</span>
                <span className={selectedStock.day_change >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {selectedStock.day_change >= 0 ? '+' : ''}
                  {new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                  }).format(selectedStock.day_change)} ({selectedStock.day_change_percent >= 0 ? '+' : ''}{selectedStock.day_change_percent.toFixed(2)}%)
                </span>
              </div>
              {tradeType === 'SELL' && ownedShares > 0 && (
                <div className="flex justify-between items-center mt-2">
                  <span className="text-gray-400">Owned Shares:</span>
                  <span className="text-white font-semibold">{ownedShares}</span>
                </div>
              )}
            </div>
          )}

          {/* Quantity Input */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-400">
                Quantity
              </label>
              {tradeType === 'BUY' ? (
                <button
                  type="button"
                  onClick={handleMaxBuy}
                  className="text-sm text-blue-400 hover:text-blue-300"
                >
                  Max
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleMaxSell}
                  className="text-sm text-blue-400 hover:text-blue-300"
                >
                  All ({ownedShares})
                </button>
              )}
            </div>
            <input
              type="number"
              value={quantity}
              onChange={(e) => {
                setQuantity(e.target.value);
                setError('');
              }}
              min="1"
              max={tradeType === 'SELL' ? ownedShares : undefined}
              className="w-full bg-[#0A1929] border border-[#2A3B4D] rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
              placeholder="Enter quantity"
              required
            />
          </div>

          {/* Total Cost */}
          {quantity && parseInt(quantity) > 0 && (
            <div className="mb-4 p-4 bg-[#0A1929] rounded-lg">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Total {tradeType === 'BUY' ? 'Cost' : 'Proceeds'}:</span>
                <span className="text-xl font-bold">
                  {new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                  }).format(totalCost)}
                </span>
              </div>
              {tradeType === 'BUY' && (
                <div className="flex justify-between items-center mt-2">
                  <span className="text-gray-400">Cash Available:</span>
                  <span className={cashAvailable >= totalCost ? 'text-green-400' : 'text-red-400'}>
                    {new Intl.NumberFormat('en-US', {
                      style: 'currency',
                      currency: 'USD'
                    }).format(cashAvailable)}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-500 bg-opacity-20 border border-red-500 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || (tradeType === 'BUY' && totalCost > cashAvailable) || (tradeType === 'SELL' && parseInt(quantity) > ownedShares)}
            className={`w-full py-3 rounded-lg font-semibold transition ${
              tradeType === 'BUY'
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-red-600 hover:bg-red-700'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {loading ? 'Processing...' : `${tradeType} ${selectedTicker || 'Stock'}`}
          </button>
        </form>
      </div>
    </div>
  );
}

export default TradingModal;


