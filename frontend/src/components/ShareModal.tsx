import { Download, Link2, Share2, X } from "lucide-react";
import { useEffect, useState } from "react";
import type { Dictionary } from "../utils/i18n";

export type ShareMode = "share" | "challenge";

type Props = {
  name: string;
  quote: string;
  shareUrl: string;
  imageUrl: string;
  pngBlob: Blob | null;
  mode: ShareMode;
  caption: string;
  t: Dictionary;
  onClose: () => void;
};

export function ShareModal({
  name,
  quote,
  shareUrl,
  imageUrl,
  pngBlob,
  mode,
  caption: initialCaption,
  t,
  onClose,
}: Props) {
  const [caption, setCaption] = useState(initialCaption);
  const [copied, setCopied] = useState<"link" | "caption" | null>(null);

  useEffect(() => {
    setCaption(initialCaption);
  }, [initialCaption]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const shareText = `${caption}\n\n${shareUrl}`;

  function openShareUrl(url: string) {
    window.open(url, "_blank", "noopener,noreferrer");
  }

  async function copy(value: "link" | "caption") {
    const text = value === "link" ? shareUrl : caption;
    await navigator.clipboard.writeText(text);
    setCopied(value);
    window.setTimeout(() => setCopied(null), 1600);
  }

  async function webShare() {
    if (!navigator.share) return;
    const data: ShareData = { title: `${name}'s Vision for India 2047`, text: caption, url: shareUrl };
    if (pngBlob && navigator.canShare?.({ files: [new File([pngBlob], "vision-card.png", { type: "image/png" })] })) {
      data.files = [new File([pngBlob], "vision-card.png", { type: "image/png" })];
    }
    await navigator.share(data);
  }

  async function downloadPng() {
    if (!pngBlob) return;
    const link = document.createElement("a");
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "my";
    link.download = `${slug}-india-2047-vision.png`;
    link.href = URL.createObjectURL(pngBlob);
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(link.href), 4000);
  }

  return (
    <div className="share-overlay" role="dialog" aria-modal="true" aria-labelledby="share-modal-title">
      <div className="share-modal">
        <header className="share-modal-head">
          <h3 id="share-modal-title">{mode === "share" ? t.shareMyVision : t.challengeYourFriends}</h3>
          <button type="button" className="share-close" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </header>

        <div className="share-modal-body">
          <img className="share-thumb" src={imageUrl} alt={`${name}'s Vision for India 2047`} />

          <label className="share-caption-label">
            {t.captionLabel}
            <textarea className="share-caption" value={caption} onChange={(event) => setCaption(event.target.value)} rows={5} />
          </label>

          <div className="share-grid">
            <button type="button" className="share-btn" onClick={() => openShareUrl(`https://wa.me/?text=${encodeURIComponent(shareText)}`)}>
              <span className="share-emoji">💬</span> {t.whatsapp}
            </button>
            <button type="button" className="share-btn" onClick={() => openShareUrl(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`)}>
              <span className="share-emoji">📘</span> {t.facebook}
            </button>
            <button type="button" className="share-btn" onClick={() => openShareUrl(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`)}>
              <span className="share-emoji">💼</span> {t.linkedin}
            </button>
            <button type="button" className="share-btn" onClick={() => openShareUrl(`https://twitter.com/intent/tweet?text=${encodeURIComponent(caption)}&url=${encodeURIComponent(shareUrl)}`)}>
              <span className="share-emoji">🐦</span> {t.xTwitter}
            </button>
            <button type="button" className="share-btn" onClick={() => copy("caption")}>
              <Download size={16} /> {t.instagram}
            </button>
            <button type="button" className="share-btn" onClick={() => copy("link")}>
              <Link2 size={16} /> {copied === "link" ? t.copied : t.copyLink}
            </button>
            {navigator.share ? (
              <button type="button" className="share-btn share-btn-primary" onClick={webShare}>
                <Share2 size={16} /> {t.webShare}
              </button>
            ) : null}
          </div>

          <p className="share-hint">
            {mode === "challenge" ? t.challengeHint : t.instagramHint}
          </p>
          <div className="share-instagram">
            <button type="button" className="button secondary" onClick={downloadPng}>
              <Download size={18} /> {t.downloadCard}
            </button>
            <button type="button" className="button secondary" onClick={() => copy("caption")}>
              {copied === "caption" ? t.copied : t.copyCaption}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
