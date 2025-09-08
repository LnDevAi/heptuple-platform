/**
 * Service API pour toutes les requêtes vers le backend
 */
import authService from './authService';

class ApiService {
  constructor() {
    const envBase = process.env.REACT_APP_API_BASE || process.env.REACT_APP_API_URL || '';
    const inferredBase = typeof window !== 'undefined' ? `${window.location.origin}/api` : '';
    this.apiBase = envBase || inferredBase;
    this.apiUrl = this.apiBase.endsWith('/api') ? this.apiBase : (this.apiBase ? `${this.apiBase}/api` : 'http://localhost:8000/api');
  }

  /**
   * Requête GET authentifiée
   */
  async get(endpoint) {
    const response = await authService.authenticatedRequest(`${this.apiUrl}${endpoint}`);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erreur de requête' }));
      throw new Error(error.detail || `Erreur ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Requête POST authentifiée
   */
  async post(endpoint, data) {
    const response = await authService.authenticatedRequest(`${this.apiUrl}${endpoint}`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erreur de requête' }));
      throw new Error(error.detail || `Erreur ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Récupère la liste des sourates
   */
  async getSourates() {
    return this.get('/v2/sourates');
  }

  /**
   * Récupère une sourate par numéro
   */
  async getSourate(numero) {
    return this.get(`/v2/sourates/${numero}`);
  }

  /**
   * Analyse un texte
   */
  async analyzeText(text, options = {}) {
    return this.post('/v2/analyze', {
      texte: text,
      langue: options.langue || 'auto',
      include_confidence: options.include_confidence !== false,
      include_details: options.include_details || false
    });
  }

  /**
   * Analyse enrichie d'un texte
   */
  async analyzeTextEnriched(text, options = {}) {
    return this.post('/v2/analyze-enriched', {
      texte: text,
      langue: options.langue || 'auto',
      include_confidence: options.include_confidence !== false,
      include_details: options.include_details || false
    });
  }

  /**
   * Recherche universelle
   */
  async universalSearch(query, searchTypes = ['coran', 'hadiths', 'fiqh'], filters = {}, limit = 20) {
    return this.post('/v2/search/universal', {
      query,
      search_types: searchTypes,
      filters,
      limit
    });
  }

  /**
   * Recherche dans le Coran
   */
  async searchCoran(query, filters = {}, limit = 20) {
    const filterString = Object.keys(filters).length > 0 ? JSON.stringify(filters) : null;
    const params = new URLSearchParams({
      query,
      limit: limit.toString()
    });
    
    if (filterString) {
      params.append('filters', filterString);
    }

    const response = await authService.authenticatedRequest(`${this.apiUrl}/v2/search/coran?${params}`);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erreur de recherche' }));
      throw new Error(error.detail || `Erreur ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Recherche dans les Hadiths
   */
  async searchHadiths(query, filters = {}, limit = 20) {
    const filterString = Object.keys(filters).length > 0 ? JSON.stringify(filters) : null;
    const params = new URLSearchParams({
      query,
      limit: limit.toString()
    });
    
    if (filterString) {
      params.append('filters', filterString);
    }

    const response = await authService.authenticatedRequest(`${this.apiUrl}/v2/search/hadiths?${params}`);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erreur de recherche' }));
      throw new Error(error.detail || `Erreur ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Recherche dans le Fiqh
   */
  async searchFiqh(query, filters = {}, limit = 20) {
    const filterString = Object.keys(filters).length > 0 ? JSON.stringify(filters) : null;
    const params = new URLSearchParams({
      query,
      limit: limit.toString()
    });
    
    if (filterString) {
      params.append('filters', filterString);
    }

    const response = await authService.authenticatedRequest(`${this.apiUrl}/v2/search/fiqh?${params}`);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erreur de recherche' }));
      throw new Error(error.detail || `Erreur ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Récupère les dimensions heptuple
   */
  async getDimensions() {
    return this.get('/v2/dimensions');
  }

  /**
   * Récupère les hadiths par dimension
   */
  async getHadithsByDimension(dimension, limit = 10) {
    return this.get(`/v2/hadiths/${dimension}?limit=${limit}`);
  }

  /**
   * Récupère les exégèses par dimension
   */
  async getExegesesByDimension(dimension, limit = 5) {
    return this.get(`/v2/exegeses/${dimension}?limit=${limit}`);
  }

  /**
   * Compare des sourates
   */
  async compareSourates(sourateIds) {
    return this.post('/v2/compare', {
      sourate_ids: sourateIds,
      include_statistics: true
    });
  }

  /**
   * Soumet un feedback
   */
  async submitFeedback(feedbackData) {
    return this.post('/v2/feedback', feedbackData);
  }

  /**
   * Vérifie la santé de l'API
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.apiUrl.replace('/api', '')}/health`);
      return response.ok ? await response.json() : null;
    } catch (error) {
      return null;
    }
  }

  /**
   * Vérifie la santé de la base de données
   */
  async databaseHealthCheck() {
    try {
      const response = await fetch(`${this.apiUrl.replace('/api', '')}/api/v2/db/health`);
      return response.ok ? await response.json() : null;
    } catch (error) {
      return null;
    }
  }
}

// Instance singleton
const apiService = new ApiService();
export default apiService;
