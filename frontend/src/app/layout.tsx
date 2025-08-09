import type { Metadata } from "next";
import "./globals.css";
import { Header } from '@/components/layout/Header'
import { ThemeProvider } from '@/components/providers/ThemeProvider'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'

export const metadata: Metadata = {
  title: {
    template: '%s | T-Developer',
    default: 'T-Developer | AI로 앱을 만드는 가장 빠른 방법',
  },
  description: '자연어로 웹 애플리케이션을 생성하는 차세대 AI 개발 플랫폼. 9개의 전문 AI 에이전트가 협업하여 완전한 프로덕션 코드를 생성합니다.',
  keywords: ['AI', '웹 개발', '노코드', '자연어 프로그래밍', '자동 코드 생성', 'React', 'Next.js'],
  authors: [{ name: 'T-Developer Team' }],
  creator: 'T-Developer',
  publisher: 'T-Developer',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'ko_KR',
    url: '/',
    title: 'T-Developer | AI로 앱을 만드는 가장 빠른 방법',
    description: '자연어로 웹 애플리케이션을 생성하는 차세대 AI 개발 플랫폼',
    siteName: 'T-Developer',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'T-Developer | AI로 앱을 만드는 가장 빠른 방법',
    description: '자연어로 웹 애플리케이션을 생성하는 차세대 AI 개발 플랫폼',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  verification: {
    // Add your verification tokens here
    // google: 'your-google-verification-token',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="font-sans antialiased">
        <a href="#main-content" className="skip-to-content">
          메인 콘텐츠로 건너뛰기
        </a>
        
        <ErrorBoundary>
          <ThemeProvider>
            <div className="relative min-h-screen flex flex-col">
              <Header />
              <main id="main-content" className="flex-1">
                {children}
              </main>
              {/* Footer can be added here */}
            </div>
          </ThemeProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}