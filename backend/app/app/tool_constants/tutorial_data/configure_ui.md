# Frontend customization guide
This guide provides instructions on how to customize the user interface elements of your project, such as colors, fonts, and general styling, using Tailwind CSS within your codebase

AgentKit frontend is leveraging [tailwindcss](https://tailwindcss.com/) to efficiently configure and customize theme colors and fonts.

The main UI config files are available in `frontend/tailwind.config.ts` and inside `frontend/src/style/` directory.

## Theme colors
The colour pallete used is defined in the `frontend/tailwind.config.ts` file:

``` typescript
  colors: {
    'bcg-green': '#156648', // replace indigo-600
    'bcg-green-light': '#39b27c',
    'bcg-green-x-light': '#5dfdb0',
    'bcg-x-green': '#00E0B5',
    'custom-light-green': 'rgba(100, 255, 100, 0.1)',
    'bcg-dark': 'rgb(28, 31, 61)',
    'bcg-dark-hover': 'rgb(0, 168, 135)',
    'bcg-dark-select': 'rgb(0, 224, 181)',
    'bcg-light': 'rgb(228,228,233)',
    'bcg-light-select': 'rgb(0, 168, 135)',
    'bcg-light-hover': '#00E0B5',
  },
```

To customize the color of table elements in the chat, you need to modify the `frontend/src/style/global.css` file:

``` css
.rdt_Pagination {
  @apply !border-t-0 dark:bg-bcg-dark-select dark:text-gray-300;
}

.rdt_Pagination button { /* pagination and buttons */
  @apply dark:bg-bcg-dark-select dark:fill-gray-300 dark:text-gray-300;
}

.rdt_Table, /* Color classes */
.rdt_TableHead,
.rdt_TableHeadRow,
.rdt_TableRow { /* Hover and Selected States */
  @apply dark:bg-bcg-dark-select dark:text-gray-300;
}
```

## Fonts

Update the fontFamily section in your `tailwind.config.ts` file:

``` typescript
  fontFamily: {
    sans: ['Henderson BCG Sans', ...defaultTheme.fontFamily.sans],
  },
```

## Logos and images

For logos and images, you will directly replace the files in your `frontend/public/logo_***.png`.Make sure the new images follow the same naming conventions and file formats as the old ones to avoid broken references.


## Renderers

If your application defines tools, it has to define application-specific artifact-renderers and action-renderers as well. The rest of the GUI & application flow is fixed (LLM-streaming, Meta-agent routing, memory, etc.).

- Add your own renderer for steps in `ToolActionRenderer/applications/YOUR_APP` and add your application to `ToolActionRenderer/index.tsx`
- (Optional) Add your own renderer for appendices in `ToolAppendixRenderer/applications/YOUR_APP`

Customize the Actions for your custom tools in the UI: create `ToolActionRenderer/applications/YOUR_APP` and add your application to `ToolActionRenderer/index.tsx`
