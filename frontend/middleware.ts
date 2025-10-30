import { NextRequest, NextResponse } from 'next/server';
import { cookieUtils } from './lib/cookies';

export function middleware(request: NextRequest) {
  // Проверяем, есть ли токен в cookies
  const token = cookieUtils.getCurrentToken();
  
  // Если пользователь пытается зайти на защищенные страницы без токена
  if (request.nextUrl.pathname.startsWith('/chat') && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  // Если пользователь уже аутентифицирован и пытается зайти на страницы входа/регистрации
  if ((request.nextUrl.pathname.startsWith('/login') || request.nextUrl.pathname.startsWith('/register')) && token) {
    return NextResponse.redirect(new URL('/chat', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
