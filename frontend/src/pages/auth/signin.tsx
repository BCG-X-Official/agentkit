import Image from "next/image"
import { getServerSession } from "next-auth/next"
import { getCsrfToken, getProviders, signIn, useSession } from "next-auth/react"
import { useEffect, useState } from "react"

import Icon from "~/components/CustomIcons/Icon"

import { authOptions } from "~/server/auth"
import { Theme } from "~/styles/themes"
import { APPLICATION_TITLE, getMainLogoSrc } from "~/utils"
import { AUTH_SELECTORS } from "~/utils/signin.selectors"
import type { GetServerSidePropsContext, InferGetServerSidePropsType } from "next"

export default function SignIn({ providers }: InferGetServerSidePropsType<typeof getServerSideProps>) {
  const [mounted, setMounted] = useState(false)

  const fixedInputClass =
    "rounded-md appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 focus:z-10 sm:text-sm"

  const providerList = Object.values(providers).filter((provider) => provider.id !== "credentials")
  const credentialsProvider = Object.values(providers).find((provider) => provider.id === "credentials")

  const session = useSession()
  const [csrfToken, setCsrfToken] = useState("")

  useEffect(() => {
    // https://github.com/nextauthjs/next-auth/issues/2426#issuecomment-1141406105
    async function fetchCsrfToken() {
      const result = await getCsrfToken()
      if (!result) {
        throw new Error("Can not sign in without a CSRF token")
      }
      setCsrfToken(result)
    }

    /*
      Wait until session is fetched before obtaining csrfToken
      to prevent synchronization issues caused by both
      /api/auth/session and /api/auth/csrf setting the cookie.
      Only happens in dev environment.
    */
    if (session.status !== "loading") {
      fetchCsrfToken()
    }
  }, [session.status])

  // useEffect only runs on the client, so now we can safely show the UI
  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-2">
      {mounted ? (
        <div className="flex flex-row items-center justify-center py-2">
          <Image src={getMainLogoSrc(Theme.Light)} alt={APPLICATION_TITLE} width={400} height={400} priority />
        </div>
      ) : null}
      <h1 className="mt-2 text-4xl font-bold text-gray-800">Welcome back</h1>
      <div className="flex min-w-full flex-col items-center justify-center py-2">
        <div className="mb-4 min-w-64 rounded-xl p-4 text-center text-gray-100">
          {credentialsProvider && (
            <div className="flex w-64 flex-col rounded-xl text-center text-gray-700">
              <form method="post" action="/api/auth/callback/credentials">
                <input name="csrfToken" type="hidden" defaultValue={csrfToken} />
                <div className="my-2">
                  <label htmlFor={"email_login"} className="sr-only">
                    {"Email"}
                  </label>
                  <input
                    id={"email_login"}
                    name={"username"}
                    type={"username"}
                    required={true}
                    className={fixedInputClass}
                    placeholder={"Email"}
                    data-cy={AUTH_SELECTORS.emailInput}
                    autoComplete="username"
                  />
                </div>
                <div className="my-2">
                  <label htmlFor={"password_login"} className="sr-only">
                    {"Password"}
                  </label>
                  <input
                    id={"password_login"}
                    name={"password"}
                    type={"password"}
                    required={true}
                    className={fixedInputClass}
                    placeholder={"Password"}
                    data-cy={AUTH_SELECTORS.passwordInput}
                    autoComplete="current-password"
                  />
                </div>
                <button
                  type="submit"
                  className="flex w-full flex-row items-center justify-center rounded-xl bg-gray-900 p-4 text-center text-gray-100"
                  data-cy={AUTH_SELECTORS.signinButton}
                >
                  <Icon.FaSignInAlt className="mr-2" />
                  Sign in with Email
                </button>
              </form>
            </div>
          )}
          {providerList.length > 0 && (
            <div className="flex flex-row items-center justify-center py-2">
              <div className="grow border-t-2 border-gray-300"></div>
              <div className="px-2 text-gray-400">or</div>
              <div className="grow border-t-2 border-gray-300"></div>
            </div>
          )}
          {providerList.map((provider) => (
            <div
              key={provider.name}
              className="mb-4 flex flex-row rounded-xl bg-gray-900 p-4 text-center text-gray-100"
            >
              <Image
                src={`/icons/${provider.name.toLowerCase()}.png`}
                alt={provider.name}
                width={30}
                height={30}
                className="mx-2"
              />
              <button onClick={() => signIn(provider.id)}>Sign in with {provider.name}</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const session = await getServerSession(context.req, context.res, authOptions)

  // If the user is already logged in, redirect.
  if (session) {
    return { redirect: { destination: "/" } }
  }

  const providers = await getProviders()

  return {
    props: {
      providers: providers ?? [],
    },
  }
}
