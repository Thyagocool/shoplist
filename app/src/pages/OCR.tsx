import { useState, useRef, useCallback } from 'react';
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
  const [showCamera, setShowCamera] = useState(false);
  const galleryRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const handleFileChange = (f: File | null) => {
    if (!f) return;
    setFile(f);
    const reader = new FileReader();
    reader.onload = () => setImage(reader.result as string);
    reader.readAsDataURL(f);
  };

  const openCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
        audio: false,
      });
      streamRef.current = stream;
      setShowCamera(true);
      // Aguarda o DOM renderizar o <video> antes de atribuir a stream
      requestAnimationFrame(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }
      });
    } catch {
      alert('Não foi possível acessar a câmera. Verifique as permissões.');
    }
  }, []);

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      if (!blob) return;
      const f = new File([blob], 'foto.jpg', { type: 'image/jpeg' });
      handleFileChange(f);
      closeCamera();
    }, 'image/jpeg', 0.9);
  };

  const closeCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setShowCamera(false);
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

      {/* Hidden file input — apenas para galeria */}
      <input
        ref={galleryRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
      />

      {/* Preview da imagem capturada */}
      {image && !showCamera && (
        <div className="bg-white rounded-xl shadow-sm p-2">
          <img src={image} alt="Preview" className="w-full rounded-lg max-h-80 object-contain" />
        </div>
      )}

      {/* Câmera ao vivo */}
      {showCamera && (
        <div className="bg-black rounded-xl overflow-hidden relative">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full max-h-[70vh] object-contain"
          />
          <canvas ref={canvasRef} className="hidden" />

          {/* Controles da câmera */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4 flex items-center justify-center gap-6">
            <button
              onClick={closeCamera}
              className="bg-white/20 text-white rounded-full p-3 hover:bg-white/30 transition"
              title="Cancelar"
            >
              <HeroIcon name="x-mark" className="size-6" />
            </button>
            <button
              onClick={capturePhoto}
              className="bg-white rounded-full p-4 shadow-lg hover:bg-gray-100 active:bg-gray-200 transition"
              title="Tirar foto"
            >
              <div className="w-8 h-8 rounded-full border-4 border-gray-800" />
            </button>
            {/* Spacer pra centralizar o botão */}
            <div className="w-12" />
          </div>
        </div>
      )}

      {/* Actions */}
      {!showCamera && (
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={() => galleryRef.current?.click()}
          >
            <span className="flex items-center gap-1.5">
              <HeroIcon name="folder" className="size-4" />
              Galeria
            </span>
          </Button>
          <Button
            variant="secondary"
            onClick={openCamera}
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
      )}

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
