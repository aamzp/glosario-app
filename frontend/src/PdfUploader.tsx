import React, { useState } from 'react';
import axios from 'axios';

interface Resultado {
  oracion: string;
  score: number;
  pagina: number;
  liked?: boolean;
}

const PDFUploader: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [resultados, setResultados] = useState<Resultado[]>([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:8000/subir_y_clasificar", formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const dataConLikes = response.data.map((item: Resultado) => ({
        ...item,
        liked: false
      }));
      setResultados(dataConLikes);
    } catch (error) {
      console.error("Error al subir PDF:", error);
    }
    setLoading(false);
  };

  const toggleLike = (index: number) => {
    const nuevosResultados = [...resultados];
    nuevosResultados[index].liked = !nuevosResultados[index].liked;
    setResultados(nuevosResultados);
  };

  return (
    <div className="max-w-3xl mx-auto p-4">
      <div className="flex items-center gap-4 mb-4">
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          {loading ? "Procesando..." : "Subir PDF"}
        </button>
      </div>

      <div className="grid gap-4">
        {resultados.map((item, index) => (
          <div key={index} className="border rounded-xl p-4 shadow hover:shadow-lg transition">
            <p className="text-lg italic mb-2">“{item.oracion}”</p>
            <div className="text-sm text-gray-600 mb-2">📄 Página {item.pagina} | 🔍 Score: {item.score}</div>
            <button
              onClick={() => toggleLike(index)}
              className={`px-3 py-1 rounded-full ${
                item.liked ? "bg-pink-600 text-white" : "bg-gray-200 text-gray-800"
              }`}
            >
              {item.liked ? "💙 Me gusta" : "🤍 Like"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PDFUploader;
