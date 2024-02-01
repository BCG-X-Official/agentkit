import { isEqual } from "lodash-es"
import { useEffect, useMemo, useRef } from "react"

type UseEffectParams = Parameters<typeof useEffect>
type EffectCallback = UseEffectParams[0]
type DependencyList = UseEffectParams[1]
type UseEffectReturn = ReturnType<typeof useEffect>

export function useDeepCompareMemoize<T>(value: T) {
  const ref = useRef<T>(value)
  const signalRef = useRef<number>(0)

  if (!isEqual(value, ref.current)) {
    ref.current = value
    signalRef.current += 1
  }

  return useMemo(() => ref.current, [signalRef.current])
}

export const useDeepCompareEffect = (callback: EffectCallback, dependencies: DependencyList): UseEffectReturn =>
  useEffect(callback, useDeepCompareMemoize(dependencies))
