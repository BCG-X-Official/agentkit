import type { NextApiRequest, NextApiResponse } from "next"
import client from "prom-client"

const register = new client.Registry()
client.collectDefaultMetrics({ register })

export default function handler(_: NextApiRequest, res: NextApiResponse) {
  res.setHeader("Content-Type", register.contentType)
  register.metrics().then((metrics) => res.send(metrics))
}
