import { useState, useRef } from 'react';
import { ocrAPI } from '../services/api';
import Button from '../components/ui/Button';
import HeroIcon from '../components/ui/HeroIcon';

interface OCRLine {
  text: string;
}

export default function OCR() {
  const [image, setImage] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [lines, setLines] = useState<OCRLine[]>([]);
  const [rawText, setRawText] = useState('');
  const [loading, setLoading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFile(f);
    const reader = new FileReader();
    reader.onload = () => setImage(reader.result as string);
    reader.readAsDataURL(f);
  };

  const handleOCR = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const { data } = await ocrAPI.upload(file);
      setRawText(data.raw_text);
      setLines(data.items || []);
    } catch {
      alert('Erro ao processar OCR');
    } finally {
      setLoading(false);
    }
  };

  const handleCamera = () => {
    if (fileRef.current) {
      fileRef.current.accept = 'image/*';
      fileRef.current.capture = 'environment';
      fileRef.current.click();
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center gap-2">
          <HeroIcon name="camera" className="size-6 text-gray-800" />
          <h2 className="text-xl font-bold text-gray-800">Câmera / OCR</h2>
        </div>
        <p className="text-sm text-gray-500">
          Tire uma foto de um comprovante ou nota fiscal para extrair os itens
        </p>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Image preview */}
      {image && (
        <div className="bg-white rounded-xl shadow-sm p-2">
          <img src={image} alt="Preview" className="w-full rounded-lg max-h-80 object-contain" />
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          variant="secondary"
          onClick={() => fileRef.current?.click()}
        >
          <span className="flex items-center gap-1.5">
            <HeroIcon name="folder" className="size-4" />
            Galeria
          </span>
        </Button>
        <Button
          variant="secondary"
          onClick={handleCamera}
        >
          <span className="flex items-center gap-1.5">
            <HeroIcon name="camera" className="size-4" />
            Câmera
          </span>
        </Button>
        {file && (
          <Button onClick={handleOCR} isLoading={loading}>
            <span className="flex items-center gap-1.5">
              <HeroIcon name="magnifying-glass" className="size-4" />
              Extrair Texto
            </span>
          </Button>
        )}
      </div>

      {/* Results */}
      {rawText && (
        <div className="bg-white rounded-xl shadow-sm p-4 space-y-3">
          <h3 className="font-semibold text-gray-800">Texto Extraído</h3>
          <pre className="text-sm text-gray-600 whitespace-pre-wrap bg-gray-50 p-3 rounded">
            {rawText}
          </pre>

          {lines.length > 0 && (
            <>
              <h3 className="font-semibold text-gray-800">Linhas Detectadas</h3>
              <div className="space-y-1">
                {lines.map((line, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="text-gray-500">#{i + 1}</span>
                    <span>{line.text}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
