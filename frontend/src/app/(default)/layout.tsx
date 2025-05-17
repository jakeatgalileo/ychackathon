import { redirect } from 'next/navigation'

export default async function DefaultLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div>
      {children}
    </div>
  )
}