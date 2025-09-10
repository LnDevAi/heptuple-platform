/**
 * Service d'authentification pour le frontend
 */
class AuthService {
  constructor() {
    this.token = localStorage.getItem('heptuple_token');
    this.user = JSON.parse(localStorage.getItem('heptuple_user') || 'null');
    const envBase = process.env.REACT_APP_API_BASE || process.env.REACT_APP_API_URL || '';
    const inferredBase = typeof window !== 'undefined' ? `${window.location.origin}/api` : '';
    this.apiBase = envBase || inferredBase;
    this.apiUrl = this.apiBase.endsWith('/api') ? this.apiBase : (this.apiBase ? `${this.apiBase}/api` : 'http://localhost:8000/api');
  }

  /**
   * Vérifie si l'utilisateur est connecté
   */
  isAuthenticated() {
    return !!this.token && !!this.user;
  }

  /**
   * Récupère le token d'authentification
   */
  getToken() {
    return this.token;
  }

  /**
   * Récupère les informations de l'utilisateur
   */
  getUser() {
    return this.user;
  }

  /**
   * Configure les headers d'authentification pour axios
   */
  getAuthHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  /**
   * Connexion d'un utilisateur
   */
  async login(username, password) {
    try {
      const response = await fetch(`${this.apiUrl}/v2/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur de connexion');
      }

      const data = await response.json();
      
      // Sauvegarde du token et des informations utilisateur
      this.token = data.access_token;
      localStorage.setItem('heptuple_token', this.token);
      
      // Récupération des informations utilisateur
      const userResponse = await fetch(`${this.apiUrl}/v2/auth/me`, {
        headers: this.getAuthHeaders()
      });
      
      if (userResponse.ok) {
        this.user = await userResponse.json();
        localStorage.setItem('heptuple_user', JSON.stringify(this.user));
      }

      return { success: true, user: this.user };
    } catch (error) {
      console.error('Erreur de connexion:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Inscription d'un nouvel utilisateur
   */
  async register(userData) {
    try {
      const response = await fetch(`${this.apiUrl}/v2/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur d\'inscription');
      }

      const data = await response.json();
      return { success: true, user: data };
    } catch (error) {
      console.error('Erreur d\'inscription:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Déconnexion de l'utilisateur
   */
  async logout() {
    try {
      if (this.token) {
        await fetch(`${this.apiUrl}/v2/auth/logout`, {
          method: 'POST',
          headers: this.getAuthHeaders()
        });
      }
    } catch (error) {
      console.error('Erreur de déconnexion:', error);
    } finally {
      // Nettoyage local
      this.token = null;
      this.user = null;
      localStorage.removeItem('heptuple_token');
      localStorage.removeItem('heptuple_user');
    }
  }

  /**
   * Vérifie la validité du token
   */
  async validateToken() {
    if (!this.token) return false;

    try {
      const response = await fetch(`${this.apiUrl}/v2/auth/me`, {
        headers: this.getAuthHeaders()
      });

      if (response.ok) {
        this.user = await response.json();
        localStorage.setItem('heptuple_user', JSON.stringify(this.user));
        return true;
      } else {
        // Token invalide, déconnexion
        await this.logout();
        return false;
      }
    } catch (error) {
      console.error('Erreur de validation du token:', error);
      await this.logout();
      return false;
    }
  }

  /**
   * Requête authentifiée
   */
  async authenticatedRequest(url, options = {}) {
    if (!this.isAuthenticated()) {
      throw new Error('Utilisateur non authentifié');
    }

    const defaultOptions = {
      headers: this.getAuthHeaders(),
      ...options
    };

    const response = await fetch(url, defaultOptions);

    if (response.status === 401) {
      // Token expiré, déconnexion
      await this.logout();
      throw new Error('Session expirée');
    }

    return response;
  }
}

// Instance singleton
const authService = new AuthService();
export default authService;
