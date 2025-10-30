import Cookies from 'js-cookie';

const TOKEN_COOKIE_NAME = 'auth_token';
const SESSION_TOKEN_COOKIE_NAME = 'session_token';
const COOKIE_EXPIRY_DAYS = 30; // 30 дней

export const cookieUtils = {
  // Сохранение токена пользователя
  setUserToken: (token: string) => {
    Cookies.set(TOKEN_COOKIE_NAME, token, { 
      expires: COOKIE_EXPIRY_DAYS,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax'
    });
  },

  // Получение токена пользователя
  getUserToken: (): string | null => {
    return Cookies.get(TOKEN_COOKIE_NAME) || null;
  },

  // Сохранение токена сессии
  setSessionToken: (token: string) => {
    Cookies.set(SESSION_TOKEN_COOKIE_NAME, token, { 
      expires: COOKIE_EXPIRY_DAYS,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax'
    });
  },

  // Получение токена сессии
  getSessionToken: (): string | null => {
    return Cookies.get(SESSION_TOKEN_COOKIE_NAME) || null;
  },

  // Получение текущего токена (приоритет: сессия > пользователь)
  getCurrentToken: (): string | null => {
    return Cookies.get(SESSION_TOKEN_COOKIE_NAME) || Cookies.get(TOKEN_COOKIE_NAME) || null;
  },

  // Очистка всех токенов
  clearTokens: () => {
    Cookies.remove(TOKEN_COOKIE_NAME);
    Cookies.remove(SESSION_TOKEN_COOKIE_NAME);
  },

  // Очистка только токена пользователя
  clearUserToken: () => {
    Cookies.remove(TOKEN_COOKIE_NAME);
  },

  // Очистка только токена сессии
  clearSessionToken: () => {
    Cookies.remove(SESSION_TOKEN_COOKIE_NAME);
  }
};
