import { type NextFetchEvent, NextResponse } from "next/server"
import { getToken } from "next-auth/jwt"
import { type NextRequestWithAuth, withAuth } from "next-auth/middleware"
import { env } from "~/env.mjs"

export default async function middleware(req: NextRequestWithAuth, event: NextFetchEvent) {
  if (!env.NEXT_PUBLIC_USE_AUTH) {
    return NextResponse.next()
  }

  const token = await getToken({ req })
  const isAuthenticated = !!token

  if (req.nextUrl.pathname.startsWith("/auth/signin") && isAuthenticated) {
    return NextResponse.redirect(new URL("/", req.url))
  }

  if (["/_next", "/logo", "/favicon", "/icons", "/fonts"].some((path) => req.nextUrl.pathname.startsWith(path))) {
    return NextResponse.next()
  }

  const authMiddleware = await withAuth({
    pages: {
      signIn: `/auth/signin`,
    },
  })

  return authMiddleware(req, event)
}
