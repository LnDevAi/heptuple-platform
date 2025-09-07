import React, { useState } from 'react';
import apiService from '../services/apiService';

const SearchModal = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [searchTypes, setSearchTypes] = useState(['coran', 'hadiths', 'fiqh']);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('universal');

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResults(null);

    try {
      if (activeTab === 'universal') {
        const data = await apiService.universalSearch(query, searchTypes);
        setResults(data);
      } else if (activeTab === 'coran') {
        const data = await apiService.searchCoran(query);
        setResults({ coran: data.results, total_results: data.total });
      } else if (activeTab === 'hadiths') {
        const data = await apiService.searchHadiths(query);
        setResults({ hadiths: data.results, total_results: data.total });
      } else if (activeTab === 'fiqh') {
        const data = await apiService.searchFiqh(query);
        setResults({ fiqh: data.results, total_results: data.total });
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const toggleSearchType = (type) => {
    setSearchTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Recherche Universelle</h2>
              <p className="text-gray-600">Recherchez dans le Coran, les Hadiths et la jurisprudence</p>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center transition-colors"
            >
              <span className="text-gray-600">×</span>
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Barre de recherche */}
          <div className="mb-6">
            <div className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Recherchez dans le Coran, les Hadiths, la jurisprudence..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                onClick={handleSearch}
                disabled={loading || !query.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  'Rechercher'
                )}
              </button>
            </div>

            {/* Types de recherche */}
            <div className="mt-4">
              <div className="flex flex-wrap gap-2">
                {['coran', 'hadiths', 'fiqh'].map((type) => (
                  <button
                    key={type}
                    onClick={() => toggleSearchType(type)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-all duration-300 ${
                      searchTypes.includes(type)
                        ? 'bg-blue-100 text-blue-800 border border-blue-300'
                        : 'bg-gray-100 text-gray-600 border border-gray-300'
                    }`}
                  >
                    {type === 'coran' ? '📖 Coran' : 
                     type === 'hadiths' ? '📜 Hadiths' : 
                     '⚖️ Fiqh'}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          {/* Résultats */}
          {results && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800">
                  Résultats de recherche
                </h3>
                <span className="text-sm text-gray-600">
                  {results.total_results || 0} résultat(s) trouvé(s)
                </span>
              </div>

              {/* Onglets des résultats */}
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                  {['universal', 'coran', 'hadiths', 'fiqh'].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`py-2 px-1 border-b-2 font-medium text-sm ${
                        activeTab === tab
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      {tab === 'universal' ? '🌐 Universel' :
                       tab === 'coran' ? '📖 Coran' :
                       tab === 'hadiths' ? '📜 Hadiths' :
                       '⚖️ Fiqh'}
                    </button>
                  ))}
                </nav>
              </div>

              {/* Contenu des résultats */}
              <div className="max-h-96 overflow-y-auto">
                {activeTab === 'universal' && results && (
                  <div className="space-y-4">
                    {results.coran && results.coran.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-800 mb-2">📖 Coran ({results.coran.length})</h4>
                        <div className="space-y-2">
                          {results.coran.slice(0, 3).map((result, index) => (
                            <div key={index} className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                              <div className="font-medium text-blue-800">
                                {result.sourate?.nom_francais} - Verset {result.verset?.numero_verset}
                              </div>
                              <div className="text-sm text-gray-700 mt-1">
                                {result.verset?.texte_arabe}
                              </div>
                              <div className="text-xs text-gray-600 mt-1">
                                {result.verset?.traduction_francaise}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {results.hadiths && results.hadiths.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-800 mb-2">📜 Hadiths ({results.hadiths.length})</h4>
                        <div className="space-y-2">
                          {results.hadiths.slice(0, 3).map((hadith, index) => (
                            <div key={index} className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                              <div className="font-medium text-yellow-800">
                                {hadith.recueil} - {hadith.numero_hadith}
                              </div>
                              <div className="text-sm text-gray-700 mt-1">
                                {hadith.texte_francais}
                              </div>
                              <div className="text-xs text-gray-600 mt-1">
                                Narrateur: {hadith.narrateur}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {results.fiqh && results.fiqh.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-800 mb-2">⚖️ Fiqh ({results.fiqh.length})</h4>
                        <div className="space-y-2">
                          {results.fiqh.slice(0, 3).map((ruling, index) => (
                            <div key={index} className="p-3 bg-green-50 rounded-lg border border-green-200">
                              <div className="font-medium text-green-800">
                                {ruling.rite} - {ruling.topic}
                              </div>
                              <div className="text-sm text-gray-700 mt-1">
                                {ruling.ruling_text}
                              </div>
                              <div className="text-xs text-gray-600 mt-1">
                                Question: {ruling.question}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {activeTab !== 'universal' && results && (
                  <div className="space-y-3">
                    {results[activeTab]?.map((result, index) => (
                      <div key={index} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                        {activeTab === 'coran' && (
                          <div>
                            <div className="font-medium text-gray-800">
                              {result.sourate?.nom_francais} - Verset {result.verset?.numero_verset}
                            </div>
                            <div className="text-sm text-gray-700 mt-1">
                              {result.verset?.texte_arabe}
                            </div>
                            <div className="text-xs text-gray-600 mt-1">
                              {result.verset?.traduction_francaise}
                            </div>
                          </div>
                        )}
                        
                        {activeTab === 'hadiths' && (
                          <div>
                            <div className="font-medium text-gray-800">
                              {result.recueil} - {result.numero_hadith}
                            </div>
                            <div className="text-sm text-gray-700 mt-1">
                              {result.texte_francais}
                            </div>
                            <div className="text-xs text-gray-600 mt-1">
                              Narrateur: {result.narrateur} | Authenticité: {result.degre_authenticite}
                            </div>
                          </div>
                        )}
                        
                        {activeTab === 'fiqh' && (
                          <div>
                            <div className="font-medium text-gray-800">
                              {result.rite} - {result.topic}
                            </div>
                            <div className="text-sm text-gray-700 mt-1">
                              {result.ruling_text}
                            </div>
                            <div className="text-xs text-gray-600 mt-1">
                              Question: {result.question}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchModal;
