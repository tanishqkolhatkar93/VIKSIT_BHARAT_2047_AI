import type { Dictionary } from "../utils/i18n";

export function Footer({ t }: { t: Dictionary }) {
  return (
    <footer>
      <strong>{t.tagline}</strong>
      <p>{t.disclaimer}</p>
    </footer>
  );
}

