# Image Generation tool

## How it works
The image generation tool generates an image based on the user prompt and shows it in an appendix in the chat. The image generation service can be defined in `generate_image`, currently the OpenAI Dall-E API is used but this can be replaced by any other service.

To manipulate the exact prompt for the image generation, you can manipulate the query object, for example if you only want the last message to be used (see [memory documentation](docs/advanced/memory.md) for more details):
```
tool_input = ToolInputSchema.parse_raw(query)
image_prompt = tool_input.latest_human_message
```
Alternatively, another option is to manipulate the user prompt to be more descriptive using a LLM call.

<img src="/docs/img/img_gen_tool_elephant.png" alt="Elephant" width="400"/>


## Layout

You can change the layout of the generated image in `ResultsView.tsx`:
```
case SUPPORTED_SYNTAX_LANGUAGES.IMAGEURL:
    return <Image src={code} width={300} height={200} alt="img" />
```

## Security

For security reasons, nextjs requires allowed remote domains to be specified. To add a new remote service to generate images, add the domain in `next.config.mjs`:
```
images: {
    domains: ['github.com', '127.0.0.1', 'localhost', 'oaidalleapiprodscus.blob.core.windows.net', 'YOUR_DOMAIN'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'oaidalleapiprodscus.blob.core.windows.net',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'YOURDOMAIN',
        port: '',
        pathname: '/**',
      },
    ],
  },
```
