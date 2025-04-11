import { useState } from "react"
import { GlosarioCard } from "./components/GlosarioCard"
import { Box, SimpleGrid, Input, Heading, Button } from "@chakra-ui/react"
import axios from "axios"

interface Resultado {
  id: string
  sentence: string
  page: number
  score: number
  liked?: boolean
}

function App() {
  const [filtro, setFiltro] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [sentences, setSentences] = useState<Resultado[]>([])
  const [loading, setLoading] = useState(false)

  const handleUpload = async () => {
    if (!file) return
    const formData = new FormData()
    formData.append("file", file)
    setLoading(true)
    try {
      const response = await axios.post("http://localhost:8000/subir_y_clasificar", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })

      const dataConLikes = response.data.map((item: any, i: number) => ({
        id: `${i}`,
        sentence: item.oracion,
        page: item.pagina,     
        score: item.score,
        liked: false,
      }))

      setSentences(dataConLikes)
    } catch (err) {
      console.error("Error al subir el PDF", err)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-background text-foreground dark:bg-zinc-950 dark:text-white px-4 py-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">🧠 Glosario Inteligente</h1>

      <div className="flex items-center gap-4 mb-6">
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="text-sm"
        />
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {loading ? "Procesando..." : "Subir PDF"}
        </button>
      </div>

      <input
        type="text"
        value={filtro}
        onChange={(e) => setFiltro(e.target.value)}
        placeholder="🔎 Buscar por concepto..."
        className="mb-4 p-2 w-full max-w-xl border border-gray-300 rounded-lg dark:bg-zinc-800 dark:text-white"
      />

      <SimpleGrid columns={{ base: 1, sm: 2, lg: 3 }} spacing={6}>
        {sentences
          .filter((s) => s.sentence.toLowerCase().includes(filtro.toLowerCase()))
          .map((s) => (
            <GlosarioCard
              key={s.id}
              id={s.id}
              sentence={s.sentence}
              page={s.page}
              score={s.score}
            />
        ))}
      </SimpleGrid>

    </div>
  )
}

export default App
