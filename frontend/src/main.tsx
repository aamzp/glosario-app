import * as React from 'react'
import * as ReactDOM from 'react-dom/client'
import App from './App'
import { ChakraProvider, ColorModeScript, extendTheme } from '@chakra-ui/react'


const config = {
  initialColorMode: 'system',
  useSystemColorMode: true,
}

const theme = extendTheme({ config })

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <App />
    </ChakraProvider>
  </React.StrictMode>
)