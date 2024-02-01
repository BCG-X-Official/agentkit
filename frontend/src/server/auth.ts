import { PrismaAdapter } from "@next-auth/prisma-adapter"
import { type GetServerSidePropsContext } from "next"
import { type DefaultSession, getServerSession, type NextAuthOptions, type Session } from "next-auth"
import Credentials from "next-auth/providers/credentials"
import { OpenAPI } from "~/api-client"
import { env } from "~/env.mjs"
import GitHubProviderEnterprise from "./githubEnterprise"
import prisma from "../../prismalib/prismadb"

/**
 * Module augmentation for `next-auth` types. Allows us to add custom properties to the `session`
 * object and keep type safety.
 *
 * @see https://next-auth.js.org/getting-started/typescript#module-augmentation
 */
declare module "next-auth" {
  interface Session extends DefaultSession {
    user: {
      id: string
      name: string | null
      // ...other properties
      // role: UserRole;
    } & DefaultSession["user"]
  }

  // interface User {
  //   // ...other properties
  //   // role: UserRole;
  // }
}

interface ExtendedSession extends Session {
  accessToken: string
}

/**
 * Options for NextAuth.js used to configure adapters, providers, callbacks, etc.
 *
 * @see https://next-auth.js.org/configuration/options
 */
export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GitHubProviderEnterprise({
      clientId: env.GITHUB_ID,
      clientSecret: env.GITHUB_SECRET,
    }),
    Credentials({
      credentials: {
        username: { label: "Username", type: "text", placeholder: "" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        // WARNING: Replace this with SSO or other auth method in production
        const userList: Record<"username" | "password", string>[] = [
          { username: "admin", password: "admin" },
          { username: "user", password: "user" },
          { username: "cypress", password: "cypress" },
        ]
        const authUser = userList.find(
          (user) =>
            user.username.toLocaleLowerCase() == credentials?.username.toLocaleLowerCase() &&
            user.password == credentials?.password
        )
        if (!credentials || !authUser) {
          return null
        }
        console.log(`User authenticated: ${credentials.username}`)
        return {
          id: credentials.username,
          name: credentials.username,
          email: credentials.username,
          image: null,
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, account }) {
      // Encode the bearer token for API calls via openapi-typegen (FastAPI, https://github.com/ferdikoomen/openapi-typescript-codegen/wiki/Authorization)
      if (account) {
        token.accessToken = account.access_token
        OpenAPI.TOKEN = account.access_token as string
      }
      return token
    },
    async session({ session, token }) {
      ;(session as ExtendedSession).accessToken = `Bearer ${token.accessToken}`
      return session
    },
  },
  session: {
    strategy: "jwt",
  },
  secret: env.NEXTAUTH_SECRET,
  pages: {
    signIn: "/auth/signin",
  },
}

/**
 * Wrapper for `getServerSession` so that you don't need to import the `authOptions` in every file.
 *
 * @see https://next-auth.js.org/configuration/nextjs
 */
export const getServerAuthSession = (ctx: {
  req: GetServerSidePropsContext["req"]
  res: GetServerSidePropsContext["res"]
}) => {
  return getServerSession(ctx.req, ctx.res, authOptions)
}
