import React, { useState, useEffect } from 'react';
import authService from './services/authService';
import apiService from './services/apiService';
import AuthModal from './components/AuthModal';
import SearchModal from './components/SearchModal';

function App() {
  const [sourates, setSourates] = useState([]);
  const [text, setText] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('analyzer');
  const [selectedDimension, setSelectedDimension] = useState('mysteres');
  const [selectedSourate, setSelectedSourate] = useState(null);
  const [showVersets, setShowVersets] = useState(false);
  
  // États d'authentification
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Vérification de l'authentification au chargement
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    const authenticated = authService.isAuthenticated();
    if (authenticated) {
      const isValid = await authService.validateToken();
      if (isValid) {
        setUser(authService.getUser());
        setIsAuthenticated(true);
        fetchSourates();
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    } else {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const fetchSourates = async () => {
    if (!isAuthenticated) return;
    
    try {
      const data = await apiService.getSourates();
      setSourates(data);
    } catch (err) {
      console.error('Error fetching sourates:', err);
      setError('Erreur lors du chargement des sourates');
    }
  };

  const analyzeText = async () => {
    if (!text.trim() || !isAuthenticated) {
      if (!isAuthenticated) {
        setShowAuthModal(true);
      }
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      const data = await apiService.analyzeTextEnriched(text, {
        langue: 'auto',
        include_confidence: true,
        include_details: true
      });
      setAnalysis(data);
    } catch (err) {
      console.error('Error analyzing text:', err);
      setError('Erreur lors de l\'analyse du texte');
    } finally {
      setLoading(false);
    }
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
    setShowAuthModal(false);
    fetchSourates();
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    setIsAuthenticated(false);
    setSourates([]);
    setAnalysis(null);
  };

  const handleSourateClick = (sourate) => {
    setSelectedSourate(sourate);
    setShowVersets(true);
  };

  const handleVersetClick = (verset) => {
    setText(verset.texte_arabe || `Verset ${verset.numero} de la sourate ${selectedSourate.nom_francais}`);
    setShowVersets(false);
    setActiveTab('analyzer');
  };

  const generateVersets = (sourate) => {
    // Génération de versets d'exemple pour démonstration
    const versets = [];
    for (let i = 1; i <= Math.min(sourate.nombre_versets, 10); i++) {
      versets.push({
        numero: i,
        texte_arabe: i === 1 && sourate.numero === 1 ? 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ' : `آية ${i} من سورة ${sourate.nom_arabe}`,
        texte_francais: i === 1 && sourate.numero === 1 ? 'Au nom d\'Allah, le Tout Miséricordieux, le Très Miséricordieux' : `Verset ${i} de la sourate ${sourate.nom_francais}`
      });
    }
    return versets;
  };

  return (
    <div className='min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900 relative overflow-hidden'>
      {/* Background Pattern */}
      <div className='absolute inset-0 opacity-10'>
        <div className='absolute top-0 left-0 w-full h-full bg-[url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.1"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")] bg-repeat'></div>
      </div>
      
      <div className='relative z-10'>
        {/* Header */}
        <header className='text-center py-12 px-4'>
          {/* Barre d'authentification */}
          <div className='absolute top-4 right-4 flex items-center space-x-4'>
            {isAuthenticated ? (
              <div className='flex items-center space-x-3'>
                <div className='text-white text-sm'>
                  <span className='font-medium'>{user?.username}</span>
                  <span className='text-blue-200 ml-2'>({user?.role})</span>
                </div>
                <button
                  onClick={handleLogout}
                  className='px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors'
                >
                  Déconnexion
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className='px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300'
              >
                Connexion
              </button>
            )}
            <button
              onClick={() => setShowSearchModal(true)}
              className='px-4 py-2 bg-gradient-to-r from-green-600 to-teal-600 text-white font-medium rounded-lg hover:from-green-700 hover:to-teal-700 transition-all duration-300'
            >
              🔍 Recherche
            </button>
          </div>

          <div className='mb-6'>
            <div className='inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full mb-4 shadow-2xl'>
              <span className='text-3xl'>🕌</span>
            </div>
          </div>
          <h1 className='text-5xl md:text-6xl font-bold text-white mb-4 tracking-tight'>
            <span className='bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent'>
              Vision Heptuple
            </span>
          </h1>
          <p className='text-xl md:text-2xl text-blue-200 mb-2'>Intelligence Spirituelle Révolutionnaire</p>
          <p className='text-lg text-blue-300'>Analyse Exégétique selon la Fatiha • IA + Références Authentiques</p>
          
          {/* Vision Description */}
          <div className='max-w-4xl mx-auto mt-8 p-6 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20'>
            <h3 className='text-2xl font-bold text-yellow-400 mb-4'>🌟 La Vision Révolutionnaire</h3>
            <p className='text-white/90 text-lg leading-relaxed mb-4'>
              La <strong>Vision Heptuple</strong> révèle que la Fatiha contient <strong>7 dimensions spirituelles universelles</strong> qui structurent tout le Coran. 
              Cette plateforme utilise l&apos;<strong>Intelligence Artificielle</strong> pour analyser n&apos;importe quel texte selon ces dimensions sacrées.
            </p>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-200'>
              <div className='flex items-center'>
                <span className='text-purple-400 mr-2'>🔮</span>
                <span><strong>Mystères:</strong> Dimension de l&apos;invisible et du sacré</span>
              </div>
              <div className='flex items-center'>
                <span className='text-green-400 mr-2'>🌍</span>
                <span><strong>Création:</strong> Manifestation divine dans l&apos;univers</span>
              </div>
              <div className='flex items-center'>
                <span className='text-blue-400 mr-2'>✨</span>
                <span><strong>Attributs:</strong> Noms et qualités divines</span>
              </div>
              <div className='flex items-center'>
                <span className='text-red-400 mr-2'>⚡</span>
                <span><strong>Eschatologie:</strong> Jour dernier et au-delà</span>
              </div>
              <div className='flex items-center'>
                <span className='text-yellow-400 mr-2'>☀️</span>
                <span><strong>Tawhid:</strong> Unicité et unification divine</span>
              </div>
              <div className='flex items-center'>
                <span className='text-indigo-400 mr-2'>🧭</span>
                <span><strong>Guidance:</strong> Direction spirituelle et sagesse</span>
              </div>
              <div className='flex items-center'>
                <span className='text-gray-400 mr-2'>🌫️</span>
                <span><strong>Égarement:</strong> Déviation et mise en garde</span>
              </div>
            </div>
          </div>
          
          {/* Stats */}
          <div className='flex justify-center mt-8 space-x-8'>
            <div className='text-center'>
              <div className='text-2xl font-bold text-yellow-400'>114</div>
              <div className='text-sm text-blue-300'>Sourates</div>
            </div>
            <div className='text-center'>
              <div className='text-2xl font-bold text-yellow-400'>85%+</div>
              <div className='text-sm text-blue-300'>Précision IA</div>
            </div>
            <div className='text-center'>
              <div className='text-2xl font-bold text-yellow-400'>30+</div>
              <div className='text-sm text-blue-300'>Références</div>
            </div>
          </div>
        </header>
        
        {/* Navigation */}
        <nav className='flex justify-center mb-8 px-4'>
          <div className='bg-white/10 backdrop-blur-md rounded-full p-2 shadow-2xl'>
            <div className='flex space-x-2'>
              <button
                onClick={() => setActiveTab('analyzer')}
                className={`px-6 py-3 rounded-full font-medium transition-all duration-300 ${
                  activeTab === 'analyzer'
                    ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white shadow-lg transform scale-105'
                    : 'text-white/80 hover:text-white hover:bg-white/10'
                }`}
              >
                🔍 Analyseur
              </button>
              <button
                onClick={() => setActiveTab('sourates')}
                className={`px-6 py-3 rounded-full font-medium transition-all duration-300 ${
                  activeTab === 'sourates'
                    ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white shadow-lg transform scale-105'
                    : 'text-white/80 hover:text-white hover:bg-white/10'
                }`}
              >
                📖 Sourates
              </button>
              <button
                onClick={() => setActiveTab('references')}
                className={`px-6 py-3 rounded-full font-medium transition-all duration-300 ${
                  activeTab === 'references'
                    ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white shadow-lg transform scale-105'
                    : 'text-white/80 hover:text-white hover:bg-white/10'
                }`}
              >
                📚 Références
              </button>
            </div>
          </div>
        </nav>

        <div className='container mx-auto px-4 pb-12'>
          {/* Message d'erreur */}
          {error && (
            <div className='max-w-4xl mx-auto mb-6 p-4 bg-red-50 border border-red-200 rounded-lg'>
              <div className='flex items-center'>
                <span className='text-red-600 mr-2'>⚠️</span>
                <p className='text-red-800'>{error}</p>
                <button
                  onClick={() => setError('')}
                  className='ml-auto text-red-600 hover:text-red-800'
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Message de non-authentification */}
          {!isAuthenticated && (
            <div className='max-w-4xl mx-auto mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg'>
              <div className='flex items-center'>
                <span className='text-yellow-600 mr-2'>🔐</span>
                <p className='text-yellow-800'>
                  Connectez-vous pour accéder à toutes les fonctionnalités de la plateforme.
                </p>
                <button
                  onClick={() => setShowAuthModal(true)}
                  className='ml-auto px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded transition-colors'
                >
                  Se connecter
                </button>
              </div>
            </div>
          )}

          {activeTab === 'analyzer' && (
            <div className='max-w-6xl mx-auto'>
              <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
                <div className='bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl p-8 border border-white/20'>
                  <div className='flex items-center mb-6'>
                    <div className='w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-4'>
                      <span className='text-white text-xl'>🤖</span>
                    </div>
                    <h2 className='text-3xl font-bold text-gray-800'>Analyseur IA Spirituel</h2>
                  </div>
                  <div className='mb-6'>
                    <label className='block text-sm font-medium text-gray-700 mb-2'>
                      Texte à analyser selon la Vision Heptuple
                    </label>
                    <textarea
                      value={text}
                      onChange={(e) => setText(e.target.value)}
                      className='w-full h-40 p-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300 resize-none'
                      placeholder='Saisissez votre texte en arabe, français ou anglais...&#10;&#10;Exemple: "بسم الله الرحمن الرحيم" ou "Au nom d&apos;Allah, le Tout Miséricordieux"'
                    />
                  </div>
                  <button
                    onClick={analyzeText}
                    disabled={loading || !text.trim()}
                    className='w-full py-4 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 text-white font-bold rounded-xl hover:from-blue-700 hover:via-purple-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 shadow-lg'
                  >
                    {loading ? (
                      <div className='flex items-center justify-center'>
                        <div className='animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3'></div>
                        Analyse en cours...
                      </div>
                    ) : (
                      <div className='flex items-center justify-center'>
                        <span className='mr-2'>🔮</span>
                        Analyser avec l&apos;IA Spirituelle
                      </div>
                    )}
                  </button>
            
            {analysis && (
              <div className='mt-6 space-y-6'>
                {/* Analyse de base */}
                <div className='p-4 bg-gray-50 rounded-lg'>
                  <h3 className='font-semibold mb-4 text-lg'>Analyse Heptuple</h3>
                  <div className='grid grid-cols-1 gap-3'>
                    <div className='flex justify-between items-center p-2 bg-blue-100 rounded'>
                      <span className='font-medium'>Dimension dominante:</span>
                      <span className='text-blue-700 font-bold'>{analysis.analyse?.dimension_dominante || analysis.dimension_dominante}</span>
                    </div>
                    <div className='flex justify-between items-center p-2 bg-green-100 rounded'>
                      <span className='font-medium'>Intensité maximale:</span>
                      <span className='text-green-700 font-bold'>{analysis.analyse?.intensity_max || analysis.intensity_max}%</span>
                    </div>
                    <div className='flex justify-between items-center p-2 bg-purple-100 rounded'>
                      <span className='font-medium'>Références trouvées:</span>
                      <span className='text-purple-700 font-bold'>{analysis.nombre_references || 0}</span>
                    </div>
                    {(analysis.analyse?.scores || analysis.scores) && (
                      <div className='mt-4'>
                        <h4 className='font-medium mb-2'>Scores par dimension:</h4>
                        <div className='space-y-2'>
                          {Object.entries(analysis.analyse?.scores || analysis.scores).map(([dim, score]) => (
                            <div key={dim} className='flex justify-between items-center'>
                              <span className='text-sm capitalize'>{dim}:</span>
                              <div className='flex items-center'>
                                <div className='w-20 bg-gray-200 rounded-full h-2 mr-2'>
                                  <div 
                                    className='bg-blue-600 h-2 rounded-full' 
                                    style={{width: `${score}%`}}
                                  ></div>
                                </div>
                                <span className='text-sm font-medium'>{score}%</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Références Hadiths */}
                {analysis.hadiths && analysis.hadiths.length > 0 && (
                  <div className='p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-400'>
                    <h4 className='font-semibold mb-3 text-lg flex items-center'>
                      📜 Hadiths authentiques ({analysis.hadiths.length})
                    </h4>
                    <div className='space-y-3'>
                      {analysis.hadiths.map((hadith, index) => (
                        <div key={index} className='bg-white p-3 rounded border'>
                          <div className='flex justify-between items-start mb-2'>
                            <span className='text-sm font-medium text-green-600'>
                              {hadith.recueil} - {hadith.numero_hadith}
                            </span>
                            <span className='text-xs bg-green-100 px-2 py-1 rounded'>
                              {hadith.degre_authenticite}
                            </span>
                          </div>
                          <p className='text-sm text-gray-700 mb-2'>{hadith.texte_francais}</p>
                          <div className='text-xs text-gray-500'>
                            <span className='font-medium'>Narrateur:</span> {hadith.narrateur}
                          </div>
                          {hadith.contexte_historique && (
                            <div className='text-xs text-gray-600 mt-1 italic'>
                              {hadith.contexte_historique}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Références Exégèses */}
                {analysis.exegeses && analysis.exegeses.length > 0 && (
                  <div className='p-4 bg-blue-50 rounded-lg border-l-4 border-blue-400'>
                    <h4 className='font-semibold mb-3 text-lg flex items-center'>
                      📖 Exégèses traditionnelles ({analysis.exegeses.length})
                    </h4>
                    <div className='space-y-3'>
                      {analysis.exegeses.map((exegese, index) => (
                        <div key={index} className='bg-white p-3 rounded border'>
                          <div className='flex justify-between items-start mb-2'>
                            <span className='text-sm font-medium text-blue-600'>
                              {exegese.auteur} - {exegese.titre_ouvrage}
                            </span>
                            <span className='text-xs bg-blue-100 px-2 py-1 rounded'>
                              {exegese.epoque}
                            </span>
                          </div>
                          <p className='text-sm text-gray-700 mb-2'>{exegese.texte_exegese}</p>
                          <div className='text-xs text-gray-500'>
                            <span className='font-medium'>École:</span> {exegese.ecole_juridique}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Citations */}
                {analysis.citations && analysis.citations.length > 0 && (
                  <div className='p-4 bg-purple-50 rounded-lg border-l-4 border-purple-400'>
                    <h4 className='font-semibold mb-3 text-lg flex items-center'>
                      📝 Citations de savants ({analysis.citations.length})
                    </h4>
                    <div className='space-y-3'>
                      {analysis.citations.map((citation, index) => (
                        <div key={index} className='bg-white p-3 rounded border'>
                          <div className='flex justify-between items-start mb-2'>
                            <span className='text-sm font-medium text-purple-600'>
                              {citation.auteur} - {citation.source}
                            </span>
                            <span className='text-xs bg-purple-100 px-2 py-1 rounded'>
                              {citation.epoque}
                            </span>
                          </div>
                          <p className='text-sm text-gray-700 mb-1 italic'>"{citation.texte_original}"</p>
                          {citation.texte_traduit && (
                            <p className='text-sm text-gray-600 mb-2'>{citation.texte_traduit}</p>
                          )}
                          {citation.contexte && (
                            <div className='text-xs text-gray-500 italic'>
                              {citation.contexte}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Histoires */}
                {analysis.histoires && analysis.histoires.length > 0 && (
                  <div className='p-4 bg-green-50 rounded-lg border-l-4 border-green-400'>
                    <h4 className='font-semibold mb-3 text-lg flex items-center'>
                      📚 Récits authentiques ({analysis.histoires.length})
                    </h4>
                    <div className='space-y-3'>
                      {analysis.histoires.map((histoire, index) => (
                        <div key={index} className='bg-white p-3 rounded border'>
                          <div className='flex justify-between items-start mb-2'>
                            <span className='text-sm font-medium text-green-600'>
                              {histoire.titre}
                            </span>
                            <span className='text-xs bg-green-100 px-2 py-1 rounded'>
                              {histoire.epoque}
                            </span>
                          </div>
                          <p className='text-sm text-gray-700 mb-2'>{histoire.recit_complet.substring(0, 200)}...</p>
                          {histoire.enseignements && histoire.enseignements.length > 0 && (
                            <div className='text-xs text-gray-600'>
                              <span className='font-medium'>Enseignements:</span> {histoire.enseignements.join(', ')}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

                <div className='bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl p-8 border border-white/20'>
                  <div className='flex items-center mb-6'>
                    <div className='w-10 h-10 bg-gradient-to-r from-green-500 to-teal-600 rounded-full flex items-center justify-center mr-4'>
                      <span className='text-white text-xl'>📊</span>
                    </div>
                    <h2 className='text-3xl font-bold text-gray-800'>Résultats & Références</h2>
                  </div>
                  <div className='max-h-96 overflow-y-auto custom-scrollbar'>
              {sourates.map((s) => (
                <div key={s.id} className='p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer'>
                  <div className='flex justify-between items-start'>
                    <div>
                      <h3 className='font-semibold text-lg'>{s.numero}. {s.nom_francais}</h3>
                      <p className='text-sm text-gray-500 mb-2'>{s.nom_arabe}</p>
                      <div className='flex gap-4 text-sm text-gray-600'>
                        <span className='bg-gray-100 px-2 py-1 rounded'>{s.type_revelation}</span>
                        <span>{s.nombre_versets} versets</span>
                      </div>
                    </div>
                    {s.profil_heptuple && (
                      <div className='text-right'>
                        <div className='text-xs text-gray-500 mb-1'>Profil Heptuple</div>
                        <div className='grid grid-cols-2 gap-1 text-xs'>
                          <div>Mystères: {s.profil_heptuple.mysteres}%</div>
                          <div>Création: {s.profil_heptuple.creation}%</div>
                          <div>Attributs: {s.profil_heptuple.attributs}%</div>
                          <div>Eschatologie: {s.profil_heptuple.eschatologie}%</div>
                          <div>Tawhid: {s.profil_heptuple.tawhid}%</div>
                          <div>Guidance: {s.profil_heptuple.guidance}%</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
              </div>
            </div>
          )}
          
          {activeTab === 'sourates' && (
            <div className='max-w-6xl mx-auto'>
              <div className='bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl p-8 border border-white/20'>
                <div className='flex items-center mb-6'>
                  <div className='w-10 h-10 bg-gradient-to-r from-emerald-500 to-green-600 rounded-full flex items-center justify-center mr-4'>
                    <span className='text-white text-xl'>📖</span>
                  </div>
                  <h2 className='text-3xl font-bold text-gray-800'>Les 114 Sourates du Coran</h2>
                </div>
                
                {!isAuthenticated ? (
                  <div className='text-center py-12'>
                    <div className='text-6xl mb-4'>🔐</div>
                    <h3 className='text-xl font-semibold text-gray-700 mb-2'>Authentification requise</h3>
                    <p className='text-gray-600 mb-6'>Connectez-vous pour accéder aux sourates du Coran</p>
                    <button
                      onClick={() => setShowAuthModal(true)}
                      className='px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300'
                    >
                      Se connecter
                    </button>
                  </div>
                ) : sourates.length === 0 ? (
                  <div className='text-center py-12'>
                    <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4'></div>
                    <p className='text-gray-600'>Chargement des sourates...</p>
                  </div>
                ) : (
                
                <div className='mb-6 p-4 bg-blue-50 rounded-xl border-l-4 border-blue-400'>
                  <p className='text-blue-800 text-sm'>
                    <strong>💡 Instructions:</strong> Cliquez sur une sourate pour voir ses versets et sélectionner un passage à analyser selon la Vision Heptuple.
                  </p>
                </div>
                
                <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto custom-scrollbar'>
                  {sourates.map((s) => (
                    <div 
                      key={s.id} 
                      onClick={() => handleSourateClick(s)}
                      className='p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 hover:shadow-lg transition-all duration-300 cursor-pointer transform hover:scale-105 bg-white'
                    >
                      <div className='flex justify-between items-start'>
                        <div className='flex-1'>
                          <h3 className='font-bold text-lg text-gray-800 mb-1'>{s.numero}. {s.nom_francais}</h3>
                          <p className='text-sm text-gray-500 mb-2 font-arabic text-right'>{s.nom_arabe}</p>
                          <div className='flex gap-2 text-xs mb-3'>
                            <span className={`px-2 py-1 rounded-full ${
                              s.type_revelation === 'Mecquoise' 
                                ? 'bg-orange-100 text-orange-800' 
                                : 'bg-green-100 text-green-800'
                            }`}>
                              {s.type_revelation}
                            </span>
                            <span className='bg-gray-100 text-gray-700 px-2 py-1 rounded-full'>
                              {s.nombre_versets} versets
                            </span>
                          </div>
                          
                          {s.profil_heptuple && (
                            <div className='mt-3'>
                              <div className='text-xs text-gray-500 mb-2 font-semibold'>Profil Heptuple:</div>
                              <div className='grid grid-cols-2 gap-1 text-xs'>
                                <div className='flex items-center'>
                                  <div className='w-2 h-2 bg-purple-500 rounded-full mr-1'></div>
                                  <span>Mystères: {s.profil_heptuple.mysteres}%</span>
                                </div>
                                <div className='flex items-center'>
                                  <div className='w-2 h-2 bg-green-500 rounded-full mr-1'></div>
                                  <span>Création: {s.profil_heptuple.creation}%</span>
                                </div>
                                <div className='flex items-center'>
                                  <div className='w-2 h-2 bg-blue-500 rounded-full mr-1'></div>
                                  <span>Attributs: {s.profil_heptuple.attributs}%</span>
                                </div>
                                <div className='flex items-center'>
                                  <div className='w-2 h-2 bg-red-500 rounded-full mr-1'></div>
                                  <span>Eschatologie: {s.profil_heptuple.eschatologie}%</span>
                                </div>
                                <div className='flex items-center'>
                                  <div className='w-2 h-2 bg-yellow-500 rounded-full mr-1'></div>
                                  <span>Tawhid: {s.profil_heptuple.tawhid}%</span>
                                </div>
                                <div className='flex items-center'>
                                  <div className='w-2 h-2 bg-indigo-500 rounded-full mr-1'></div>
                                  <span>Guidance: {s.profil_heptuple.guidance}%</span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                        
                        <div className='ml-4 text-center'>
                          <div className='w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center'>
                            <span className='text-blue-600 text-sm'>→</span>
                          </div>
                          <div className='text-xs text-gray-500 mt-1'>Analyser</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'references' && (
            <div className='max-w-6xl mx-auto'>
              <div className='bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl p-8 border border-white/20'>
                <div className='flex items-center mb-6'>
                  <div className='w-10 h-10 bg-gradient-to-r from-amber-500 to-orange-600 rounded-full flex items-center justify-center mr-4'>
                    <span className='text-white text-xl'>📚</span>
                  </div>
                  <h2 className='text-3xl font-bold text-gray-800'>Références Islamiques Authentiques</h2>
                </div>
                
                {/* Dimension Selector */}
                <div className='mb-6'>
                  <div className='flex flex-wrap gap-2'>
                    {['mysteres', 'creation', 'attributs', 'eschatologie', 'tawhid', 'guidance', 'egarement'].map((dim) => (
                      <button
                        key={dim}
                        onClick={() => setSelectedDimension(dim)}
                        className={`px-4 py-2 rounded-full font-medium transition-all duration-300 ${
                          selectedDimension === dim
                            ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {dim.charAt(0).toUpperCase() + dim.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
                  <div className='bg-yellow-50 p-6 rounded-xl border-l-4 border-yellow-400'>
                    <h4 className='font-bold text-lg mb-3 text-yellow-800'>📜 Hadiths Authentiques</h4>
                    <p className='text-sm text-gray-600'>Collection de hadiths sahih classés par dimension heptuple</p>
                    <div className='mt-3 text-xs text-gray-500'>Sources: Bukhari, Muslim, Tirmidhi</div>
                  </div>
                  
                  <div className='bg-blue-50 p-6 rounded-xl border-l-4 border-blue-400'>
                    <h4 className='font-bold text-lg mb-3 text-blue-800'>📖 Exégèses Traditionnelles</h4>
                    <p className='text-sm text-gray-600'>Commentaires des grands savants de l&apos;Islam</p>
                    <div className='mt-3 text-xs text-gray-500'>Auteurs: Ibn Kathir, At-Tabari, Al-Qurtubi</div>
                  </div>
                  
                  <div className='bg-purple-50 p-6 rounded-xl border-l-4 border-purple-400'>
                    <h4 className='font-bold text-lg mb-3 text-purple-800'>📝 Citations de Savants</h4>
                    <p className='text-sm text-gray-600'>Sagesse des maîtres spirituels authentifiée</p>
                    <div className='mt-3 text-xs text-gray-500'>Sources: Al-Ghazali, Ibn Taymiyyah, Ibn Arabi</div>
                  </div>
                  
                  <div className='bg-green-50 p-6 rounded-xl border-l-4 border-green-400'>
                    <h4 className='font-bold text-lg mb-3 text-green-800'>📚 Récits Authentiques</h4>
                    <p className='text-sm text-gray-600'>Histoires vérifiées de l&apos;époque prophétique</p>
                    <div className='mt-3 text-xs text-gray-500'>Période: Prophétique, Compagnons, Tabi&apos;in</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Modal pour les versets */}
        {showVersets && selectedSourate && (
          <div className='fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4'>
            <div className='bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden'>
              <div className='p-6 border-b border-gray-200'>
                <div className='flex justify-between items-center'>
                  <div>
                    <h3 className='text-2xl font-bold text-gray-800'>
                      {selectedSourate.numero}. {selectedSourate.nom_francais}
                    </h3>
                    <p className='text-gray-600 font-arabic text-right mt-1'>{selectedSourate.nom_arabe}</p>
                  </div>
                  <button
                    onClick={() => setShowVersets(false)}
                    className='w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center transition-colors'
                  >
                    <span className='text-gray-600'>×</span>
                  </button>
                </div>
              </div>
              
              <div className='p-6 overflow-y-auto max-h-[60vh]'>
                <div className='mb-4 p-4 bg-blue-50 rounded-xl border-l-4 border-blue-400'>
                  <p className='text-blue-800 text-sm'>
                    <strong>📖 Sélection de verset:</strong> Cliquez sur un verset pour l\'analyser selon la Vision Heptuple.
                  </p>
                </div>
                
                <div className='space-y-3'>
                  {generateVersets(selectedSourate).map((verset) => (
                    <div
                      key={verset.numero}
                      onClick={() => handleVersetClick(verset)}
                      className='p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 hover:shadow-md transition-all duration-300 cursor-pointer bg-gray-50 hover:bg-blue-50'
                    >
                      <div className='flex items-start gap-4'>
                        <div className='w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0'>
                          <span className='text-blue-600 font-bold text-sm'>{verset.numero}</span>
                        </div>
                        <div className='flex-1'>
                          <p className='text-lg font-arabic text-right mb-2 leading-relaxed'>{verset.texte_arabe}</p>
                          <p className='text-gray-700 text-sm'>{verset.texte_francais}</p>
                        </div>
                        <div className='w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0'>
                          <span className='text-green-600 text-xs'>→</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {selectedSourate.nombre_versets > 10 && (
                    <div className='p-4 text-center text-gray-500 text-sm border-2 border-dashed border-gray-300 rounded-xl'>
                      ... et {selectedSourate.nombre_versets - 10} autres versets
                      <br />
                      <span className='text-xs'>Version complète disponible prochainement</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Modales */}
        <AuthModal 
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          onSuccess={handleAuthSuccess}
        />
        
        <SearchModal 
          isOpen={showSearchModal}
          onClose={() => setShowSearchModal(false)}
        />
        
        {/* Footer */}
        <footer className='text-center py-8 px-4 border-t border-white/20 mt-12'>
          <div className='text-white/80 text-sm'>
            <p className='mb-2'>🚀 <strong>Révolution Technologique Spirituelle</strong> • Intelligence Artificielle + Sagesse Millénaire</p>
            <p className='text-white/60'>"Comme la Fatiha contient l&apos;essence du Coran, cette plateforme contient l&apos;essence technologique de l&apos;expérience spirituelle humaine."</p>
          </div>
        </footer>
      </div>
      
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: linear-gradient(45deg, #3b82f6, #8b5cf6);
          border-radius: 3px;
        }
        .font-arabic {
          font-family: 'Amiri', 'Times New Roman', serif;
          direction: rtl;
        }
      `}</style>
    </div>
  );
}

export default App;