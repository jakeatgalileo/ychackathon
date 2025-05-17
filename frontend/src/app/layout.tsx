import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'MLE Agent',
  description: 'mle-agent',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`dark ${inter.className}`}>
      <body className="bg-background text-foreground">
        <div className="flex min-h-screen flex-col">
          {children}
        </div>
      </body>
    </html>
  )
}