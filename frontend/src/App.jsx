import React, { useState, useEffect, useMemo } from 'react';
import { db } from './firebase';
import { collection, query, orderBy, limit, getDocs } from 'firebase/firestore';
import { 
  TrendingUp, Filter, Search, ExternalLink, 
  Calendar, DollarSign, Star, Menu, RefreshCw
} from 'lucide-react';
import { format, parseISO } from 'date-fns';

const CurrencyMap = {
  "USD": "$",
  "EUR": "€",
  "GBP": "£",
  "INR": "₹"
};

function App() {
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedBrokers, setSelectedBrokers] = useState([]);
  const [selectedRatings, setSelectedRatings] = useState([]);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const q = query(collection(db, "ratings"), orderBy("entry_date", "desc"), limit(200));
      const querySnapshot = await getDocs(q);
      const data = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setRatings(data);
    } catch (e) {
      console.error("Error fetching data:", e);
    } finally {
      setLoading(false);
    }
  };

  const uniqueBrokers = useMemo(() => [...new Set(ratings.map(r => r.broker))], [ratings]);
  const uniqueRatings = useMemo(() => [...new Set(ratings.map(r => r.rating))], [ratings]);

  const filteredRatings = useMemo(() => {
    return ratings.filter(r => {
      const matchesSearch = r.stock_name.toLowerCase().includes(search.toLowerCase()) || 
                            r.article_title?.toLowerCase().includes(search.toLowerCase());
      const matchesBroker = selectedBrokers.length === 0 || selectedBrokers.includes(r.broker);
      const matchesRating = selectedRatings.length === 0 || selectedRatings.includes(r.rating);
      return matchesSearch && matchesBroker && matchesRating;
    });
  }, [ratings, search, selectedBrokers, selectedRatings]);

  const toggleFilter = (set, val) => {
    set(prev => prev.includes(val) ? prev.filter(x => x !== val) : [...prev, val]);
  };

  const getRatingColor = (rating) => {
    const r = rating?.toLowerCase() || "";
    if (r.includes("buy") || r.includes("outperform")) return "tag-buy";
    if (r.includes("sell") || r.includes("underperform")) return "tag-sell";
    return "tag-hold";
  };

  return (
    <div className="min-h-screen">
      
      {/* Navbar */}
      <nav className="glass-panel sticky top-4 mx-4 md:mx-auto max-w-7xl z-50 mb-8 p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg shadow-lg shadow-blue-500/30">
            <TrendingUp className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
              AlgoTrade Pro
            </h1>
            <p className="text-xs text-slate-400">Institutional Research Tracker</p>
          </div>
        </div>

        <div className="flex items-center w-full md:w-auto gap-3">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input 
              type="text" 
              placeholder="Search stocks..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-800/50 border border-slate-700 rounded-full pl-9 pr-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors text-slate-200 placeholder-slate-500"
            />
          </div>
          <button 
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded-full border border-slate-700 transition-colors ${showFilters ? 'bg-blue-600/20 border-blue-500 text-blue-400' : 'bg-slate-800/50 text-slate-400 hover:text-white'}`}
          >
            <Filter className="w-5 h-5" />
          </button>
          <button 
            onClick={fetchData} 
            className="p-2 rounded-full bg-slate-800/50 border border-slate-700 text-slate-400 hover:text-white hover:rotate-180 transition-all duration-500"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </nav>

      {/* Filters Panel */}
      {showFilters && (
        <div className="max-w-7xl mx-auto px-4 mb-8 animate-fade-in">
          <div className="glass-panel p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wider">Brokers</h3>
                <div className="flex flex-wrap gap-2">
                  {uniqueBrokers.map(b => (
                    <button 
                      key={b}
                      onClick={() => toggleFilter(setSelectedBrokers, b)}
                      className={`px-3 py-1 rounded-full text-sm border transition-all ${
                        selectedBrokers.includes(b) 
                          ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/20' 
                          : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-500'
                      }`}
                    >
                      {b}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wider">Ratings</h3>
                <div className="flex flex-wrap gap-2">
                  {uniqueRatings.map(r => (
                    <button 
                      key={r}
                      onClick={() => toggleFilter(setSelectedRatings, r)}
                      className={`px-3 py-1 rounded-full text-sm border transition-all ${
                        selectedRatings.includes(r) 
                          ? 'bg-emerald-600 border-emerald-500 text-white shadow-lg shadow-emerald-500/20' 
                          : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-500'
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="max-w-7xl mx-auto px-4 pb-20">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRatings.length === 0 ? (
              <div className="col-span-full text-center py-20 text-slate-500">
                No ratings found matching your filters.
              </div>
            ) : (
              filteredRatings.map((item) => (
                <div key={item.id} className="glass-panel p-5 hover:translate-y-[-4px] transition-transform duration-300 group">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h2 className="text-lg font-bold text-white group-hover:text-blue-400 transition-colors">
                        {item.stock_name}
                      </h2>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-700 text-slate-300 border border-slate-600">
                          {item.broker}
                        </span>
                      </div>
                    </div>
                    <div className={`tag ${getRatingColor(item.rating)}`}>
                      {item.rating}
                    </div>
                  </div>

                  <div className="mb-4 pt-4 border-t border-slate-700/50 flex justify-between items-center">
                    <div>
                      <p className="text-xs text-slate-500 mb-0.5">Target Price</p>
                      <p className="text-xl font-bold text-white font-mono">
                         {item.target_price ? `${CurrencyMap[item.currency] || "₹"}${item.target_price.toLocaleString()}` : "N/A"}
                      </p>
                    </div>
                    <div className="text-right">
                       <p className="text-xs text-slate-500 mb-0.5">Date</p>
                       <div className="flex items-center gap-1 text-sm text-slate-300">
                         <Calendar className="w-3 h-3" />
                         <span>{item.entry_date}</span>
                       </div>
                    </div>
                  </div>
                  
                  {item.article_title && (
                    <div className="bg-slate-800/50 rounded-lg p-3 text-sm text-slate-300 border border-slate-700/50 hover:bg-slate-800 transition-colors">
                      <a href={item.article_url} target="_blank" rel="noreferrer" className="flex items-start gap-2 group/link">
                         <span className="line-clamp-2 group-hover/link:text-blue-400 transition-colors">
                           {item.article_title}
                         </span>
                         <ExternalLink className="w-3 h-3 flex-shrink-0 mt-1 opacity-50 group-hover/link:opacity-100" />
                      </a>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

    </div>
  );
}

export default App;
