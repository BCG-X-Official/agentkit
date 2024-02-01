declare module "can-ndjson-stream" {
  export default function ndjsonStream(data: unknown): {
    getReader: () => {
      read: () => Promise<{
        done: boolean
        value: any
      }>
    }
    cancel: () => void
  }
}
